import json
import os
import subprocess

enable_mongodb_auth = os.environ.get("ENABLE_MONGODB_AUTH", "").lower() in {"1", "true", "yes"}
mongodb_keyfile_content = os.environ.get("MONGODB_KEYFILE_CONTENT")

if enable_mongodb_auth and not mongodb_keyfile_content:
    raise RuntimeError(
        "ENABLE_MONGODB_AUTH is set, but MONGODB_KEYFILE_CONTENT is missing. "
        "Provide a shared keyfile content value for all replica set nodes."
    )

# Retrieve the stack outputs from Pulumi
try:
    env = os.environ.copy()
    # NOTE: Set PULUMI_CONFIG_PASSPHRASE in your environment before running.
    # For local development without encryption, you can use an empty string:
    #   export PULUMI_CONFIG_PASSPHRASE=""
        
    # Resolve pulumi directory relative to this script (works from any cwd)
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _pulumi_dir = os.path.join(_script_dir, "..", "pulumi")

    # Run the pulumi stack output command inside the pulumi demo directory (expose secrets)
    result = subprocess.run(
        ["pulumi", "stack", "output", "--json", "--show-secrets"],
        cwd=_pulumi_dir,
        capture_output=True,
        text=True,
        check=True,
        env=env,
        timeout=30
    )
    outputs = json.loads(result.stdout)
    _public_ips = outputs.get("vm_public_ips", [])
    _private_ips = outputs.get("vm_private_ips", [])
    _ssh_user = outputs.get("ssh_user", "azureuser")

    if not _public_ips or not _private_ips:
        raise RuntimeError("Pulumi outputs are missing vm_public_ips or vm_private_ips.")
    if len(_public_ips) != len(_private_ips):
        raise RuntimeError("Pulumi outputs must contain equal numbers of public and private IPs.")
    
    # Extract ssh_password which may be encrypted/nested in Pulumi outputs
    _ssh_password = None
    if "ssh_password" in outputs:
        val = outputs["ssh_password"]
        if isinstance(val, dict):
            _ssh_password = val.get("value")
          
            # Handle standard redaction string just in case
            if _ssh_password == "[secret]":
                _ssh_password = None
        else:
            _ssh_password = val
except Exception as error:
    allow_mock_inventory = os.environ.get("ALLOW_MOCK_INVENTORY", "").lower() in {"1", "true", "yes"}
    if allow_mock_inventory:
        # Mock data is allowed only when explicitly requested for local dry-runs.
        _public_ips = ["20.185.196.10", "20.185.196.11", "20.185.196.12"]
        _private_ips = ["10.0.1.4", "10.0.1.5", "10.0.1.6"]
        _ssh_user = "azureuser"
        _ssh_password = None
    else:
        raise RuntimeError(
            "Failed to retrieve Pulumi stack outputs for inventory. "
            "Deploy or select a Pulumi stack first (cd ../pulumi && pulumi up), "
            "or set ALLOW_MOCK_INVENTORY=1 for demo-only mock inventory usage. "
            f"Original error: {error}"
        ) from error

# construct the PyInfra inventory groups
# PyInfra will look for defined lists/tuples of hosts.
# We define 'mongodb_servers' which assigns host-specific data (SSH details, private IPs, indices).
mongodb_servers = []
for i, public_ip in enumerate(_public_ips):
    host_data = {
        "ssh_user": _ssh_user,
        "ssh_strict_host_key_checking": "no",
        "private_ip": _private_ips[i],
        "node_name": f"mongo-node-{i+1}",
        "node_index": i,
        "all_nodes": _private_ips,
        "enable_mongodb_auth": enable_mongodb_auth,
        "mongodb_keyfile_path": "/etc/mongod.keyfile"
    }

    if enable_mongodb_auth:
        host_data["mongodb_keyfile_content"] = mongodb_keyfile_content
    
    # Add authentication credentials (SSH Key vs Username/Password)
    if _ssh_password:
        host_data["ssh_password"] = _ssh_password
    else:
        host_data["ssh_key"] = "~/.ssh/id_rsa"
        
    mongodb_servers.append((public_ip, host_data))

