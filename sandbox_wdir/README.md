# LOLA Sandbox: Scenario Execution and Algorithm Testing

## Overview

LOLA Sandbox is a framework for executing and evaluating AI recommendation algorithms. 

It allows users to integrate their own algorithms, test them on datasets, and compare results with existing models.

The LOLA Sandbox consists of:
- scenarios - predefined structured environments for testing recommendation algorithms
- algorithms - implemented AI models used for recommendation tasks
- execution framework -a llows running, monitoring, and evaluating the performance of different algorithms

To use the sandbox effectively, Trax LRS must be set up first, as the scenario execution relies on stored data.

## Repository structure

```
/sandbox_wdir
│── recommandation_params.json  # Scenario configuration
│── /scenarios                  # Predefined LOLA scenarios
│    ├── /recommandation        # Main scenario for recommendation testing
│    │   ├── main.nf            # Scenario execution pipeline
│    │   ├── bin/               # Scenario-related execution scripts
│    │   ├── input/             # Expected input formats
│── /algorithms                 # Recommendation algorithms
│    ├── svdpp/                 # Predefined SVD++ algorithm for reference
│    │   ├── svdpp_train.py     # Training script
│    │   ├── svdpp_test.py      # Testing script
│    │   ├── Dockerfile         # Optional Docker environment for SVD++
│    ├── test-recommandation/   # Example user-defined test algorithm
│    │   ├── model_test.py      # Execution script for user-defined algorithm
│    │   ├── Dockerfile         # Optional Docker environment
│── /workdir                    # Stores execution results
│── Makefile                    # Automates setup and execution
│── README.md                   # Documentation
```

## Installation & Setup

Before executing the sandbox, make sure Trax LRS is running. If not, refer to [TRAX LRS Installation Guide](https://gitlab.inria.fr/okuksa/stage1-test/-/blob/main/data/trax/README.md?ref_type=heads).

**1. Setting up the environment**

**Note: ** A python environment is recommanded (not required) for sandbox to avoid polluting base environment with dependencies. You can use conda/miniconda or venv

**Conda environment installation**

Quick installation of conda on Linux x68 to manage Python environment. For more information on conda, see the official documentation https://docs.conda.io or miniconda **Note: ** This tuto show the installation of miniconda instead of conda. Miniconda is just a lighter version of Conda.
```
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
$HOME/miniconda/bin/conda init bash
echo auto_activate_base: false >> ~/.condarc
echo 'export PATH=$PATH:$HOME/miniconda/bin' >> ~/.bashrc
source ~/.bashrc
```
Once the environment is set up, you can execute a predefined scenario.

Note:
- If Conda is detected, the system will automatically install dependencies inside a Conda environment
- If Conda is not installed, dependencies will be installed system-wide

```
cd sandbox_wdir
make up
```

This command:
- ensures all dependencies are installed
- install lola-sandbox
- runs the recommandation scenario with the available algorithms.
- saves the results in /sandbox_wdir/workdir.

To verify:
```
lola-sandbox --help
``` 
If the command works, LOLA is successfully installed.

**2. Running a scenario**

If you've already install everything and want just to execute scenario, **DO NOT USE** `make up`, instead:

```
make run_sandbox

```
This will: 
- retrieve data from TRAX LRS
- execute the recommendation model
- generate evaluation metrics

Check results in `sandbox_wdir/workdir/created_folder/output.json`

## Algorithm structure

Each algorithm is located inside `/sandbox_wdir/algorithms`

Example:
```
/sandbox_wdir/algorithms/svdpp
│── svd_train.py   # Training script
│── svd_test.py    # Testing script
│── svd_eval.py    # Evaluation script
│── config.json    # Algorithm configuration
```

To use a custom algorithm, create a new folder in /algorithms, then modify `recommandation_params.json` to include it.

### Example: Running SVD++ Algorithm

Ensure svdpp exists inside /sandbox_wdir/algorithms

**Modify recommandation_params.json:**
```
{
  "scenario_path": "scenarios/recommandation",
  "algorithms": [
    {
      "algorithm_path": "algorithms/svdpp",
      "parameters": {
        "n_factors": 20,
        "n_epochs": 20,
        "init_mean": 40,
        "init_std_dev": 1,
        "lr_all": "0.007",
        "reg_all": "0.02"
      }
    }
  ]
}
```
**Run the scenario:**

``` 
make run_sandbox
```


## Algorithm Development

### Writing a new algorithm

Users can add new algorithms by creating a new folder inside sandbox_wdir/algorithms/ and implementing the necessary scripts.

**Expected input & output** you can check
- input: a CSV file containing xAPI interaction data from Trax LRS

Example, test_data.csv

```
actor,item,num_click
mailto:2457256@open.ac.uk,http://open.ac.uk/546662,0.05078125
mailto:2412002@open.ac.uk,http://open.ac.uk/546650,0.0
mailto:2691206@open.ac.uk,http://open.ac.uk/546986,0.0

```


- output: a prediction file with recommended actions for each user
Example, output.json

```
{ 
    "svd": [
        {"RMSE": [0.06943950099602435]}, 
        {"FCP": [0.3460093287769326]}, 
        {"MAE": [0.03749568605698269]}, 
        {"MSE": [0.004821844298576866]}
    ]
}
```

**Adding an algorithm**

1. Create a new folder in `sandbox_wdir/algorithms/`

```
mkdir sandbox_wdir/algorithms/my_algorithm
```

2. Implement your model (my_model.py)
3. Modify recommandation_params.json

Add your algorithm configuration:
```
{
    "name": "MyAlgorithm",
    "description": "A test recommendation model",
    "command": "python3 my_model.py --input {{ INPUT_DATA }} --output {{ OUTPUT_DATA }}"
}
```

4. Run the scenario with your algorithm

```
make run_sandbox
```

## Troubleshooting
**1. No Data in Trax LRS**

Ensure you have uploaded the dataset:
```
cd data/trax
make upload_data
```

**2. Scenario Execution Fails**
Ensure Trax LRS is running:
```
docker ps  # Check if Trax containers are running
```

