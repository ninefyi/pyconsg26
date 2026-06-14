import json
from io import StringIO
from pyinfra import host
from pyinfra.operations import apt, files, server

# Install system dependencies
apt.packages(
    name="Install dependencies",
    packages=["curl", "gnupg"],
    update=True,
    _sudo=True
)

# Download and add the MongoDB 8.0 signing key
server.shell(
    name="Add MongoDB GPG signing key",
    commands=[
        "curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | "
        "gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg --yes"
    ],
    _sudo=True
)

# Add MongoDB APT repository source
files.put(
    name="Add MongoDB repository list",
    src=StringIO(
        "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] "
        "https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse\n"
    ),
    dest="/etc/apt/sources.list.d/mongodb-org-8.0.list",
    _sudo=True
)

# Install MongoDB Community Edition 8.0.23 (pinning all key packages to avoid dependency shifts)
apt.packages(
    name="Install MongoDB Community Edition 8.0.23 packages",
    packages=[
        "mongodb-org=8.0.23",
        "mongodb-org-server=8.0.23",
        "mongodb-org-database=8.0.23",
        "mongodb-org-mongos=8.0.23",
        "mongodb-org-tools=8.0.23",
        "mongodb-mongosh"
    ],
    update=True,
    _sudo=True
)

if host.data.enable_mongodb_auth:
    # The mongodb uazser/group are created by mongodb-org packages.
    files.put(
        name="Install MongoDB replica keyfile",
        src=StringIO(f"{host.data.mongodb_keyfile_content}\n"),
        dest=host.data.mongodb_keyfile_path,
        user="mongodb",
        group="mongodb",
        mode="400",
        _sudo=True
    )

# Deploy the configuration template
files.template(
    name="Configure MongoDB mongod.conf",
    src="templates/mongod.conf.j2",
    dest="/etc/mongod.conf",
    user="root",
    group="root",
    mode="644",
    _sudo=True
)

# Start and enable the mongod service (restart to apply binding IP changes)
server.service(
    name="Restart and enable MongoDB service",
    service="mongod",
    running=True,
    enabled=True,
    restarted=True,
    _sudo=True
)

# Initialize MongoDB Replica Set on the Primary Node (node_index 0)
# SECURITY NOTE: For production environments, database authorization must be enabled
# (security.authorization: enabled) in mongod.conf, and a shared replica set keyfile
# must be created, secured (chmod 400), and copied to all nodes to authorize inter-node syncing.
if host.data.node_index == 0:
    # Build list of replica set members using private IPs
    members = []
    for idx, private_ip in enumerate(host.data.all_nodes):
        members.append({
            "_id": idx,
            "host": f"{private_ip}:27017"
        })
    
    # Serialize to JSON format for mongosh script execution
    members_json = json.dumps(members).replace('"', "'")

    rs_initiate_cmd = (
        "mongosh --quiet --eval \""
        "try { const st = rs.status(); if (st.ok === 1) { print('Replica set already initialized'); quit(0); } } catch (e) {} "
        f"rs.initiate({{ _id: 'rs0', members: {members_json} }});"
        "\""
    )
    
    # Run the initiation script. It checks if replica set is already initiated to ensure idempotency.
    server.shell(
        name="Initialize replica set on Primary node",
        commands=[
            "for i in $(seq 1 60); do mongosh --quiet --eval \"db.adminCommand({ ping: 1 }).ok\" >/dev/null 2>&1 && break; sleep 2; done",
            "mongosh --quiet --eval \"db.adminCommand({ ping: 1 }).ok\" >/dev/null 2>&1 || (echo 'MongoDB did not become ready in time' && exit 1)",
            rs_initiate_cmd,
            "for i in $(seq 1 90); do mongosh --quiet --eval \"const st = rs.status(); if (st.ok !== 1) quit(1); const primary = st.members.filter(m => m.stateStr === 'PRIMARY').length; const secondaries = st.members.filter(m => m.stateStr === 'SECONDARY').length; if (primary === 1 && secondaries >= 1) { printjson({ ok: st.ok, primary, secondaries }); quit(0); } quit(2);\" && exit 0; sleep 2; done; echo 'Replica set did not reach healthy state in time'; exit 1"
        ],
        _sudo=True
    )
