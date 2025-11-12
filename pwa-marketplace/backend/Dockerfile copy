FROM python:3.9-slim-buster

# This is default ARG if it's not set in docker-compose.yml.
# If Dockerfile is run directly, it will use "customer" as default ARG
# Notice: In Dockerfile(s) can't have inline comments, just above or below the code
# ARG: var definition available at build-time (for docker build)
ARG BACKEND_TYPE=customer
# ENV: var definition available at runtime (for Docker run)
# You need both to pass the value from build-time into the running container
ENV BACKEND_TYPE=${BACKEND_TYPE}

ENV PYTHONDONTWRITEBYTECODE=1
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

# Copy source
COPY . .

# Ensure entrypoint script is present and executable. The entrypoint is expected
# to build DATABASE_URL from secrets and then exec the supplied CMD (or overridden
# if it's run from docker-compose and it has command: directive)
COPY ./entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Entrypoint builds runtime secrets/ENV (DATABASE_URL) and then execs the CMD
ENTRYPOINT ["./entrypoint.sh"]

# Default command: run the customer WSGI app with gunicorn so the image can be run
# directly. docker-compose services will override this CMD to point to the admin
# WSGI app when needed
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:5000", "app.customer.wsgi:app"]
