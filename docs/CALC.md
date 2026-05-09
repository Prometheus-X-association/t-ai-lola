# Calc Server Deployment Guide

The Calc server is responsible for running the computation workloads. It primarily hosts the Slurm workload manager (Controller and Worker) and mounts the shared NFS storage from the Arch server.

Below are the manual Linux CLI instructions (targeted for Debian/Ubuntu environments) to replicate the automated Ansible deployment.

## 1. System Preparation & Users

Create a specific user (`lolauser`) to match the Arch node to ensure file ownership consistency over NFS:

```bash
sudo useradd -m -s /bin/bash lolauser
```

## 2. Docker Installation

Install Docker to allow jobs submitted to Slurm to run inside containers if required.

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

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Enable and start Docker
sudo systemctl enable --now docker
```

## 3. NFS Client Configuration

Calc nodes must mount the shared workspace hosted on the Arch node to facilitate job data exchange.

```bash
# Install NFS client packages
sudo apt-get install -y nfs-common

# Create the mount point directory locally
sudo mkdir -p /home/lolauser/nf-workdir

# Test the manual mount (Replace <ARCH_IP> with the Arch server IP)
sudo mount -t nfs <ARCH_IP>:/home/lolauser/nf-workdir /home/lolauser/nf-workdir

# Persist the mount via /etc/fstab
echo "<ARCH_IP>:/home/lolauser/nf-workdir /home/lolauser/nf-workdir nfs defaults 0 0" | sudo tee -a /etc/fstab

# Apply mount
sudo mount -a
```

## 4. SSH Key Distribution

In distributed HPC clusters, nodes need to communicate passwordlessly.
You should copy the public key (`id_rsa.pub`) generated in the LolaPy container on the Arch node into the `/root/.ssh/authorized_keys` and `/home/lolauser/.ssh/authorized_keys` on the Calc node(s).

## 5. Slurm Controller and Munge Setup

Slurm acts as the resource manager, scheduling and allocating jobs across compute partitions. Munge creates cryptographic credentials.

```bash
# Install Munge
sudo apt-get install -y munge libmunge-dev libmunge2

# Generate a Munge key (if it does not already exist)
sudo create-munge-key

# Ensure secure permissions
sudo chown munge:munge /etc/munge/munge.key
sudo chmod 0400 /etc/munge/munge.key

# Start Munge
sudo systemctl enable --now munge

# IMPORTANT: You must copy this /etc/munge/munge.key to the Arch node 
# (and all Worker nodes, if separate) so they accept jobs from each other.
```

### Install Slurm Daemons

Since this node hosts `slurmctld` (the centralized controller) and `slurmd` (the local execution worker).

```bash
# Install Slurm packages
sudo apt-get install -y slurm-wlm slurmctld slurm-client

# Set up required directories
sudo mkdir -p /etc/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm:slurm /var/log/slurm
sudo chmod 0755 /var/log/slurm

# Create spool state directories
sudo mkdir -p /var/spool/slurm
sudo mkdir -p /var/spool/slurmctld
sudo chown slurm:slurm /var/spool/slurm /var/spool/slurmctld 
sudo chmod 0755 /var/spool/slurm /var/spool/slurmctld 

# Create /etc/slurm/slurm.conf 
# Ensure it defines the 'ClusterName', the 'SlurmctldHost', the Nodes, and Partition accurately.
sudo nano /etc/slurm/slurm.conf

# Start Slurm Controller and Worker
sudo systemctl enable --now slurmctld
sudo systemctl enable --now slurmd
```

> [!NOTE]
> The `/etc/slurm/slurm.conf` file created here must be identical to the one copied over to the Arch server (which acts as a Slurm client).
