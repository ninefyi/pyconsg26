# Azure MongoDB Replica Set Demo: Pulumi & PyInfra

This proof-of-concept directory contains code to provision 3 Azure VM instances and configure them as a 3-node MongoDB Replica Set cluster.

---

## 📋 Prerequisites

Ensure you have the following installed on your machine:
- [Python 3.9+](https://www.python.org/)
- [Pulumi CLI](https://www.pulumi.com/docs/install/)
- Azure CLI logged in (`az login`)
- SSH keypair generated at `~/.ssh/id_rsa` & `~/.ssh/id_rsa.pub`

---

## 🚀 Step-by-Step Execution Guide

⚠️ Cost reminder: this demo provisions billable Azure resources. Always run cleanup when done.

### Non-Interactive Mode (CI/Automation)

Use non-interactive flags to avoid confirmation prompts:

```bash
# Pulumi apply/destroy (auto-approve)
pulumi up --yes --non-interactive
pulumi destroy --yes --non-interactive

# PyInfra apply (auto-approve)
pyinfra inventory.py deploy.py --yes
```

For headless Azure authentication in CI, prefer a service principal instead of interactive `az login`:

```bash
az login --service-principal \
   --username "$AZURE_CLIENT_ID" \
   --password "$AZURE_CLIENT_SECRET" \
   --tenant "$AZURE_TENANT_ID"
```

### Step 1: Provision Infrastructure with Pulumi
1. Navigate to the Pulumi project:
   ```bash
   cd pulumi
   ```
2. Initialize virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Sign in to Azure CLI and select the target subscription:
   ```bash
   # Interactive browser/device login
   az login

   # Verify account and tenant currently in use
   az account show --output table

   # If you have multiple subscriptions, pick the one to deploy into
   az account list --output table
   az account set --subscription "<SUBSCRIPTION_ID_OR_NAME>"

   # Final verification
   az account show --output table
   ```
   Tips:
   - If your org requires a specific tenant, use `az login --tenant <TENANT_ID>`.
   - If your account has no subscription selected, Pulumi Azure provider operations will fail.

4. Set up Pulumi environment/login before initializing the stack:
   ```bash
   # Check Pulumi CLI installation
   pulumi version

   # Login to Pulumi backend (choose one)
   pulumi login                          # Pulumi Cloud backend
   # pulumi login --local                # Local file backend (alternative)

   # Confirm active backend/user
   pulumi whoami

   # Recommended: set secrets passphrase for this shell session
   export PULUMI_CONFIG_PASSPHRASE="<your-passphrase>"
   # For demo-only local use without passphrase:
   # export PULUMI_CONFIG_PASSPHRASE=""
   ```

5. Initialize the Pulumi stack (e.g. `dev`):
   ```bash
   pulumi stack init dev
   ```
6. Configure required stack configuration (e.g., Azure location and public SSH key path or SSH password):
   ```bash
   pulumi config set azure-native:location eastus
   pulumi config set sshSourceCIDR "$(curl ifconfig.me -4)/32"
   
   # For SSH Private Key authentication (default):
   pulumi config set sshPublicKey "$(cat ~/.ssh/id_rsa.pub)"
   
   # For SSH Username/Password authentication (optional):
   pulumi config set --secret sshPassword "SecurePassword123!"
   ```
   For demo-only open SSH access (not recommended), explicitly opt in:
   ```bash
   export ALLOW_OPEN_SSH=1
   ```

   If your stack uses passphrase-based secrets encryption, export it before Pulumi commands:
   ```bash
   export PULUMI_CONFIG_PASSPHRASE=""
   ```
7. Deploy the resources:
   ```bash
   pulumi up --yes --non-interactive
   ```
   *Note: This will create the Resource Group, Virtual Network, Subnet, Network Security Group, Public IPs, Network Interfaces, and 3 Virtual Machines.*

---

### Step 2: Configure MongoDB with PyInfra
1. Navigate to the PyInfra project (in a new terminal tab or after returning to the parent directory):
   ```bash
   cd ../pyinfra
   ```
2. Initialize virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the configuration playbook:
   ```bash
   pyinfra inventory.py deploy.py --yes
   ```
   *Note: `inventory.py` will dynamically read the output IP addresses from the active Pulumi stack, configure credentials, download MongoDB keys/packages, configure `/etc/mongod.conf` with host VNet IPs, start services, and run `rs.initiate()` on the primary VM.*

   *If Pulumi output lookup fails, `inventory.py` now fails fast by default. For demo-only dry-runs, opt into mock inventory data explicitly:*
   ```bash
   export ALLOW_MOCK_INVENTORY=1
   ```

   *Optional secure-mode toggle (for non-demo usage):*
   ```bash
   export ENABLE_MONGODB_AUTH=1
   export MONGODB_KEYFILE_CONTENT="<shared-random-keyfile-content>"
   ```

---

### Step 3: Verify the Replica Set
1. SSH into the primary VM (using the first public IP output by Pulumi):
   ```bash
   ssh azureuser@<VM-1-PUBLIC-IP>
   ```
2. Open the MongoDB shell:
   ```bash
   mongosh
   ```
3. Check replication status:
   ```javascript
   rs.status()
   ```
   You should see 3 nodes listed, with one `PRIMARY` and two `SECONDARY` nodes.

---

### Step 4: Clean Up Resources
To destroy the virtual machines and avoid recurring Azure costs:
1. Navigate to the Pulumi folder and run:
   ```bash
   cd ../pulumi
   pulumi destroy --yes --non-interactive
   ```
