# Lola-sandbox

Sandbox for Lola project.  
This Python tool is used to validate and test the run of scenario/algorithm of the LOLA project. It is a kind of replication of the lola web application.  

[[_TOC_]]

# Requirements

This program works only on Linux 64bits and MacOS (not tested). Nextflow does not work with full capabilities on Windows system's.

- python >= 3.10 (used for the sandbox)
- pip >= 22.0 (to install python dependencies. See [Installation](#installation) to set-up python environment)
- nextflow >= 22.04 (see [Nextflow - Installation](https://www.nextflow.io/index.html#GetStarted))
- docker >= 20.10.18 (see [Docker - installation](https://docs.docker.com/get-docker/))
- Trax server or any LRS with distant or local server that follow the LRS requirements. (See [Set up a local LRS](#set-up-a-local-lrs))

# Installation

## From sources
**Note:** A python environment _is recommanded_ (not required) for sandbox to avoid polluting base environment with dependencies. You can use [conda/miniconda](https://docs.conda.io/en/latest/miniconda.html) (see [installation conda](#installation-conda)) or  [venv](https://docs.python.org/3/tutorial/venv.html)

```sh 
$ cd /tmp
$ git clone git@gitlab.inria.fr:lola/lola-sandbox.git
$ cd lola-sandbox
$ conda create -y -n my_env python=3.10
$ conda activate my_env
$ python -m pip install .
```
Installation of dependencies :
```
$ pip install pandas
$ pip install scikit-learn
$ pip install surprise
$ pip install numpy==1.23.5
```
You can now check that you have the correct program (be careful, ubuntu has an other `sandbox` program): 

```sh
$ lola-sandbox --help
usage: lola-sandbox [-h] [-v] [--version] ...

Manage Sandbox environment for Lola Platform

positional arguments:
  {validate,run}  Command to run

options:
  -h, --help      show this help message and exit
  -v, --verbose   Increase verbosity
  --version       show program's version number and exit
  ```

# Guide how to use

This guide is a complete introduction on 'how to use the sandbox with [Recommandation](https://gitlab.inria.fr/lola/scenarios/recommandation) scenario'.

You must have a LRS to use the sandbox. See [requirements](#requirements)  
  
The first step is to download scenario, algorithms and docker images.  

1. **Create a working directory in your home space:**
    ```sh 
    $ mkdir -p $HOME/sandbox_wdir/{scenarios,algorithms,workdir}
    $ cd $HOME/sandbox_wdir
    ```
    - `scenarios`: will contain scenarios
    - `algorithms`: will contain algorithms
    - `workdir`: will contain scenarios run
    
2. **Download scenario Recommandation and algorithms and docker images**
    ```sh
    $ cd $HOME/sandbox_wdir/scenarios
    $ git clone git@gitlab.inria.fr:lola/scenarios/recommandation.git

    $ cd $HOME/sandbox_wdir/algorithms
    $ git clone git@gitlab.inria.fr:lola/algorithms/svdpp.git
    $ git clone git@gitlab.inria.fr:lola/algorithms/test-recommandation.git
    ```
    
    If you are on the Inria network (on site, or with VPN):
    ```sh 
    $ docker pull harbor.loria.fr/lola/recommandation:1.1.0_switchable 
    $ docker tag harbor.loria.fr/lola/recommandation:1.1.0_switchable recom:latest

    $ docker pull harbor.loria.fr/lola/svdpp_recom:latest
    $ docker tag harbor.loria.fr/lola/svdpp_recom:latest lola.lhs.loria.fr:4443/sisr_user/svdpp_recom:latest

    $ docker pull harbor.loria.fr/lola/test_recom:latest
    $ docker tag harbor.loria.fr/lola/test_recom:latest lola.lhs.loria.fr:4443/sisr_user/test_recom:latest
    ```
    
    In the previous commands, images were tagged to match the name used in `algo_recipe.json` (for algorithms) and `params.json` (for scenario).
    
3. **Install the lola-sandbox**

    See [Installation](#installation) (don't do it if you already did it!)

4. **Generate the config file for the sandbox**

    The config file contains information on "how to run the complete scenario". Create the file `recommandation_params.json` in `$HOME/sandbox_wdir`
    
    ```json
    {
      "scenario_path": "~/sandbox_wdir/scenarios/recommandation/",
      "scenario_parameters": {
        "fcp": "fcp",
        "mae": "mae",
        "mse": "mse",
        "rmse": "rmse",
        "datasetName": "oulad"
      },
      "algorithms": [
        {
          "algorithm_path": "~/sandbox_wdir/algorithms/svdpp/",
          "nf_variable": "userModel",
          "parameters": {
            "init_mean": "40",
            "init_std_dev": "1",
            "n_epochs": "20",
            "n_factors": "20",
            "lr_all": "0.007",
            "reg_all": "0.02"
          }
        },
        {
          "algorithm_path": "~/sandbox_wdir/algorithms/test-recommandation",
          "nf_variable": "userTest",
          "parameters": {}
        }
      ]
    }
    ```
    
5. Structure of the project

    After following this guide, you should have the next directory tree:
    
    ```sh 
    $ tree -L 2
    .
    ├── recommandation_params.json
    ├── algorithms
    │   ├── svdpp
    │   └── test-recommandation
    ├── scenarios
    │   └── recommandation
    └── workdir 
    ``` 
    
5. **Run the scenario**

    ```sh 
    $ lola-sandbox run --lrs-host http://localhost:80 -w workdir -C recommandation_params.json
    ```
If the sandbox program is not in your PATH, maybe you don't set-up correctly your PATH environment. Please refer to [installation conda](#installation-conda) or to your system to find the correct executable.

# Set up a local LRS

**Requirements for this setup :**
- curl

1. **Clone trax :**

    ``` sh
    $ git clone https://gitlab.inria.fr/lola/back-end/trax
    $ cd trax
    ```

2. **Create the environment file for the service.**

    ``` sh
    $ make env
    ```
    
    This command create a `.env` and a `.envrc` files at the root of the repository. This file contains all data required by the service to work. You can edit all parameters if you need.  
      
    **Note:** If you move the project (change directory), you have to remove the `.env` file and re-generate the `.env` file with `make env`.
    
3. **Build docker images or get Docker images from ~~Inria~~ Loria forge**

   You can build your own docker images for the service with:  

    ```sh
    $ make build 
    ```
    
    Or download images on the ~~Inria~~ Loria forge (note that you need a connection to the Inria VPN):

    ```sh
    $ docker pull harbor.loria.fr/lola/trax_admin:latest
    $ docker tag harbor.loria.fr/lola/trax_admin:latest trax_trax:latest

    $ docker pull harbor.loria.fr/lola/trax_client:latest
    $ docker tag harbor.loria.fr/lola/trax_admin:latest trax_client:latest
    ```
    
    - **trax_admin** or **trax_trax** : is the classic trax image used to upload and consult data.  
    - **trax_client** : is an image based on `trax_trax` but with an edition in its apache server that disable modification of the database. In fact, with `trax_client`, you can only see your data, not edit them. The web interface is also unavailable (login in web interface needs POST).  

4. **Run the service and setup for the first run**

    ```sh
    $ make up
    ```
    
    Now you can set up the first run:
    
    ```sh
    $ make trax_initdb
    $ make trax_create_client
    $ make trax_create_admin
    ```
    This initialisation the sql database. Next lines create account for the web interface (admin account) and for http client (client account).  
      
    Without editing configuration, your services should be available:
    
    ```sh
    $ make ps
    trax_db           docker-entrypoint.sh --def ...   Up      0.0.0.0:3306->3306/tcp,:::3306->3306/tcp, 33060/tcp
    trax_phpmyadmin   /docker-entrypoint.sh apac ...   Up      0.0.0.0:8080->80/tcp,:::8080->80/tcp
    trax_trax         docker-php-entrypoint apac ...   Up      443/tcp, 0.0.0.0:80->80/tcp
    ```
    
    You can now connect to http://localhost:80 and use your admin credential.
    
5. **Upload xapi data to the LRS.**

    If your xapi file is large (> 100Mo), split it in multiple files. Trax does not handle very well large files. In the following command, change the `my_xapi_file.xapi` with the name of your xapi file. 
        
    ```sh 
       $ curl --request POST localhost:80/trax/ws/xapi/statements --header 'X-Experience-API-Version: 1.0.3' --header 'Content-Type: application/json' --header 'Accept: application/json' -u testsuite:password --data "@my_xapi_file.xapi"
    ```
    
    At the end of the upload, you can check xapi data in the web interface at http://localhost:80 after connecting with your admin credential.

6. **Stop the service**
   
   ```sh
   $ make stop 
   ```
   
# Quick Installation of conda

Quick installation of conda on Linux x68 to manage Python environment.  
For more information on conda, see the official documentation [https://docs.conda.io](https://docs.conda.io) or [miniconda](https://docs.conda.io/en/latest/miniconda.html)  
**Note**: This tuto show the installation of miniconda instead of conda. Miniconda is just a lighter version of Conda.

``` sh
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
$HOME/miniconda/bin/conda init bash
echo auto_activate_base: false >> ~/.condarc
echo 'export PATH=$PATH:$HOME/miniconda/bin' >> ~/.bashrc
source ~/.bashrc
```

To create environment with python 3.10

``` sh
conda create -y -n my_env python=3.10
```

Each time you want to use your environment, use:

``` sh
conda activate my_env
```

# Create Binary from sources

This is specify for developpers. You can create a binary with pyinstaller to have a unique binary.  
1. Create a clean python environment (py-env, or miniconda ([installation conda](#quick-installation-of-conda)))
2. `pip install -r requirements.txt`
3. `pip install pyinstaller`
4. `pyinstaller --onefile --name=lola-sandbox sandbox/app.py`
5. ```bash
   ./dist/lola-sandbox --version
   "1.0.3"
   ```

# Using the Preconfigured Lola-Sandbox Virtual Machine (Ubuntu 24.04)

If you prefer to use a ready-to-use virtual machine instead of installing everything manually, you can download and set up the Lola-Sandbox VM using the following steps:
1. Install VirtualBox (>= Version 7.1.6)
Download and install VirtualBox from the official website: [🔗 VirtualBox](https://www.virtualbox.org/)
2. Download the VM Image
Run the following command to retrieve the virtual machine image from mbi-storage:
`scp sisr@mbi-storage:/export/sisr/archives/vm/sandbox-lola/sandbox.ova . `
3. Import the Image into VirtualBox :
Open VirtualBox
Go to File → Import Appliance
Select the sandbox.ova file
Follow the instructions to complete the import
4. Running the Sandbox
Open a terminal inside the VM and execute the following commands:
```
cd sandbox_wdir/trax
sudo make up
User password for vboxuser: changeme
sudo make ps
conda activate my_env
cd ..
lola-sandbox run --lrs-host http://localhost:80 -w workdir -C recommandation_params.json

```
5. Output
The output of the command will be a file named output.json, stored in:
📂 /home/vboxuser/sandbox_wdir/workdir/...