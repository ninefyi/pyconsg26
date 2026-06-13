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
3. Initialize the Pulumi stack (e.g. `dev`):
   ```bash
   pulumi stack init dev
   ```
4. Configure required stack configuration (e.g., Azure location and public SSH key path or SSH password):
   ```bash
   pulumi config set azure-native:location eastus
   
   # For SSH Private Key authentication (default):
   pulumi config set sshPublicKey "$(cat ~/.ssh/id_rsa.pub)"
   
   # For SSH Username/Password authentication (optional):
   pulumi config set --secret sshPassword "SecurePassword123!"
   ```
5. Deploy the resources:
   ```bash
   pulumi up
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
   pyinfra inventory.py deploy.py
   ```
   *Note: `inventory.py` will dynamically read the output IP addresses from the active Pulumi stack, configure credentials, download MongoDB keys/packages, configure `/etc/mongod.conf` with host VNet IPs, start services, and run `rs.initiate()` on the primary VM.*

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
   pulumi destroy
   ```
