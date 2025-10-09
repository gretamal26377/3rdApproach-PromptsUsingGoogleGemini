# Backend-scoped Makefile to generate plain SQLAlchemy 2.0 models from the running DB service
# using sqlacodegen package, which is a bit different from Flask-SQLAlchemy models
# that the project is using, so review and changes are needed after generation
# Usage from backend/scripts:
# 	make generate-models-from-host (if you want to run from host repo, e.g. dev machine)
# 	make generate-models-from-container (if you want to run inside the container, e.g. CI/CD)

# Env Vars you can override defaults:
#   SERVICE - docker-compose service to use (default: backend-admin)
#   OUT     - As this env var will be used by sqlacodegen inside the container, it should be an
#             output path relative to Dockerfile WORKDIR. So default is: ./app/shared/models_sql2orm_plainsqlalchemy2.py
#	OUT_HOST - As this env var will be used by sqlacodegen from the host repo, it should be an
#             output path relative to the host repo this Makefile context. So default is: ../app/shared/models_sql2orm_plainsqlalchemy2.py
#   COMPOSE_FILE - As this env var will always be used out of containers, it'll run in the host context,
#                  so the docker-compose.yml's path should be relative to this host Makefile context:
#                  default: ../../docker-compose.yml

SERVICE ?= backend-admin
COMPOSE_FILE ?= ../../docker-compose.yml

# .PHONY: is a special built-in target that tells Makefile 
# that the following targets aren't files
.PHONY: generate-models start-db generate-models-from-host

start-db:
	@echo "Ensuring db and $(SERVICE) are running (using $(COMPOSE_FILE))..."
	docker compose -f $(COMPOSE_FILE) up -d db $(SERVICE)

# generate models from inside the container (writes to path relative to WORKDIR in Dockerfile)
OUT ?= ./app/shared/models_sql2orm_plain-sqlalchemy2.py
generate-models-from-container: start-db
    # 2>/dev/null: 0 = stdin, 1 = stdout, 2 = stderr. Redirect stderr to /dev/null to avoid
    # error message if secret file doesn't exist
	@echo "Generating models inside container $(SERVICE) and writing to $(OUT)..."
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE) sh -lc '\
	  pw=$$(cat /run/secrets/mysql_db_user_password 2>/dev/null || echo $$MYSQL_PASSWORD_FILE); \
	  sqlacodegen "mysql+pymysql://$$MYSQL_USER:$${pw}@db:3306/$$MYSQL_DATABASE" --outfile $(OUT) \
	'
	@echo "Generated file written to $(OUT). Review and git add/commit as needed"

# generate models from host (writes to repo-relative path)
OUT_HOST ?= ../app/shared/models_sql2orm_plain-sqlalchemy2.py
generate-models-from-host:
	@echo "Generating models from host repo and writing to $(OUT_HOST)..."
	sh -lc '\
	  pw=$$(cat ../../database/secrets/mysql_db_user_password.txt 2>/dev/null || echo $$MYSQL_PASSWORD_FILE); \
	  sqlacodegen "mysql+pymysql://db_user:$${pw}@localhost:3306/marketplace_db" --outfile $(OUT_HOST) \
	'
	@echo "Generated file written to $(OUT_HOST). Review and git add/commit as needed"
