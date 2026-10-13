Resource: https://www.youtube.com/playlist?list=PL7iMyoQPMtAOtZSkmBatClzzB0Et60iAR

### Getting Started
- Login using MS Account
- Use Free Credits
- Create Subscription
- Auto Validate/Review each Resource created/updated

### Azure Network
- Resource Group
    - Logical Unit to group resources
    - Has attached Billing Subscription
    - Contains VNETs, Subnets, VMs etc resources
    - Has a Region (location of Physical Data Centers)
    - Add Tags (Keys and Values) particularly for Team Ownership, Project Name and Version
- VNET
    - A Virtual Network
    - Has CIDR Notation for IP Range
    - Has attached Subscription and Resource Group
    - Has Network Encryption (TLS/SSL), Firewall (Rules for Incomming and Outgoing Messages), DDoS Protection
    - Add Tags
- Subnets
    - A Subnet within VNET
    - Has Base Network IP and CIDR Prefix for IP Range
    - Select IPv4 vs IPv6 for IPs
    - Type: Public or Private (Depends on Route Table Config)
- Route Table
    - A Table for Rules of IP Routing or Mapping
    - Has Resource Group
    - Belows to a Region
    - Add Tags
    - Associate a Subnet
    - Public: Attach Internet to 0.0.0.0/0 IP in Route Table
    - Private: Nothing/
- Network Security Layer
- VM
    - Select Resource Group
    - Select Region
    - Select Image
    - Select Compute, Memory and Storage
    - Add/Download SSH Key and SSH Username & Port
    - Select Default Key Management
    - Select VNET, Subnet
    - Select Load Balancer
    - Add Backup, Alerts and Init Script & Seed Data
    - Add Tags
    - See the Private and Public IP Addresses
- Access VM
    - SSH client
    - Azure CLI
    - Azure Bastion
- VNET PEERING
    - Config Peering in VNET Options
- DNS
    - General Flow:
        - User enters Domain Name in Browser
        - Browser sends DN Resolver Server (ISP)
        - DN Serves have Anycasted (Same IP to all Nodes in Network)
        - DN Resolves Recursively (Top -> Bottom, Root -> Node, Less Authoritative -> More Authoritative)
        - DB Have Record (CNAME for Intermidiate DN Resolution Servers, NS for Forwarded Server, (A)NAME for IP) that Maps DN to IP Address (TTL)
        - Browser Caches the Record
    - Create DNS Zone
        - Select Subscription
        - Select Resource Group
        - Give a Name to DNS Zone
        - Add Certbot for HTTPS certificate
        - Allow https at 443 in Inbound Rules of Network Security Group

### CIDR
- Subnet IPs = Network IP + Host Usable IP + Broadcast IP
- Represent Subnet IPs Range using CIDR (Network_IP/Prefix or Network_IP/Subnet_Mask)
- Prefix & Subnet Mask are Inter-Convertible
- Example:
    - 192.168.1.0/26
    - /26 → 11111111.11111111.11111111.11000000
    - 11111111.11111111.11111111.11000000 -> 255.255.255.192
    - 256−192=64
    - Starting at 192.168.1.0, count 64 addresses, from 0 to 63.

### Notes
AuthN/AuthO -> Cognito and IAM
CORS -> AWS Security Layer
CSRF/SSRF -> AWS Security Layer
OD Ingress/Egress Rules -> AWS WAF
Routing Tables -> AWS Subnets