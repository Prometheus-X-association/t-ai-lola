ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

up_all: up_trax up_sandbox

up_trax:
	@echo "Starting Trax LRS..."
	@$(MAKE) -C $(ROOT_DIR)/data/trax up

up_sandbox:
	@echo "Starting Lola Sandbox..."
	@$(MAKE) -C $(ROOT_DIR)/sandbox_wdir up
