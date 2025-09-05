FROM python:3.9-slim-buster

# This is default ARG if it's not set in docker-compose.yml.
# If Dockerfile is run directly, it will use "customer" as default ARG
# Notice: In Dockerfile(s) can't have inline comments, just above or below the code
# ARG: var definition available at build-time (for docker build)
ARG BACKEND_TYPE=customer
# ENV: var definition available at runtime (for Docker run)
# You need both to pass the value from build-time into the running container
ENV BACKEND_TYPE=${BACKEND_TYPE}

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
WORKDIR /pwa-marketplace/backend

# COPY and ADD:
# Source Path (1st argument): Always relative to the build context, and is not affected by WORKDIR
# Build Context: Folder specified as context: in your docker-compose.yml or with docker build when Dockerfile is run directly
# Destination Path (2nd argument): Affected by WORKDIR if you use a relative path (stating with ./)
# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code and scripts
COPY ./app/shared ./app/shared
COPY ./scripts ./scripts

# Conditionally copy only the relevant backend folder
RUN if [ "$BACKEND_TYPE" = "admin" ]; then \
      cp -r ./app/admin ./app/admin && \
      echo 'FROM admin backend'; \
    elif [ "$BACKEND_TYPE" = "customer" ]; then \
      cp -r ./app/customer ./app/customer && \
      echo 'FROM customer backend'; \
    else \
      echo "Unknown BACKEND_TYPE: $BACKEND_TYPE" && exit 1; \
    fi

# Ensure scripts are executable
RUN chmod +x ./scripts/entrypoint.sh ./scripts/wait-for-it.sh

# Entrypoint builds runtime secrets/ENV (DATABASE_URL) and then execs the CMD
# (if CMD isn't overridden for docker-compose having a command: directive)
ENTRYPOINT ["./scripts/entrypoint.sh"]
    
# Set default CMD based on BACKEND_TYPE 
CMD ["/bin/sh", "-c", "if [ '$BACKEND_TYPE' = 'admin' ]; \
     then exec gunicorn --workers=3 --bind=0.0.0.0:5000 app.admin.wsgi:app; \
     else exec gunicorn --workers=3 --bind=0.0.0.0:5000 app.customer.wsgi:app; \
     fi"]
