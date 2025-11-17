# Notice: In Dockerfiles can't have inline comments, just above or below the code

###############################################
# 1️⃣ BUILD STAGE — production build with full Node
###############################################
FROM node:20 AS build

# Build shared-lib
WORKDIR /pwa-marketplace/frontend/shared-lib
# Copy only package metadata to leverage caching
COPY ./shared-lib/package*.json ./
# Install deps (including devDependencies)
RUN npm ci
# Copy shared-lib
COPY ./shared-lib ./
# Build SSR bundle + client bundle
RUN npm run build







# Use the official Node.js ver 18 with Alpine lightweight Linux
FROM node:22-alpine

# This is default ARG if it's not set in docker-compose.yml.
# If Dockerfile is run directly, it will use "customer" as default ARG
ARG APP_TYPE=customer

# Set working directory to the project root in Docker image/container
WORKDIR /pwa-marketplace/frontend

# Copy shared-lib
COPY ./shared-lib ./shared-lib
# Copy the rest of app's source code from docker-compose build context folder
# to defined WORKDIR inside the container as destination path uses relative path ("./")
# Despite Admin and Customer Frontends run in different containers, it's needed to copy
# both Frontends to each container, because main package.json at context root declares
# both, if only relevant Frontend + shared-lib source code are copied the missing one
# declared in main package.json will cause npm install to fail, as it will try to install it.
# This was best solution advised by vsCode Copilot (there're others but more error prone)
COPY ./${APP_TYPE} ./${APP_TYPE}

# This is main package.json placed at context root that when run npm install
# will install all dependencies for both Frontends and shared-lib declared in
# respective package.json files
# COPY ./package*.json ./

# Install system dependencies
# RUN apk add python3 make g++
# RUN apk add --no-cache python3 make g++

# Only for debugging purposes, list the files in the current WORKDIR
# RUN ls -l && ls -l admin && ls -l customer && ls -l shared-lib

# Build shared-lib
WORKDIR /pwa-marketplace/frontend/shared-lib
RUN npm install
RUN npm run build

# Build selected Frontend app inside the container taking as path WORKDIR
WORKDIR /pwa-marketplace/frontend/${APP_TYPE}
# Alternative to npm install. ci: Means clean install, more suitable for CI/CD pipelines
# Install dependencies based on package-lock.json to ensure exact versions
# RUN npm ci
RUN npm install
RUN npm run build

# Only for documentation purposes, docker-compose.yml really will expose the port in the container
EXPOSE 3000

# Start the selected frontend app using as path latest WORKDIR setting
ARG APP_TYPE=customer
RUN echo "APP_TYPE is $APP_TYPE"
CMD ["sh", "-c", "if [ \"$APP_TYPE\" = \"customer\" ]; then node server.js; else npm start; fi"]
