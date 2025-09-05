# Backend-scoped Makefile to generate SQLAlchemy models from the running DB service
# Usage (from repository root or from backend/):
#   (from repo root) make -C backend generate-models
#   (from backend/) make generate-models
# Variables you can override:
#   SERVICE - docker-compose service to use (default: backend-admin)
#   OUT     - output path inside backend/ (default: app/shared/models.py)
#   COMPOSE_FILE - location of docker-compose.yml relative to this Makefile (default: ../docker-compose.yml)

SERVICE ?= backend-admin
OUT ?= app/shared/models.py
COMPOSE_FILE ?= ../docker-compose.yml

.PHONY: generate-models start-db

start-db:
	@echo "Ensuring db and $(SERVICE) are running (using $(COMPOSE_FILE))..."
	docker compose -f $(COMPOSE_FILE) up -d db $(SERVICE)

generate-models: start-db
	@echo "Generating models inside container $(SERVICE) and writing to $(OUT)..."
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE) sh -lc '\
	  pw=$$(cat /run/secrets/mysql_db_user_password 2>/dev/null || echo $$MYSQL_PASSWORD); \
	  sqlacodegen "mysql+pymysql://$$MYSQL_USER:$${pw}@db:3306/$$MYSQL_DATABASE" --outfile $(OUT) \
	'
	@echo "Generated file written to $(OUT). Review and git add/commit as needed"
