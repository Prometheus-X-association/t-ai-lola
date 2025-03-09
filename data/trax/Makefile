# set the ROOT_DIR var with an absolute path
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# The env file is shared between this Makefile and docker-compose
ENV_FILE=$(ROOT_DIR)/.env
# The env file is shared between this Makefile and docker-compose
ENV_TRAX_FILE=$(ROOT_DIR)/.env.trax

# The envrc file is synced with the env file and is usable by direnv
ENVRC_FILE=$(ROOT_DIR)/.envrc

# Read the env file, and source it inside this Makefile
ifeq (,$(wildcard $(ENV_FILE)))
$(shell echo ROOT_DIR=${ROOT_DIR} > $(ENV_FILE))
$(shell cat .env.sample >> $(ENV_FILE))
$(info    )
$(info      an .env file has been generated for you; check its content)
$(info    )
endif

# Read the env file, and source it inside this Makefile
ifeq (,$(wildcard $(ENV_TRAX_FILE)))
$(shell echo ROOT_DIR=${ROOT_DIR} > $(ENV_TRAX_FILE))
$(shell cat .env.trax.sample >> $(ENV_TRAX_FILE))
$(info    )
$(info      an .env.trax file has been generated for you; check its content)
$(info    )
endif

ifeq (,$(wildcard $(ENVRC_FILE)))
$(shell echo 'test -f $(ENV_FILE) && source <(sed -e "s/^[A-Z].*/export &/" $(ENV_FILE))' > $(ENVRC_FILE))
$(info      an .envrc file has been generated for you; leave it as it is)
endif

# Import the content of the env file within the execution context of this Makefile
include $(ENV_FILE)
export $(shell sed -e 's/=.*//' -e 's/^\#.*//' $(ENV_FILE))

ifndef DOCKER_COMPOSE_USER
export DOCKER_COMPOSE_USER=$(shell id -un)
export DOCKER_COMPOSE_GROUP=$(shell id -gn)
export DOCKER_COMPOSE_UID=$(shell id -u)
export DOCKER_COMPOSE_GID=$(shell id -g)
endif

.DEFAULT_GOAL := help
.PHONY: build help

OS=$(shell uname -s)

# OPEN launches the system command adapted to its parameter
ifeq ($(OS),Linux)
INTERACTIVE=
OPEN=xdg-open
ifndef DOCKER_COMPOSE_UID
export DOCKER_COMPOSE_UID=$(shell id -u)
export DOCKER_COMPOSE_GID=$(shell id -g)
endif
else ifeq ($(OS),Darwin)
INTERACTIVE=
OPEN=open
else ifeq ($(OS),CYGWIN_NT-10.0)
INTERACTIVE=winpty
OPEN=cmd /c start
else
INTERACTIVE=
OPEN=echo
endif

.DEFAULT_GOAL := help

up: create_trax## First start-up
	@$(MAKE) upload_data

create_trax: .envrc
	@$(MAKE) env
	@docker-compose up -d
	@sleep 10
	@$(MAKE) trax_initdb
	@$(MAKE) trax_create_client
	@$(MAKE) trax_create_admin

upload_data: ##  Trax 
	@docker-compose run --rm data_uploader

env: ## Build .env and .env.trax files
	@envsubst < .env > .env.tmp
	@mv .env.tmp .env
	@envsubst < .env.trax > .env.trax.tmp
	@mv .env.trax.tmp .env.trax

build: ## Build the instance
	@docker-compose build --pull

ps: ## Display the state of the container
	@docker-compose $@

start: ## Start the instance
	@docker-compose $@
	@watch -g 'docker-compose logs' > /dev/null 2>&1

stop: ## Stop the instance
	@docker-compose $@

restart: ## Restart the instance
	@docker-compose $@

logs: ## Access logs
	@docker-compose $@

bash: ## Bash access to the container
	@$(INTERACTIVE) docker-compose exec trax bash

bashroot: ## Root bash access to the container
	@$(INTERACTIVE) docker-compose exec --user root trax bash

bashmysql: ## Connect to the Mysql container
	@docker-compose exec db bash

logsf: ## Access logs and follow them
	@docker-compose logs -f

remove_dangling: ## Remove Docker dangling images
	@docker image prune -f

trax_cacheclear: ## clear cache of the Trax application
	@docker-compose exec -w /var/www/html/traxlrs/ trax php artisan cache:clear

trax_create_client: ## create a client
	@docker-compose exec -w /var/www/html/traxlrs/ trax php artisan client:create

trax_initdb: wait_for_db## init database
	@docker-compose exec -w /var/www/html/traxlrs/ trax php artisan migrate --force

trax_create_admin: ## create the admin user
	@docker-compose exec -w /var/www/html/traxlrs/ trax php artisan user:create-admin

app_cleandb: ## delete databases files
	@rm -rf ./database/*

freshstart: app_cleandb ## Reset the instance !! DELETE DATABASE !!
	@docker-compose down --rmi all --remove-orphans
	@docker-compose rm -sfv

trax_list_db: ## List databases in Mysql server
	@docker-compose exec -u root:root db /usr/bin/mysql --password=${MYSQL_ROOT_PASSWORD} --execute "SHOW DATABASES"

wait_for_db:
	@echo "Waiting for database to be ready..."
	@sleep 10
	@until docker exec trax_db mysqladmin ping -h"db" --silent; do \
		echo "Waiting for MySQL to start..."; \
		sleep 2; \
	done
	@echo "MySQL is ready!"