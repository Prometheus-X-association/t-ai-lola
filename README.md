# Trustworthy AI: algorithm assessment BB – LOLA

<!--_Short description of the BB._-->
LOLA is an autonomous platform designed to audit AI algorithms using datasets shared by the EdTech community. The platform allows users to experiment with algorithms across different datasets and benchmark multiple algorithms on the same dataset. The main challenges addressed by LOLA include transparency, security, and innovation in algorithm evaluation.

## Design Document
See the design document [here](docs/).

## Building instructions

**Note:** This program works only on Linux 64bits and MacOS (not tested).

To build the LOLA system, follow these steps:
### 1. Clone the repository

The test repository contains all necessary files to validate the LOLA system, including data (Trax-LRS setup), algorithms, scenarios, and configuration files.

```sh
git clone https://gitlab.inria.fr/okuksa/stage1-test.git
cd stage1-test
```

This repository includes two main directories and README file:
- `/data` – contains Trax-LRS and the OULAD dataset
- `/sandbox_workdir` – includes algorithms, scenarios, workdir (results), and the configuration file for LOLA-Sandbox
- `README.md` - where you can check how to use it

### 2. Install LOLA-Sandbox
Note: A python environment is recommanded (not required) for sandbox to avoid polluting base environment with dependencies. You can use conda/miniconda or  venv
```sh
cd /tmp
git clone git@gitlab.inria.fr:lola/lola-sandbox.git
cd lola-sandbox
conda create -y -n my_env python=3.10
conda activate my_env
python -m pip install .
```

### 3. Install and configure Trax-LRS
1. **Create the environment file for the service.**

    ```sh
    make env
    ```
    
    This command create a `.env` and a `.envrc` files at the root of the repository. This file contains all data required by the service to work. You can edit all parameters if you need.  
      
    **Note:** If you move the project (change directory), you have to remove the `.env` file and re-generate the `.env` file with `make env`.
    
2. **Build docker images or get Docker images from Loria forge**

    Download images on the Loria forge (note that you need a connection to the Inria VPN):

   ```sh
   docker pull harbor.loria.fr/lola/trax_admin:latest
   docker tag harbor.loria.fr/lola/trax_admin:latest trax_trax:latest

   docker pull harbor.loria.fr/lola/trax_client:latest
   docker tag harbor.loria.fr/lola/trax_admin:latest trax_client:latest
   ```
    
    - **trax_admin** or **trax_trax** : is the classic trax image used to upload and consult data.  
    - **trax_client** : is an image based on `trax_trax` but with an edition in its apache server that disable modification of the database. In fact, with `trax_client`, you can only see your data, not edit them. The web interface is also unavailable (login in web interface needs POST).  

3. **Run the service and setup for the first run**

    ```sh
    make up
    ```
    
    Now you can set up the first run:
    
    ```sh
    make trax_initdb
    make trax_create_client
    make trax_create_admin
    ```
    This initialise the sql database. Next lines create account for the web interface (admin account) and for http client (client account). Please do not forget to **SAVE** your **credentials** and **passwords** displayed on your prompt.
      
    Without editing configuration, your services should be available:
    
    ```sh
    make ps
    ```
    ```
    trax_db           docker-entrypoint.sh --def ...   Up      0.0.0.0:3306->3306/tcp,:::3306->3306/tcp, 33060/tcp
    trax_phpmyadmin   /docker-entrypoint.sh apac ...   Up      0.0.0.0:8080->80/tcp,:::8080->80/tcp
    trax_trax         docker-php-entrypoint apac ...   Up      443/tcp, 0.0.0.0:80->80/tcp
    ```
    
    You can now connect to http://localhost:80 and use your admin credential.

4. **Upload xapi data to the LRS**
    ```sh
    curl --request POST localhost:80/trax/ws/xapi/statements \
     --header 'X-Experience-API-Version: 1.0.3' \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     -u testsuite:password \
     --data "@oulad-data.json"
    ```

    
## Running instructions
1. **Move the sandbox_workdir folder to $HOME**
    ```sh
    mv sandbox_workdir $HOME/
    ```
2. **Run the scenario using LOLA-Sandbox**
   ```sh
   cd $HOME/sandbox_workdir
   lola-sandbox run --lrs-host http://localhost:80 -w workdir -C recommandation_params.json
   ```

## Example usage
_Describe how to check some basic functionality of the BB._
E.g.:

Send the following requests to the designated endpoints:
| Endpoint      | Example input | Expected output   |
| ------------- | ------------- | ----------------- |
| /hello        | World         | 200, Hello World! |
|               |               |                   |
|               |               |                   |

## Unit testing
To ensure the correct functioning of the LOLA platform, unit tests will focus on three key components: Trax-LRS, the algorithm execution, and the scenario validation within LOLA-sandbox.


