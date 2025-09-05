FROM mysql:8.0

# Using secret management in docker-compose.yml instead of 
# hardcoding the password here, so commenting this out
#ENV MYSQL_ROOT_PASSWORD=root
#ENV MYSQL_DATABASE=marketplace_db

# /docker-entrypoint-initdb.d/: is a special dir in the official
# MySQL Docker image. Any .sql, .sql.gz, or .sh files placed here
# will be executed at container 1st start
COPY ./docker-entrypoint-initdb.d/init.sql /docker-entrypoint-initdb.d/