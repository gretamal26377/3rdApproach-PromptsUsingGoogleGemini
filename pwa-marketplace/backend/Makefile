# Backend-scoped Makefile to generate plain SQLAlchemy models from the running DB service
# using sqlacodegen package. Which is a little different from Flask-SQLAlchemy models
# that the project is using, so some changes are needed after generation
# Usage (from repository root or from backend/):
#   (from repo root) make -C backend generate-models
#   (from backend/) make generate-models
# Variables you can override:
#   SERVICE - docker-compose service to use (default: backend-admin)
#   OUT     - output path inside backend/ (default: app/shared/models.py)
#   COMPOSE_FILE - location of docker-compose.yml relative to this Makefile (default: ../docker-compose.yml)

SERVICE ?= backend-admin
OUT ?= app/shared/models_sql2orm_plainsqlalchemy2.py
COMPOSE_FILE ?= ../docker-compose.yml

# .PHONY: is a special built-in target that tells Makefile 
# that the following targets aren't files
.PHONY: generate-models start-db

start-db:
	@echo "Ensuring db and $(SERVICE) are running (using $(COMPOSE_FILE))..."
	docker compose -f $(COMPOSE_FILE) up -d db $(SERVICE)

# start-db is right there, it's a generate-models' dependency
generate-models: start-db
	@echo "Generating models inside container $(SERVICE) and writing to $(OUT)..."
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE) sh -lc '\
	  pw=$$(cat /run/secrets/mysql_db_user_password 2>/dev/null || echo $$MYSQL_PASSWORD_FILE); \
	  sqlacodegen "mysql+pymysql://$$MYSQL_USER:$${pw}@db:3306/$$MYSQL_DATABASE" --outfile $(OUT) \
	'
	@echo "Generated file written to $(OUT). Review and git add/commit as needed"
