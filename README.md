# Trustworthy AI: algorithm assessment BB – LOLA

<!--_Short description of the BB._-->
LOLA is an autonomous platform designed to audit AI algorithms using datasets shared by the EdTech community. The platform allows users to experiment with algorithms across different datasets and benchmark multiple algorithms on the same dataset. The main challenges addressed by LOLA include transparency, security, and innovation in algorithm evaluation.

This project sets up an xAPI Learning Record Store (LRS) using TRAX, loads OULAD dataset into it, and executes a LOLA Sandbox scenario for recommendation testing.

The system consists of:
- Trax LRS – a Laravel-based Learning Record Store (LRS) for storing xAPI data
- LOLA Sandbox – a scenario execution framework for recommendation algorithms
- Docker & Makefile Automation – automated setup and execution using Docker and Makefiles

    
## Design Document
See the design document [here](docs/).

## Building instructions

**1. Clone the repository**

```
git clone https://gitlab.inria.fr/okuksa/stage1-test.git
cd stage1-test
```

**2. Connect to Inria’s Internal Network (VPN)**

**Important:** To download the required TRAX Docker images, you must be connected to Inria's internal network. This can be done via VPN.

### How to connect to Inria VPN
- download and install Cisco AnyConnect VPN Client (available at: https://vpn.inria.fr)
- open Cisco AnyConnect and enter the server address:
    ``` vpn.inria.fr ```
- login with your Inria credentials

**3. Download TRAX Docker images**

After connecting to the VPN, run the following commands to download and tag the TRAX images:

```
docker pull harbor.loria.fr/lola/trax_admin:latest
docker tag harbor.loria.fr/lola/trax_admin:latest trax_trax

docker pull harbor.loria.fr/lola/trax_client:latest
docker tag harbor.loria.fr/lola/trax_admin:latest trax_client
```


    
## Running instructions
**1. Run the project**

Run the following command in the project root directory:
```
make up
```

This command:
- starts Trax LRS using docker-compose
- loads the OULAD dataset automatically into TRAX
- installs LOLA Sandbox locally
- executes the recommendation scenario

**2. Verify running services**

Check if the containers are running:
```
docker ps
```

## Example usage

**1. Access TRAX Web Interface**

- open http://localhost:80 in a browser
- login with admin credentials (generated during setup)

**2. Inspect results**

The LOLA Sandbox execution results are stored in `/sandbox_wdir/workdir`

## Unit testing
To ensure the correct functioning of the LOLA platform, unit tests will focus on three key components: installing Trax LRS, uploading data to Trax LRS and scenario execution.

### Setup test environment
If you’ve already run **building and running instructions**, skip this step

Check if services are running:
```
docker ps

Result:
b0c388f68312   phpmyadmin/phpmyadmin   "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp                trax_phpmyadmin
98fc9e3959c6   trax_trax               "docker-php-entrypoi…"   2 minutes ago   Up 2 minutes   0.0.0.0:80->80/tcp, 443/tcp                            trax_trax
b5c6f9853f77   mysql:8.0               "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   trax_db
```

```
docker images

Result:
curlimages/curl                    latest    5dce198cca46   3 weeks ago     28.1MB
phpmyadmin/phpmyadmin              latest    0276a66ce322   5 weeks ago     571MB
mysql                              8.0       6616596982ed   6 weeks ago     764MB
harbor.loria.fr/lola/trax_client   latest    5e7cb9a86b4f   4 years ago     662MB
harbor.loria.fr/lola/trax_admin    latest    7fe95b918e45   4 years ago     662MB
trax_client                        latest    7fe95b918e45   4 years ago     662MB
trax_trax                          latest    7fe95b918e45   4 years ago     662MB
```
Otherwise, follow these:

**1. Trax installing**

Download TRAX Docker images via  Inria VPN:
```
docker pull harbor.loria.fr/lola/trax_admin:latest
docker tag harbor.loria.fr/lola/trax_admin:latest trax_trax

docker pull harbor.loria.fr/lola/trax_client:latest
docker tag harbor.loria.fr/lola/trax_admin:latest trax_client
```

Installing trax:
```
cd data/trax
make create_trax
```

**2. Lola-sandbox installing (scenario executer)**

Installing lola-sandbox in the project root

```
make install_lola_sandbox
```

### Run tests

**1. For Trax LRS (upload data to Trax LRS):**
```
cd data/trax
make upload_data
```

**2. For scenario execution - lola-sandbox (after Trax data is uploaded!):**
In the root of the project:
```
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
[3b/6779b5] process > svd_train       [100%] 1 of 1 ✔
[17/b2fc3d] process > svd_test (1)    [100%] 1 of 1 ✔
[fe/dd09d8] process > svd_eval (1)    [100%] 1 of 1 ✔
[d1/324c2f] process > userModel       [100%] 1 of 1 ✔
[20/d2fd2e] process > userTest (1)    [100%] 1 of 1 ✔
[7a/bab146] process > userEval (1)    [100%] 1 of 1 ✔
[b8/214adb] process > mergeResProcess [100%] 1 of 1 ✔

2025-03-07 09:18:45,198:INFO:Results and data of the run stored in '/home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a'
2025-03-07 09:18:45,199:INFO:Result files should be in :
2025-03-07 09:18:45,199:INFO:  /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json
```

isit the specified directory (in our case /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json) and view the results in the output.json folder

## Component-level testing
### Setup test environment
Check if services are running:
```
docker ps

Result:
b0c388f68312   phpmyadmin/phpmyadmin   "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp                trax_phpmyadmin
98fc9e3959c6   trax_trax               "docker-php-entrypoi…"   2 minutes ago   Up 2 minutes   0.0.0.0:80->80/tcp, 443/tcp                            trax_trax
b5c6f9853f77   mysql:8.0               "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   trax_db
```

```
docker images

Result:
curlimages/curl                    latest    5dce198cca46   3 weeks ago     28.1MB
phpmyadmin/phpmyadmin              latest    0276a66ce322   5 weeks ago     571MB
mysql                              8.0       6616596982ed   6 weeks ago     764MB
harbor.loria.fr/lola/trax_client   latest    5e7cb9a86b4f   4 years ago     662MB
harbor.loria.fr/lola/trax_admin    latest    7fe95b918e45   4 years ago     662MB
trax_client                        latest    7fe95b918e45   4 years ago     662MB
trax_trax                          latest    7fe95b918e45   4 years ago     662MB
```
Otherwise, follow the building instructions.

### Run tests
Simply run:
```
make up
```

### Expected results
You should see in the terminal following result:

```
executor >  local (8)
[7c/c9b36b] process > requestData     [100%] 1 of 1 ✔
[3b/6779b5] process > svd_train       [100%] 1 of 1 ✔
[17/b2fc3d] process > svd_test (1)    [100%] 1 of 1 ✔
[fe/dd09d8] process > svd_eval (1)    [100%] 1 of 1 ✔
[d1/324c2f] process > userModel       [100%] 1 of 1 ✔
[20/d2fd2e] process > userTest (1)    [100%] 1 of 1 ✔
[7a/bab146] process > userEval (1)    [100%] 1 of 1 ✔
[b8/214adb] process > mergeResProcess [100%] 1 of 1 ✔

2025-03-07 09:18:45,198:INFO:Results and data of the run stored in '/home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a'
2025-03-07 09:18:45,199:INFO:Result files should be in :
2025-03-07 09:18:45,199:INFO:  /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json
```

isit the specified directory (in our case /home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json) and view the results in the output.json folder
