# Arch Server Deployment Guide

The Arch server is the core administrative and backend node. It hosts the Harbor container registry, serves as an NFS file server for the calculation nodes, runs the LolaPy backend application, and acts as a Slurm client to submit jobs.

Below are the manual Linux CLI instructions (targeted for Debian/Ubuntu environments) to replicate the automated Ansible deployment.

## 1. System Preparation & Users

Create a specific user (`lolauser`) for application components:

```bash
sudo useradd -m -s /bin/bash lolauser
sudo passwd lolauser # set the password
```

*(Optional) Install any custom cron jobs (e.g., `sftp.sh` synchronization script) into `/usr/local/bin/` and configure them via `crontab -e`.*

## 2. Docker Installation

Install Docker and Docker Compose to manage containerized services:

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Set up the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine and Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable and start Docker
sudo systemctl enable --now docker
```

To configure Docker to allow insecure connections to Harbor (if SSL is disabled):
```bash
sudo mkdir -p /etc/docker
echo '{ "insecure-registries": ["<ARCH_IP>:80"] }' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

## 3. Harbor Registry Setup

Harbor is used for hosting Docker images locally.

```bash
sudo mkdir -p /opt/harbor
cd /tmp

# Download the offline installer 
# (e.g. v2.13.3, check Harbor releases for the exact version)
wget https://github.com/goharbor/harbor/releases/download/v2.13.3/harbor-offline-installer-v2.13.3.tgz

# Extract
sudo tar -xvzf harbor-offline-installer-v2.13.3.tgz -C /opt/

# Configure Harbor
cd /opt/harbor
sudo cp harbor.yml.tmpl harbor.yml

# Edit harbor.yml:
# 1. Change 'hostname' to the Arch server IP or FQDN
# 2. Change 'harbor_admin_password'
# 3. If NOT using SSL, comment out the entire 'https' block (port, certificate, private_key)
sudo nano harbor.yml

# Install Harbor
sudo ./install.sh
```

## 4. NFS Server Configuration

The Arch node exports a shared filesystem to the Slurm computation clusters.

```bash
# Create shared directory
sudo mkdir -p /home/lolauser/nf-workdir
sudo chown lolauser:lolauser /home/lolauser/nf-workdir
sudo chmod 0755 /home/lolauser/nf-workdir

# Install NFS kernel server
sudo apt-get install -y nfs-kernel-server nfs-common

# Export the directory 
# (Replace * with the specific allowed subnet, e.g., 10.0.1.0/24)
echo "/home/lolauser/nf-workdir *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports

# Apply and restart
sudo systemctl enable --now nfs-kernel-server
sudo exportfs -ra
```

## 5. Slurm Client Setup

The client package allows submitting jobs to the Calc nodes.

```bash
# Install Munge and Slurm Client
sudo apt-get install -y munge libmunge-dev libmunge2 slurm-client

# The munge key must be identical to the one on the Calc (Slurm Controller) node.
# Copy /etc/munge/munge.key from the Calc node to this machine at /etc/munge/munge.key
# Then set permissions:
sudo chown munge:munge /etc/munge/munge.key
sudo chmod 0400 /etc/munge/munge.key
sudo systemctl enable --now munge

# Copy the configuration from the controller node to Arch:
# Place it at /etc/slurm/slurm.conf
```

## 6. LolaPy Backend Setup

The Lola Python API must be cloned and started with Docker Compose.

```bash
sudo mkdir -p /opt/lola
cd /opt/lola

# Clone the backend repository
sudo git clone -b test/devops <GIT_REPO_URL> ./lolapy
cd lolapy

# Create required directories
sudo mkdir -p certs

# Setup environment variables
sudo cp .env.sample .env
# Edit .env file to match your environment variables
# Must include HARBOR_HOST, HARBOR_PASSWORD, LOLAPY_HOST_IP, FRONTEND_API_IP
sudo nano .env

# Generate self-signed certificates
cd certs
sudo openssl genpkey -algorithm RSA -out private.key -pkeyopt rsa_keygen_bits:2048
sudo openssl req -new -x509 -key private.key -out certificate.crt -days 365 -subj "/CN=your-domain.com"
cd ..

# Fetch Docker group ID for volume permissions
DOCKER_GROUP=$(getent group docker | cut -d: -f3)

# Start the backend via Docker Compose
sudo DOCKER_GROUP=$DOCKER_GROUP docker compose -f docker-compose.yml up -d

# Fix permissions inside containers
sudo docker exec -u root lolapy-hueyconsumer-1 chown munge:munge /etc/munge/munge.key
sudo docker exec -u root lolapy-hueyconsumer-1 chown -R lolauser /tmp/certs
sudo docker exec -u root lolapy-hueyconsumer-1 chown -R lolauser /home/lolauser

# Prepare SFTP Directory
sudo docker exec lolapy-sftp-1 chown <SFTP_USER> /home/<SFTP_USER>/upload

# Restart Consumer
sudo docker compose -f docker-compose.yml restart hueyconsumer

# SSH Keys Creation for internal cluster access
sudo docker exec lolapy-hueyconsumer-1 ssh-keygen -q -t rsa -b 4096 -N "" -f /home/lolauser/.ssh/id_rsa
```
