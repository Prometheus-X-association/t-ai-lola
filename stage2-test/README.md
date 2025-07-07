# Introduction

The project **stage2-test** consists of two main components: 

- Trax LRS: A Laravel-based Learning Record Store (LRS) that manages and stores xAPI data.

In this stage, the dataset is not included within the distribution.
Therefore, the process involves three steps:

-- Activate the exchange between the data provider and our data connector provided by the Promotheus-X consortium.
The data connector is located to a privtae server located at *http://lola.ovh*

-- Import the data locally

-- and then finally Install and feed the LRS TRAX

- LOLA Sandbox: A framework for executing scenarios to test Machine learning models for resource recommendation within a virtual learning environment. The OULAD dataset is used (see [OULAD-Documentation](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset))

The project leverages Docker and Makefile automation to streamline setup and operations,
ensuring a reproducible environment across different systems (Ubuntu and MacOS).Docker encapsulates all dependencies within containers, simplifying management and deployment, while Makefiles automate repetitive tasks such as building, running, and testing the application. 



# Requirements

This program is compatible with Linux 64-bit and MacOS systems. Please note that while the program can operate on Windows, Nextflow may not function with full capabilities on Windows environments (not recommanded).

The project requires the following software to be installed before installing Trax-LRS and lola-sandbox : 

- Nextflow (>= 22.04): Essential for workflow management. Installation details can be found on the Nextflow website (see [Nextflow - Installation](https://www.nextflow.io/index.html#GetStarted)).
-  Docker (>= 20.10.18): Necessary for containerization. Installation instructions are available on the Docker website ((see [Docker - installation](https://docs.docker.com/get-docker/))).
- make to execute Makefile scripts (see [build-essential install on Ubuntu](https://stackoverflow.com/questions/11934997/how-to-install-make-in-ubuntu) )

# Installation & Setup

**Clone the repository**

```
git clone git@github.com:Prometheus-X-association/t-ai-lola.git
cd t-ai-lola/stage2-test
```

# Running instructions

Before proceeding, ensure that the Docker daemon is active.

## 1. LRS settings

### Configuration

All the configuration parameters are set in the *data/.env* file.
You just need to edit this file and set optiosn parameters:

```
#if True, activate the exchange between data provider and LOLA's pdc-connector
#else use the last available dataset 
EXCHANGE_MODE=False 

# if True, get dataset from http://lola.ovh:8081
# else keep the last imported dataset
IMPORT_MODE=True 

# if True, transfer the statements included in the dataset to the LRS
FEED_MODE=True
```

### Install everything in appropriate containers

Run the following command in the project directory (t-ai-lola/stage2-test) : 

```
cd data
make up
```

### get the dataset through the data-connector

```
make import
make test
```

## 2. Lola-sandbox setup
Run the following command in the project directory (t-ai-lola/stage1-test):
```
cd sandbox
make up
```
# Expected results

If the installation proceeds successfully, you should see output similar to the following, at the end of installation, in your terminal:

```
N E X T F L O W  ~  version 22.10.4
Launching `../stage1-test/sandbox_wdir/scenarios/recommandation/main.nf` [Rc4f80af3-7ad9-452c-ae60-824297a8c6ba] DSL2 - revision: e75d58603e
executor >  local (8)
[89/8388b4] process > requestData     [100%] 1 of 1 ✔
[23/7a317b] process > svd_train       [100%] 1 of 1 ✔
[96/e6d1cd] process > svd_test (1)    [100%] 1 of 1 ✔
[f9/3f74bb] process > svd_eval (1)    [100%] 1 of 1 ✔
[fc/891bac] process > userModel       [100%] 1 of 1 ✔
[be/70218c] process > userTest (1)    [100%] 1 of 1 ✔
[a5/c6bc6b] process > userEval (1)    [100%] 1 of 1 ✔
[cd/ff9f09] process > mergeResProcess [100%] 1 of 1 ✔

INFO:Results and data of the run stored in '../stage1-test/sandbox_wdir/workdir/Rc4f80af3-7ad9-452c-ae60-824297a8c6ba'
2025-03-18 14:49:13,455:INFO:Result files should be in :
2025-03-18 14:49:13,456:INFO:  ../stage1-test/sandbox_wdir/workdir/Rc4f80af3-7ad9-452c-ae60-824297a8c6ba/cd/ff9f09205fb71caaf8b7756f7f3ac7/output.json

```
The output from the execution scenario, which includes a file containing precision indicators (json file) used to evaluate the performance of the machine learning recommendation models, is generated in the final process called **mergeResProcess**. 

To access this file, navigate to stage1-test/sandbox_wdir/workdir/ and look for the file named after the ID of your process. For instance, in this example, the file is named **cd**.

For additional details on the recommendation scenario, please check this ((see [Documentation](https://github.com/Prometheus-X-association/t-ai-lola/blob/main/stage2-test/sandbox_wdir/scenarios/recommandation/README.md))).