### Setup test environment
### Run tests
1. **Trax-LRS**

    Uploading data to Trax-LRS
    ```sh
    curl --request POST localhost:80/trax/ws/xapi/statements --header 'X-Experience-API-Version: 1.0.3' --header 'Content-Type: application/json' --header 'Accept: application/json' -u testsuite:password --data "@oulad-data.json"
    ```
    Checking that the data is successfully uploaded to Trax-LRS
    ```sh
    curl --request GET localhost:80/trax/ws/xapi/statements --header 'X-Experience-API-Version: 1.0.3' --header 'Content-Type: application/json' --header 'Accept: application/json' -u testsuite:password
    ```

2. **Algorithm execution**
    Test uploading an algorithm to Harbor:
    ```sh
    docker tag my_algorithm:latest harbor.loria.fr/lola/my_algorithm:latest
    docker push harbor.loria.fr/lola/my_algorithm:latest
    ```

   Test pulling and running an algorithm from Harbor:
   ```sh
   docker pull harbor.loria.fr/lola/svdpp_recom:latest
   docker run --rm harbor.loria.fr/lola/svdpp_recom:latest
   ```
### Expected results
**Trax-LRS** successfully stores and retrieves datasets.
**Algorithms** are correctly uploaded, pulled, and executed from Harbor.

## Component-level testing
### Setup test environment
Ensure that LOLA-Sandbox and all required services are running correctly.
    1. **Trax-LRS is running**
    ```sh
    docker ps
    ```
    ```
    CONTAINER ID   IMAGE                   COMMAND                  CREATED          STATUS          PORTS                                                  NAMES
    664cef73b46f   phpmyadmin/phpmyadmin   "/docker-entrypoint.…"   26 minutes ago   Up 26 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp                trax_phpmyadmin
    b62398881ffa   trax_trax               "docker-php-entrypoi…"   26 minutes ago   Up 22 minutes   0.0.0.0:80->80/tcp, 443/tcp                            trax_trax
    99454f8c3fec   mysql:5.7.31            "docker-entrypoint.s…"   26 minutes ago   Up 26 minutes   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   trax_db
    ```

    2. **You have images of algorithms and scenarios from Harbor**

    ```sh
    docker images
    ```
    ```sh
    harbor.loria.fr/lola/recommandation            1.1.0_switchable   3f006208d82e   2 years ago     1.35GB
    harbor.loria.fr/lola/svdpp_recom               latest             1b032219cb1b   2 years ago     1.1GB
    lola.lhs.loria.fr:4443/sisr_user/svdpp_recom   latest             1b032219cb1b   2 years ago     1.1GB
    harbor.loria.fr/lola/test_recom                latest             2c6adb930d4f   2 years ago     1.1GB
    lola.lhs.loria.fr:4443/sisr_user/test_recom    latest             2c6adb930d4f   2 years ago     1.1GB
    ```
### Run tests
Run your scenario with lola-sandbox

    ```sh
    cd $HOME/sandbox_wrkdir
    lola-sandbox run --lrs-host http://localhost:80 -w workdir -C recommandation_params.json
    ```


### Expected results

```sh
Launching /home/lap/sandbox_wdir/scenarios/recommandation/main.nf [Ra72661fb-db59-49c3-9b95-80e151028d45] DSL2 - revision: e75d58603e

executor >  local (8)
[04/90b533] process > requestData     [100%] 1 of 1 ✔
[b2/3151a2] process > svd_train       [100%] 1 of 1 ✔
[49/1b424a] process > svd_test (1)    [100%] 1 of 1 ✔
[c1/76c22e] process > svd_eval (1)    [100%] 1 of 1 ✔
[0d/d0252e] process > userModel       [100%] 1 of 1 ✔
[3d/5745a0] process > userTest (1)    [100%] 1 of 1 ✔
[d0/1c22b9] process > userEval (1)    [100%] 1 of 1 ✔
[7f/7184d4] process > mergeResProcess [100%] 1 of 1 ✔

2025-02-28 00:18:37,366:INFO:Results and data of the run stored in '/home/lap/sandbox_wdir/workdir/Ra72661fb-db59-49c3-9b95-80e151028d45'
2025-02-28 00:18:37,367:INFO:Result files should be in :
2025-02-28 00:18:37,367:INFO:  /home/lap/sandbox_wdir/workdir/Ra72661fb-db59-49c3-9b95-80e151028d45/7f/7184d4e6fe9103cb7c7221bb66aa18/output.json
```
Visit the specified directory (in our case `/home/lap/sandbox_wdir/workdir/Ra72661fb-db59-49c3-9b95-80e151028d45/7f/7184d4e6fe9103cb7c7221bb66aa18/output.json`) and view the results in the output.json folder
