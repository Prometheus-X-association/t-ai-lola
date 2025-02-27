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
git clone [https://gitlab.inria.fr/lola/test-repository.git](https://gitlab.inria.fr/okuksa/stage1-test.git)
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
    trax_db           docker-entrypoint.sh --def ...   Up      0.0.0.0:3306->3306/tcp,:::3306->3306/tcp, 33060/tcp
    trax_phpmyadmin   /docker-entrypoint.sh apac ...   Up      0.0.0.0:8080->80/tcp,:::8080->80/tcp
    trax_trax         docker-php-entrypoint apac ...   Up      443/tcp, 0.0.0.0:80->80/tcp
    ```
    
    You can now connect to http://localhost:80 and use your admin credential.

4. **Upload xapi data to the LRS.**
```sh
curl --request POST localhost:80/trax/ws/xapi/statements \
 --header 'X-Experience-API-Version: 1.0.3' \
 --header 'Content-Type: application/json' \
 --header 'Accept: application/json' \
 -u testsuite:password \
 --data "@oulad-data.json"
```
## Running instructions
_Describe how to run the BB._

E.g.: `docker compose up` or `npm run`

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
### Setup test environment
### Run tests
### Expected results

## Component-level testing
### Setup test environment
### Run tests
### Expected results
