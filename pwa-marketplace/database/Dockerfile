FROM mysql:8.0

#ENV MYSQL_ROOT_PASSWORD=root ## Using secret management in docker-compose.yml instead of hardcoding the password here, so commenting this out
#ENV MYSQL_DATABASE=marketplace_db ## Defined in docker-compose.yml, so commenting this out

# /docker-entrypoint-initdb.d/: is a special dir in the official MySQL Docker image. Any .sql, .sql.gz, or .sh files placed here will be executed at container 1st start
# We changed approach to mounting folder in docker-compose.yml, so commenting this out
# COPY init.sql /docker-entrypoint-initdb.d/