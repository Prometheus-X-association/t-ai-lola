.DEFAULT_GOAL := help
.PHONY: all check-prereqs configure certs deploy clean status logs up help reset-db

DOCKER_GROUP_ID := $(shell which getent >/dev/null 2>&1 && getent group docker | cut -d: -f3)
ifeq ($(DOCKER_GROUP_ID),)
  DOCKER_GROUP := 0
else
  DOCKER_GROUP := $(DOCKER_GROUP_ID)
endif

help: ## Display available commands in this Makefile
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

up: deploy ## Alias for deploy target

check-prereqs: ## Verify required dependencies (docker, python3.12)
	@which python3.12 >/dev/null 2>&1 || (echo "you need to install docker or python3.12" && exit 1)
	@which docker >/dev/null 2>&1 || (echo "you need to install docker or python3.12" && exit 1)

configure: check-prereqs ## Generate local environment configuration files
	@python3.12 configure_local.py

certs: ## Generate SSL certificate keys
	@mkdir -p ../../app/lolapy/certs
	@if [ ! -f ../../app/lolapy/certs/private.key ]; then \
		openssl genpkey -algorithm RSA -out ../../app/lolapy/certs/private.key -pkeyopt rsa_keygen_bits:2048; \
	fi
	@if [ ! -f ../../app/lolapy/certs/certificate.crt ]; then \
		openssl req -new -x509 -key ../../app/lolapy/certs/private.key -out ../../app/lolapy/certs/certificate.crt -days 365 -subj "/CN=example.com"; \
	fi
	@mkdir -p certs
	@if [ ! -f certs/openssl.cnf ]; then \
		echo "[req]" > certs/openssl.cnf; \
		echo "distinguished_name = req_distinguished_name" >> certs/openssl.cnf; \
		echo "x509_extensions = v3_req" >> certs/openssl.cnf; \
		echo "prompt = no" >> certs/openssl.cnf; \
		echo "" >> certs/openssl.cnf; \
		echo "[req_distinguished_name]" >> certs/openssl.cnf; \
		echo "CN = localhost" >> certs/openssl.cnf; \
		echo "" >> certs/openssl.cnf; \
		echo "[v3_req]" >> certs/openssl.cnf; \
		echo "keyUsage = keyEncipherment, dataEncipherment" >> certs/openssl.cnf; \
		echo "extendedKeyUsage = serverAuth" >> certs/openssl.cnf; \
		echo "subjectAltName = @alt_names" >> certs/openssl.cnf; \
		echo "" >> certs/openssl.cnf; \
		echo "[alt_names]" >> certs/openssl.cnf; \
		echo "DNS.1 = localhost" >> certs/openssl.cnf; \
		echo "IP.1 = 127.0.0.1" >> certs/openssl.cnf; \
	fi
	@if [ ! -f certs/domain.key ] || [ ! -f certs/domain.crt ]; then \
		openssl req -new -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/domain.key -out certs/domain.crt -config certs/openssl.cnf; \
		mkdir -p ~/.docker/certs.d/localhost:5001; \
		cp certs/domain.crt ~/.docker/certs.d/localhost:5001/ca.crt; \
	fi

