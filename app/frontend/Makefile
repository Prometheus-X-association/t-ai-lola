# set the ROOT_DIR var with an absolute path
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# The env file is shared between this Makefile and docker-compose
ENV_FILE=$(ROOT_DIR)/.env

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

help: ## Display available commands in Makefile
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## env file and direnv related goal ##
.envrc: .env # This target force a direnv allow if the .env file has changed
	@touch .envrc

## docker-compose commands ##
build: ## Build the instance
	@docker compose build --pull

ps: ## Display the state of the container
	@docker compose $@

start: ## Start the instance
	@docker compose $@
	@watch -g 'docker compose logs' > /dev/null 2>&1

stop: ## Stop the instance
	@docker compose $@

restart: ## Restart the instance
	@docker compose $@

logs: ## Access logs
	@docker compose $@

bash: ## Bash access to the container
	@$(INTERACTIVE) docker compose exec app bash

bashroot: ## Root bash access to the container
	@$(INTERACTIVE) docker compose exec --user root app bash

bashmysql: ## Connect to the the Mysql container
	@docker compose exec db bash

logsf: ## Access logs and follow them
	@docker compose logs -f

remove_dangling: ## Remove Docker dangling images
	@docker image prune -f


app_cleandb: ## delete databases files
	@rm -rf ./database/*

freshstart: app_cleandb ## Reset the instance !! DELETE DATABASE !!
	@docker compose down --rmi all --remove-orphans
	@docker compose rm -sfv

env_sf:  ## copy of the .env file for Symfony
	cp .env build/app/.env

up: .envrc ## First start-up
	@docker compose up -d
	@watch -g 'docker-compose logs' > /dev/null 2>&1

up_dev: env_sf .envrc ## Start dev-mode 
	@docker-compose -f docker-compose-dev.yml up -d 
	@docker-compose exec app yarn install
	@docker-compose exec app composer install
	@watch -g 'docker-compose logs' > /dev/null 2>&1

app_cli_symfony: ## launch command line Symfony bin/console
	@docker compose exec app bin/console $(ARGS)

app_cacheclear: ## cache:clear symfony
	@docker compose exec app bin/console cache:clear

app_update_db_force: ## update the database with doctrine command
	@docker compose exec app bin/console doctrine:schema:update --force --dump-sql

app_update_db: ## dump the database update with doctrine command
	@docker compose exec app bin/console doctrine:schema:update --dump-sql

app_db_fixture_dev: ## !! DELETE DATABASE + recreate database + load fixtures for dev environment
	@docker compose exec app bin/console doctrine:database:drop --force --if-exists
	@docker compose exec app bin/console doctrine:database:create
	@docker compose exec app bin/console doctrine:schema:create
	@docker compose exec app bin/console doctrine:fixtures:load --group=DevFixtures --no-interaction

app_db_fixture_prod: ## !! DELETE DATABASE + recreate database + load fixtures for prod environment
	@docker compose exec app bin/console doctrine:database:drop --force --if-exists
	@docker compose exec app bin/console doctrine:database:create
	@docker compose exec app bin/console doctrine:schema:create
	@docker compose exec app bin/console doctrine:fixtures:load --group=ProdFixtures --no-interaction
	@docker compose exec app rm -rf var/cache/prod
	@docker compose exec app chown -R www-data:www-data var/cache var/log
	@docker compose exec -u www-data app bin/console cache:clear --env=prod --no-debug
	@docker compose exec -u www-data app bin/console cache:warmup --env=prod --no-debug
