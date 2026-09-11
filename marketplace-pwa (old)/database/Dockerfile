FROM mysql:8.0

#ENV MYSQL_ROOT_PASSWORD=root ## Using secret management in docker-compose.yml instead of hardcoding the password here
#ENV MYSQL_DATABASE=marketplace_db ## Defined in docker-compose.yml

# /docker-entrypoint-initdb.d/: is a special dir in the official MySQL Docker image. Any .sql, .sql.gz, or .sh files placed here will be executed at container 1st start
COPY init.sql /docker-entrypoint-initdb.d/