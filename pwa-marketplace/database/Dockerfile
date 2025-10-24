FROM mysql:8.0
# Replace with your specific image digest if you want to ensure exact version
# FROM mysql@sha256:18dee92bbc23147cf0917a26b079c7b659e1170bd03f2ccc42b91236a02fa34b

# Using secret management in docker-compose.yml instead of 
# hardcoding the password here, so commenting this out
#ENV MYSQL_ROOT_PASSWORD=root
#ENV MYSQL_DATABASE=marketplace_db

# /docker-entrypoint-initdb.d/: is a special dir in the official
# MySQL Docker image. Any .sql, .sql.gz, or .sh files placed here
# will be executed at container 1st start
COPY ./docker-entrypoint-initdb.d/init.sql /docker-entrypoint-initdb.d/