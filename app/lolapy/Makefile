help: ## Display available commands in Makefile
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

test_not_integration: ## Run tests for modules but not them marked with `integration` or `slow`
	@pytest --cov-report html:cov_html --cov=lolapy --show-capture=all -o log_cli=true -o log_cli_level="INFO" -m "not slow and not integration"

test_all: ## Run all tests
	@pytest --cov-report html:cov_html --cov=lolapy --show-capture=all -o log_cli=true -o log_cli_level="INFO"
