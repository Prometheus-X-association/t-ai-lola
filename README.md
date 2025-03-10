# Trustworthy AI: algorithm assessment BB – LOLA

<!--_Short description of the BB._-->
LOLA is an autonomous platform designed to audit AI algorithms using datasets shared by the EdTech community. The platform allows users to experiment with algorithms across different datasets and benchmark multiple algorithms on the same dataset. The main challenges addressed by LOLA include transparency, security, and innovation in algorithm evaluation.

This project sets up an xAPI Learning Record Store (LRS) using TRAX, loads OULAD dataset into it, and executes a LOLA Sandbox scenario for recommendation testing.

The project consists of two main components:
1. Trax LRS (Learning Record Store) – stores and manages xAPI data
2. LOLA Sandbox – runs recommendation scenarios based on algorithms

    
## Design Document
See the design document [here](docs/).

## Building instructions

**Clone the repository**

```
git clone git@github.com:Prometheus-X-association/t-ai-lola.git
cd t-ai-lola
```

## Running instructions

**1. Setup TRAX and uploadging data**

```
cd data/trax
make up
cd ../..
```
**2. Setup Lola-sandbox and scenario execution**
```
cd sandbox_wdir
make up
```

## Example usage

**1. Access TRAX Web Interface**

- open http://localhost:80 in a browser
- login with admin credentials (generated during setup)

**2. Inspect results**

The LOLA Sandbox execution results are stored in `/sandbox_wdir/workdir`

## Unit testing
To ensure the correct functioning of the LOLA platform, unit tests will focus on two key components: uploading data to Trax LRS and scenario execution.

### Setup test environment
If you've already run the setup instructions, verify services are running

```
docker ps
```

Expected result
```
b0c388f68312   phpmyadmin/phpmyadmin   "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp                trax_phpmyadmin
98fc9e3959c6   trax_trax               "docker-php-entrypoi…"   2 minutes ago   Up 2 minutes   0.0.0.0:80->80/tcp, 443/tcp                            trax_trax
b5c6f9853f77   mysql:8.0               "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   trax_db
```


Otherwise, follow **building** and **running instructions**.

### Run tests

**1. For Trax LRS (upload data to Trax LRS):**
```
cd data/trax
make upload_data
```

**2. For scenario execution - lola-sandbox (after Trax data is uploaded!):**

```
cd sandbox_wdir
make run_sandbox
```

### Expected results
**1. Trax LRS:**

- open [http://localhost:80]
- login with the admin credentials shown in the terminal
Example (your credential will look different), 
```
+-----------------+-----------------+
| Identifier      | Password        |
+-----------------+-----------------+
| admin@trax.test | -0iNq[3').DY)$z |
+-----------------+-----------------+
```
- navigate to "Statements" and verify that oulad-data.json data is loaded

**2. Lola-sandbox (scenario executor)**
You should see in the terminal following result:

```
executor >  local (8)
[7c/c9b36b] process > requestData     [100%] 1 of 1 ✔
...

2025-03-07 09:18:45,199:INFO:Result files should be in :
2025-03-07 09:18:45,199:INFO:  /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json
```

isit the specified directory (in our case /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json) and view the results in the output.json folder

## Component-level testing
### Setup test environment

The run tests will setup test environment by itself.

**Note: ** A python environment is recommanded (not required) for sandbox to avoid polluting base environment with dependencies. You can use [conda/miniconda](https://www.anaconda.com/docs/main) or  venv

### Conda environment installation
Quick installation of conda on Linux x68 to manage Python environment.
For more information on conda, see the official documentation https://docs.conda.io or miniconda
**Note: ** This tuto show the installation of miniconda instead of conda. Miniconda is just a lighter version of Conda.

```
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
$HOME/miniconda/bin/conda init bash
echo auto_activate_base: false >> ~/.condarc
echo 'export PATH=$PATH:$HOME/miniconda/bin' >> ~/.bashrc
source ~/.bashrc
```

### Run tests
## 1. Trax installation

Run the following command in the project root directory:
```
cd /data/trax
make up
```
This command:
- starts Trax LRS using docker-compose
- loads the OULAD dataset automatically into TRAX

## 2. Lola-sandbox setup

### Lola-sanbox installation and scenario execution

**Note:**
- If Conda is detected, the system will automatically install dependencies inside a Conda environment
- If Conda is not installed, dependencies will be installed system-wide

```
cd /sandbox_wdir
make up
```

### Expected results

```
executor >  local (8)
[7c/c9b36b] process > requestData     [100%] 1 of 1 ✔
...

2025-03-07 09:18:45,199:INFO:Result files should be in :
2025-03-07 09:18:45,199:INFO:  /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json
```

isit the specified directory (in our case /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json) and view the results in the output.json folder

