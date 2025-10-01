.PHONY: up down restart clean init logs help country-etl

help: ## Show this help
	@echo "Available commands:"
	@echo "  make up        - Start the database container"
	@echo "  make down      - Stop the database container"
	@echo "  make restart   - Restart the database container"
	@echo "  make clean     - Remove the database container and volume"
	@echo "  make init      - Initialize/reset the database"
	@echo "  make logs      - Show database logs"
	@echo "  make country-etl - Process raw country data and load into DB"

up: ## Start the database container
	docker-compose up -d

down: ## Stop the database container
	docker-compose down

restart: down up ## Restart the database container

clean: ## Remove the database container and volume
	docker-compose down -v
	rm -rf postgres_data

init: ## Initialize/reset the database
	@echo "Warning: This will reset all data. Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	make clean
	make up
	@echo "Waiting for database to start..."
	@sleep 10
	@echo "Database reset complete."

logs: ## Show database logs
	docker-compose logs -f postgres

# Include environment variables from .env
-include .env
export

country-etl: ## Process raw country metrics and load them into PostgreSQL
	.venv/Scripts/python.exe scripts/process_country_metrics.py
	.venv/Scripts/python.exe scripts/load_country_metrics.py