deploy: configure certs ## Start the application and run migrations/fixtures
	@echo "Building backend and app images..."
	DOCKER_GROUP=$(DOCKER_GROUP) docker compose -f docker-compose.local.yml build backend app
	@echo "Starting all containers..."
	DOCKER_GROUP=$(DOCKER_GROUP) docker compose -f docker-compose.local.yml up -d
	@echo "Running container post-start configuration..."
	@SFTP_USER=$$(grep '^SFTP_USER=' ../../app/lolapy/.env | cut -d= -f2); \
	if [ ! -z "$$SFTP_USER" ]; then \
		docker exec local-sftp-1 chown -R $$SFTP_USER /home/$$SFTP_USER/upload 2>/dev/null || true; \
	fi
	@docker exec -u root local-hueyconsumer-1 chown -R lolauser /tmp/certs 2>/dev/null || true
	@docker exec -u root local-hueyconsumer-1 chown -R lolauser /tmp/lolauser 2>/dev/null || true
	@echo "Restarting hueyconsumer..."
	DOCKER_GROUP=$(DOCKER_GROUP) docker compose -f docker-compose.local.yml restart hueyconsumer
	@echo "Waiting for MySQL database to be ready..."
	@MYSQL_ROOT_PASSWORD=$$(grep '^MYSQL_ROOT_PASSWORD=' ../../app/lolapy/.env | cut -d= -f2); \
	for i in {1..30}; do \
		if docker exec local-db-1 mysqladmin ping -uroot -p"$$MYSQL_ROOT_PASSWORD" --silent >/dev/null 2>&1; then \
			echo "Database is ready!"; \
			break; \
		fi; \
		echo "Database not ready yet, waiting..."; \
		sleep 2; \
	done
	@echo "Waiting 10 seconds for database to be ready..."
	sleep 10
	@echo "Deployment complete! Application is running locally."
	@echo ""
	@echo "================================================================="
	@echo "🔑 GENERATED SSL CERTIFICATE: Needs to be copied to lola_toolbox/src/crypto.py"
	@echo "================================================================="
	@cat ../../app/lolapy/certs/certificate.crt
	@echo "================================================================="
	@echo ""
	@echo "================================================================="
	@echo "📂 SFTP CONNECTION CONFIGURATION: Needed at lola_toolbox/src/connection.py"
	@echo "================================================================="
	@SFTP_USER=$$(grep '^SFTP_USER=' ../../app/lolapy/.env | cut -d= -f2); \
	SFTP_PASS=$$(grep '^SFTP_PASSWORD=' ../../app/lolapy/.env | cut -d= -f2); \
	echo "  Host:      localhost"; \
	echo "  Port:      2222"; \
	echo "  Username:  $$SFTP_USER"; \
	echo "  Password:  $$SFTP_PASS"
	@echo "================================================================="
	@echo ""

clean: ## Stop all containers and clean generated configurations
	@echo "Stopping and cleaning up containers..."
	DOCKER_GROUP=$(DOCKER_GROUP) docker compose -f docker-compose.local.yml down -v || true
	@sudo rm -f ../../app/lolapy/.env ../../app/frontend/.env ../../app/frontend/build/app/.env .env
	@sudo rm -rf ../../app/lolapy/certs
	@sudo rm -rf /tmp/lolauser
	@sudo rm -rf auth
	@sudo rm -rf certs
	@echo "Cleanup complete."

status: ## Display status of running containers
	DOCKER_GROUP=$(DOCKER_GROUP) docker compose -f docker-compose.local.yml ps

logs: ## Tail logs of running containers
	DOCKER_GROUP=$(DOCKER_GROUP) docker compose -f docker-compose.local.yml logs -f

reset-db: ## Drop, recreate database schema and load fixtures 
	@echo "Running database migrations and fixtures inside app container..."
	docker compose -f docker-compose.local.yml exec -T app bin/console doctrine:database:drop --force --if-exists
	docker compose -f docker-compose.local.yml exec -T app bin/console doctrine:database:create
	docker compose -f docker-compose.local.yml exec -T app bin/console doctrine:schema:create
	docker compose -f docker-compose.local.yml exec -T app bin/console doctrine:fixtures:load --group=ProdFixtures --no-interaction
	docker compose -f docker-compose.local.yml exec -T app rm -rf var/cache/prod
	docker compose -f docker-compose.local.yml exec -T app chown -R www-data:www-data var/cache
	docker compose -f docker-compose.local.yml exec -u www-data -T app bin/console cache:clear --env=prod --no-debug
	docker compose -f docker-compose.local.yml exec -u www-data -T app bin/console cache:warmup --env=prod --no-debug
