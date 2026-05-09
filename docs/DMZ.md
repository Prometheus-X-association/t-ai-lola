# DMZ Server Deployment Guide

The DMZ (Demilitarized Zone) server handles public-facing ingress. It hosts the Frontend application components and handles initial traffic routing.

Below are the manual Linux CLI instructions (targeted for Debian/Ubuntu environments) to replicate the automated Ansible deployment.

## 1. Docker Installation

The frontend is served exclusively through Docker containers.

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

## 2. Harbor Installation (Optional)

Based on the automation playbooks, Harbor acts as an image registry. If mirroring is required in the DMZ:

```bash
sudo mkdir -p /opt/harbor
cd /tmp

# Download the offline installer 
wget https://github.com/goharbor/harbor/releases/download/v2.13.3/harbor-offline-installer-v2.13.3.tgz

# Extract and install
sudo tar -xvzf harbor-offline-installer-v2.13.3.tgz -C /opt/
cd /opt/harbor
sudo cp harbor.yml.tmpl harbor.yml

# Edit harbor.yml (Update 'hostname' and 'harbor_admin_password')
# Disable 'https' block if not terminating SSL there.
sudo nano harbor.yml

# Run installer
sudo ./install.sh
```

## 3. Frontend Application Setup

The DMZ requires pulling the frontend source code repository, injecting the Arch target IP for the backend API, and running a database initialization sequence.

```bash
# Prepare the destination directory
sudo mkdir -p /opt/lola
cd /opt/lola

# Clone the Git repository (test/devops branch)
sudo git clone -b fix/devops <GIT_REPO_URL> ./frontend
cd frontend

# Set up environment variables
sudo cp .env.sample .env

# Edit .env substituting backend connections:
# e.g., LOLAPY_API_ADRESS=<ARCH_IP>
# e.g., ENABLE_API_ACCESS_CONTROL=true
# e.g., MYSQL_HOST=db
sudo nano .env

# Copy the configuration variable file directly into the application build path
sudo mkdir -p build/app/
sudo cp .env build/app/.env

# Start the stack using Docker Compose
sudo docker compose up -d

# Wait ~60 seconds for the 'db' container to fully initialize MySQL.
sleep 60

# Run the database fixtures command (typically defined in a Makefile)
# This populates initial schema tracking.
sudo make app_db_fixture_dev

# Fix SFTP upload permissions
sudo docker exec frontend-sftp-1 chown <DMZ_SFTP_USER> "/home/<DMZ_SFTP_USER>/upload"
```

> [!NOTE]
> The frontend stack uses an Nginx/Apache container bound to port `80` (and `443` for SSL) to serve traffic externally. Make sure your DMZ firewall permits these ingress ports.
