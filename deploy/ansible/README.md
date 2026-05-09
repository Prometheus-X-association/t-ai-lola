# Ansible Deployment for PrometheusX (LOLA)

This directory contains Ansible playbooks and roles for deploying the PrometheusX infrastructure, including the DMZ, Arch, and Calc environments.

## 🏗️ Architecture Overview

The deployment is split into three main components:

- **DMZ (Demilitarized Zone)**: Hosts the frontend and provides public-facing services.
- **Arch (Archive/Registry)**: Hosts the Harbor registry, GitLab-linked services, and the NFS server for shared storage.
- **Calc (Calculation)**: Hosts the Slurm cluster for heavy computation and acts as an NFS client.

## 📋 Prerequisites

Before running the playbooks, ensure the following are installed and configured:

1.  **Python 3.10+**: Required on both the control node (your machine) and all target servers.
2.  **Ansible**: Installed on the control node.
    ```bash
    pip install ansible
    ```
3.  **SSH Access**: Ensure you have SSH access to all target hosts. A bastion host is **not mandatory**. However, if your environment requires it, you can configure a `ProxyJump` in your `inventory/hosts.yml` like this:
    ```yaml
    ansible_ssh_common_args: >
      -o ProxyJump=bastion-user@bastion-host
    ```
    Alternatively, configure your SSH config (`~/.ssh/config`). Ensure to update `inventory/hosts.yml` with the correct IPs and usernames for your environment.
4.  **Network Connectivity**: The nodes must be able to communicate according to the roles (e.g., Calc nodes must reach the NFS server in Arch).

## ⚙️ Configuration

### 1. Inventory

Update `inventory/hosts.yml` with the correct IP addresses or hostnames for your environment.

### 2. Variables (IMPORTANT)

The variables in `inventory/group_vars/` have been cleared for security. **You must populate these files before running the playbooks.**

-   **`arch.yml`**: Configure `git_repo_url` (with token), `harbor_password`, `arch_ip`, etc.
-   **`dmz.yml`**: Configure `git_repo_url`, `harbor_hostname`, etc.
-   **`calc.yml`**: Configure `nfs_server_ip`, `slurm_role`, etc.

Every variable currently set to `""` in these files must be filled with a valid value.

## 🚀 Usage

### Run individual deployments

-   **Deploy DMZ (Frontend)**:
    ```bash
    ansible-playbook playbooks/dmz.yml -i inventory/hosts.yml
    ```

-   **Deploy Arch (Registry/Storage)**:
    ```bash
    ansible-playbook playbooks/arch.yml -i inventory/hosts.yml
    ```

-   **Deploy Calc (Slurm/Compute)**:
    ```bash
    ansible-playbook playbooks/calc.yml -i inventory/hosts.yml
    ```

### Run the full deployment

To deploy the entire infrastructure in the correct order (Arch, then Calc, then DMZ):

```bash
ansible-playbook playbooks/deploy_all.yml -i inventory/hosts.yml
```

## 🔍 Audit & Logs

-   **Roles**: Found in the `roles/` directory. Each role is self-contained.
-   **Artifacts**: Playbooks will create logs and may require specific permissions (sudo) on the target hosts.

> [!CAUTION]
> Never commit `group_vars` files containing cleartext passwords or tokens to version control. Use Ansible Vault for sensitive data if needed.