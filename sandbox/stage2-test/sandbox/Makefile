SHELL := /bin/bash  # Force Makefile to use Bash instead of sh
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
ENV_NAME = lola_env
PYTHON_VERSION = 3.10

# Check for Conda
CONDA_EXISTS := $(shell which conda || echo "")

# Run all processes
up: install_lola_sandbox setup_python_env run_sandbox

# Verify LOLA Sandbox is available locally
install_lola_sandbox:
	@echo "Checking for LOLA Sandbox..."
	@if [ ! -d "$(ROOT_DIR)/lola-sandbox" ]; then \
		echo "Error: LOLA Sandbox directory not found at $(ROOT_DIR)/lola-sandbox."; \
		echo "Please ensure the LOLA Sandbox is available locally at the correct location."; \
		exit 1; \
	else \
		echo "LOLA Sandbox found at $(ROOT_DIR)/lola-sandbox."; \
	fi

# Setup Python environment (with Conda if available, otherwise system-wide)
setup_python_env:
	@echo "Checking Python environment..."
	@if [ -n "$(CONDA_EXISTS)" ]; then \
		echo "Conda detected. Using Conda environment."; \
		source "$(shell conda info --base)/etc/profile.d/conda.sh" && \
		conda env list | grep -q $(ENV_NAME) || conda create -y -n $(ENV_NAME) python=$(PYTHON_VERSION); \
		echo "Activating Conda environment..."; \
		bash -c "source '$(shell conda info --base)/etc/profile.d/conda.sh' && conda activate $(ENV_NAME) && pip install -r $(ROOT_DIR)/lola-sandbox/requirements.txt"; \
		bash -c "source '$(shell conda info --base)/etc/profile.d/conda.sh' && conda activate $(ENV_NAME) && pip install pandas scikit-learn surprise numpy==1.23.5"; \
		bash -c "source '$(shell conda info --base)/etc/profile.d/conda.sh' && conda activate $(ENV_NAME) && pip install -e $(ROOT_DIR)/lola-sandbox"; \
	else \
		echo "Conda not found. Installing system-wide dependencies..."; \
		python3 -m ensurepip --default-pip || sudo apt-get install python3-pip; \
		pip3 install -r $(ROOT_DIR)/lola-sandbox/requirements.txt; \
		pip3 install pandas scikit-learn surprise numpy==1.23.5; \
		pip3 install -e $(ROOT_DIR)/lola-sandbox; \
	fi

# Run LOLA-Sandbox scenario
run_sandbox:
	@cd $(ROOT_DIR) && mkdir -p workdir
	@echo "Running lola-sandbox..."
	@if [ -n "$(CONDA_EXISTS)" ]; then \
		bash -c "source '$(shell conda info --base)/etc/profile.d/conda.sh' && conda activate $(ENV_NAME) && cd $(ROOT_DIR) && lola-sandbox run --lrs-host http://localhost:80 -w workdir -C recommandation_params.json"; \
	else \
		bash -c "cd $(ROOT_DIR) && lola-sandbox run --lrs-host http://localhost:80 -w workdir -C recommandation_params.json"; \
	fi