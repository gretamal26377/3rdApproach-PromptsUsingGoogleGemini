# Stage 1: Create base image with all common dependencies
FROM python:3.9-slim-buster AS base

# Prevents Python from writing .pyc files to disk (python compiled files inside
# __pycache__ folders). This is good practice in Docker containers,
# because containers are meant to be immutable and stateless.
# Python compiling is quick, so no having .pyc files impacts performance in negligible way
ENV PYTHONDONTWRITEBYTECODE=1
# Forces Python to output logs and print statements directly
# to terminal (stdout/stderr) without buffering
ENV PYTHONUNBUFFERED=1

# Notice: WORKDIR sets the default working folder in Docker image/container
# affecting only commands like RUN, CMD, and ENTRYPOINT
# Align WORKDIR with compose paths and application layout
# WORKDIR /pwa-marketplace/backend
WORKDIR /app

# COPY and ADD:
# Source Path (1st argument): Always relative to the build context, and is not affected by WORKDIR
# Build Context: Folder specified as context: in your docker-compose.yml or with docker build when Dockerfile is run directly
# Destination Path (2nd argument): Affected by WORKDIR if you use a relative path (stating with ./)
# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy shared code and scripts that are common to both backends, except the Search Engine implementation
COPY ./app/shared ./shared
COPY ./scripts /scripts

# Ensure scripts are executable
RUN chmod +x /scripts/entrypoint.sh /scripts/wait-for-it.sh

# Stage 2: Create a builder for the 'admin' backend
# FROM base AS builder-admin
# COPY ./app/admin ./app/admin

# Stage 3: Create a builder for the 'customer' backend
# FROM base AS builder-customer
# COPY ./app/customer ./app/customer

# Stage 4: Final image - select which builder to use based on the build argument
# This is default ARG if it's not set in docker-compose.yml.
# If Dockerfile is run directly, it will use "customer" as default ARG
# Notice: In Dockerfile(s) can't have inline comments, just above or below the code
# ARG: var definition available at build-time (for docker build)
ARG BACKEND_TYPE=customer
# Below line is equivalent to: COPY ./app/${BACKEND_TYPE} ./${BACKEND_TYPE}
# FROM builder-${BACKEND_TYPE} AS final
COPY ./app/${BACKEND_TYPE} ./${BACKEND_TYPE}

# ENV: var definition available at runtime (for Docker run)
# You need both to pass the value from build-time into the running container
ENV BACKEND_TYPE=${BACKEND_TYPE}

# Entrypoint builds runtime secrets/ENV (DATABASE_URL) and then execs the CMD
# (if CMD isn't overridden for docker-compose having a command: directive)
ENTRYPOINT ["/scripts/entrypoint.sh"]

# Set default CMD based on BACKEND_TYPE. Ports here correspond to container ports, not localhost ports 
CMD ["/bin/sh", "-c", "if [ '$BACKEND_TYPE' = 'org_admin' ]; \
     then exec gunicorn --workers=3 --bind=0.0.0.0:5000 app.org_admin.wsgi:app; \
     else if [ '$BACKEND_TYPE' = 'platform_admin' ]; \
     then exec gunicorn --workers=3 --bind=0.0.0.0:5000 app.platform_admin.wsgi:app; \
     else exec gunicorn --workers=3 --bind=0.0.0.0:5000 app.customer.wsgi:app; \
     fi"]
