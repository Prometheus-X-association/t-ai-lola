# Introduction

This project sets up an xAPI Learning Record Store (LRS) using TRAX, loads OULAD dataset into it, and executes a LOLA Sandbox scenario for recommendation testing.

The system consists of:

1. Trax LRS – A Laravel-based Learning Record Store (LRS) for storing xAPI data
2. LOLA Sandbox – A scenario execution framework for recommendation algorithms
3. Docker & Makefile Automation – Automated setup and execution using Docker and Makefiles


# Requirements

This program works only on Linux 64bits and MacOS (not tested). Nextflow does not work with full capabilities on Windows system's.

- python >= 3.10 (used for the sandbox)
- pip >= 22.0 (to install python dependencies. See [Installation](#installation) to set-up python environment)
- nextflow >= 22.04 (see [Nextflow - Installation](https://www.nextflow.io/index.html#GetStarted))
- docker >= 20.10.18 (see [Docker - installation](https://docs.docker.com/get-docker/))

# Repository structure
```
/stage1-test
│── /data
│   ├── /trax                    # Contains TRAX LRS setup
│   │   ├── docker-compose.yml    # Docker configuration for TRAX
│   │   ├── Makefile              # Makefile for TRAX setup
│   ├── /dataJson                 # Directory for storing dataset files
│── /sandbox_wdir                 # LOLA Sandbox execution environment
│   ├── recommandation_params.json # Scenario configuration
│   ├── /scenarios                # Predefined LOLA scenarios
│   ├── /algorithms               # Recommendation algorithms
│   ├── /workdir                  # Stores execution results
│   ├── Makefile                  # Makefile for lola-sandbox setup
│── README.md                     # Documentation

```

# Installation & Setup

**Clone the repository**

```
git clone https://gitlab.inria.fr/okuksa/stage1-test.git
cd stage1-test
```

# Running instructions
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

### Lola-sanbox installation and scenario execution

**Note:**
- If Conda is detected, the system will automatically install dependencies inside a Conda environment
- If Conda is not installed, dependencies will be installed system-wide

```
cd /sandbox_wdir
make up
```
# Expected results

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

isit the specified directory (in our case `/home/lap/Documents/stage1/stage1-test/sandbox_wdir/workdir/Rc7a39c82-f0a5-4133-bc4d-3d3a055c059a/b8/214adb1fde548e5840f52071154514/output.json`) and view the results in the output.json folder