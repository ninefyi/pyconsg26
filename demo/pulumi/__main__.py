import pulumi
from pulumi_azure_native import resources, network, compute

import os

# Load configuration
config = pulumi.Config()
ssh_public_key = config.get("sshPublicKey")
ssh_password = config.get_secret("sshPassword")
has_password = config.get("sshPassword") is not None
ssh_source_cidr = config.get("sshSourceCIDR")
allow_open_ssh = os.environ.get("ALLOW_OPEN_SSH", "").lower() in {"1", "true", "yes"}
RESOURCE_NAME_PREFIX = "pyconsg-mdb"

if not ssh_source_cidr:
    if allow_open_ssh:
        ssh_source_cidr = "*"
    else:
        raise ValueError(
            "Configuration Error: You must set 'sshSourceCIDR' (for example, '203.0.113.10/32'). "
            "For demo-only open SSH access, set ALLOW_OPEN_SSH=1 before running Pulumi."
        )

# Security Best Practice: Eliminate hardcoded fallback keys.
# Attempt to read the user's default public key if no key is configured in Pulumi.
if not ssh_public_key and not has_password:
    default_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
    if os.path.exists(default_key_path):
        with open(default_key_path, "r") as key_file:
            ssh_public_key = key_file.read().strip()
        if not ssh_public_key.startswith(("ssh-rsa ", "ssh-ed25519 ", "ecdsa-sha2-")):
            raise ValueError(
                f"Configuration Error: Invalid SSH public key format in {default_key_path}."
            )
    else:
        raise ValueError(
            "Configuration Error: You must set either 'sshPublicKey' or "
            "'sshPassword' configuration to allow secure VM login authentication. "
            "Please run: 'pulumi config set sshPublicKey \"$(cat ~/.ssh/id_rsa.pub)\"' "
            "or 'pulumi config set --secret sshPassword \"<Password>\"'."
        )

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(f"{RESOURCE_NAME_PREFIX}-rg",
    resource_group_name=f"rg-{RESOURCE_NAME_PREFIX}"
)

# Create a Virtual Network (VNet)
vnet = network.VirtualNetwork(f"{RESOURCE_NAME_PREFIX}-vnet",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    )
)

# Create a Network Security Group (NSG) for the firewall
nsg = network.NetworkSecurityGroup(f"{RESOURCE_NAME_PREFIX}-nsg",
    resource_group_name=resource_group.name
)

# Rule to allow SSH traffic (port 22)
# SECURITY NOTE: In a production environment, source_address_prefix should be restricted 
# strictly to specific administrative public IPs (e.g. your office/VPN gateway IP) instead of "*".
ssh_rule = network.SecurityRule(f"{RESOURCE_NAME_PREFIX}-allow-ssh",
    resource_group_name=resource_group.name,
    network_security_group_name=nsg.name,
    security_rule_name=f"{RESOURCE_NAME_PREFIX}-allow-ssh",
    protocol=network.SecurityRuleProtocol.TCP,
    source_port_range="*",
    destination_port_range="22",
    source_address_prefix=ssh_source_cidr,
    destination_address_prefix="*",
    access=network.SecurityRuleAccess.ALLOW,
    priority=1000,
    direction=network.SecurityRuleDirection.INBOUND,
)

# Rule to allow MongoDB traffic (port 27017) inside VNet
mongodb_rule = network.SecurityRule(f"{RESOURCE_NAME_PREFIX}-allow-mongodb",
    resource_group_name=resource_group.name,
    network_security_group_name=nsg.name,
    security_rule_name=f"{RESOURCE_NAME_PREFIX}-allow-mongodb",
    protocol=network.SecurityRuleProtocol.TCP,
    source_port_range="*",
    destination_port_range="27017",
    source_address_prefix="VirtualNetwork", # Security best practice: restrict to VNet
    destination_address_prefix="VirtualNetwork",
    access=network.SecurityRuleAccess.ALLOW,
    priority=1010,
    direction=network.SecurityRuleDirection.INBOUND,
)

# Create a Subnet associated with the NSG
subnet = network.Subnet(f"{RESOURCE_NAME_PREFIX}-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24",
    network_security_group=network.NetworkSecurityGroupArgs(
        id=nsg.id
    )
)

# Provision 3 Virtual Machines
vm_public_ips = []
vm_private_ips = []

for i in range(1, 4):
    # Public IP Address for each VM
    public_ip = network.PublicIPAddress(f"{RESOURCE_NAME_PREFIX}-pip-{i}",
        resource_group_name=resource_group.name,
        public_ip_allocation_method="Static",
        dns_settings=network.PublicIPAddressDnsSettingsArgs(
            domain_name_label=f"{RESOURCE_NAME_PREFIX}-mongo-{i}"
        )
    )
    
    # Network Interface Card (NIC)
    nic = network.NetworkInterface(f"{RESOURCE_NAME_PREFIX}-nic-{i}",
        resource_group_name=resource_group.name,
        ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
            name="ipconfig1",
            subnet=network.SubnetArgs(id=subnet.id),
            public_ip_address=network.PublicIPAddressArgs(id=public_ip.id),
            private_ip_allocation_method="Static",
            private_ip_address=f"10.0.1.{3 + i}"
        )]
    )
    
    # Ubuntu 22.04 LTS VM
    vm = compute.VirtualMachine(f"{RESOURCE_NAME_PREFIX}-vm-{i}",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        hardware_profile=compute.HardwareProfileArgs(
            vm_size="Standard_B2s" # Cost-effective instance size (2 vCPUs, 4GB RAM)
        ),
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                publisher="Canonical",
                offer="0001-com-ubuntu-server-jammy",
                sku="22_04-lts-gen2",
                version="latest"
            ),
            os_disk=compute.OSDiskArgs(
                create_option="FromImage",
                managed_disk=compute.ManagedDiskParametersArgs(
                    storage_account_type="Standard_LRS"
                )
            )
        ),
        os_profile=compute.OSProfileArgs(
            computer_name=f"{RESOURCE_NAME_PREFIX}-node-{i}",
            admin_username="azureuser",
            admin_password=ssh_password,
            linux_configuration={
                "disable_password_authentication": False if has_password else True,
                "ssh": {
                    "public_keys": [{
                        "path": "/home/azureuser/.ssh/authorized_keys",
                        "key_data": ssh_public_key
                    }]
                } if ssh_public_key else None
            }
        ),
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[compute.NetworkInterfaceReferenceArgs(
                id=nic.id,
                primary=True
            )]
        )
    )
    
    # Collect IP Outputs
    vm_public_ips.append(public_ip.ip_address)
    # Safely retrieve private IP from IP configuration list output
    private_ip = nic.ip_configurations.apply(lambda configs: configs[0].private_ip_address)
    vm_private_ips.append(private_ip)

# Export the public and private IPs to be consumed by pyinfra
pulumi.export("resource_group", resource_group.name)
pulumi.export("vm_public_ips", vm_public_ips)
pulumi.export("vm_private_ips", vm_private_ips)
pulumi.export("ssh_user", "azureuser")
if has_password:
    pulumi.export("ssh_password", ssh_password)
