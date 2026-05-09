# Lola Cloud Infrastructure

Welcome to the Lola cloud repository. This project orchestrates a distributed, high-performance web architecture designed for modular deployment, encompassing computation clusters, a container registry, and public-facing services.

## 📂 Project Hierarchy

The repository is structured to separate application source code, infrastructure deployment automation, and detailed manual documentation:

- **`app/`**: Contains the application logic and modules (e.g., the `lolapy` backend) that drive the core functionality of PrometheusX.
- **`deploy/`**: Houses all automation configurations. Contains the `ansible/` directory, which holds the playbooks, roles, and inventory required to deploy the entire infrastructure across target nodes automatically.
- **`docs/`**: Contains in-depth, manual Linux CLI deployment guides for each specific segment of the architecture (`ARCH.md`, `CALC.md`, `DMZ.md`).

## 🏗️ Architecture Components

The infrastructure is segmented into three distinct roles to ensure security, scalability, and performance. 

### 1. DMZ (Demilitarized Zone)
The **DMZ** is the gateway to the infrastructure. It is the only component directly exposed to the public internet, acting as a secure buffer to the internal network.
* **Role**: Hosts the frontend application and manages initial user traffic ingress.
* **Key Technologies**: Docker, Docker Compose, Harbor Registry (for frontend image pulling/mirroring), and SFTP drop points.
* **Documentation**: See [`docs/DMZ.md`](docs/DMZ.md) for detailed manual installation steps.

### 2. ARCH (Storage & Backend APIs)
The **ARCH** node functions as the backbone of the system's administration and application logic. It operates within a secure, internal network.
* **Role**: Hosts the centralized Harbor container registry for internal services, hosts the LolaPy Python backend, and acts as the central NFS file server for distributed storage. It also serves as a client to submit workloads to the calculation cluster.
* **Key Technologies**: Docker, Harbor, NFS Kernel Server, Slurm Client, LolaPy Application.
* **Documentation**: See [`docs/ARCH.md`](docs/ARCH.md) for detailed manual installation steps.

### 3. CALC (Computation Cluster)
The **CALC** environment is dedicated to heavy workload execution. It consists of controller and worker nodes designed to handle resource-intensive computations dispatched from the backend.
* **Role**: Processes application tasks and pipelines using the Slurm workload manager, seamlessly reading/writing data from the shared Arch NFS mount.
* **Key Technologies**: Slurm Workload Manager (Controller and Worker logic), Munge Authentication, Docker, NFS Client.
* **Documentation**: See [`docs/CALC.md`](docs/CALC.md) for detailed manual installation steps.

---

### Deployment

* **Automated**: For automated deployment, navigate to `deploy/ansible` and refer to the [Ansible README](deploy/ansible/README.md).
* **Manual**: For step-by-step CLI setup on bare-metal or VMs, refer to the individual markdown files in the `docs/` directory.
