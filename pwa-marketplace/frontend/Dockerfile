# Notice: In Dockerfiles can't have inline comments, just above or below the code

###############################################
# 1️⃣ BUILD STAGE — Production build with full node + pnpm
###############################################
FROM node:20 AS build

# Enable corepack for pnpm
RUN corepack enable
# Following best practice to use a WORKDIR called /app
WORKDIR /app
# Copy workspace definition files first (cache-friendly)
COPY ./pnpm-workspace.yaml ./
COPY ./package.json ./
COPY ./pnpm-lock.yaml ./
# Copy ONLY package.json of shared-lib + customer (no source yet)
COPY ./shared-lib/package.json ./frontend/shared-lib/
COPY ./customer/package.json ./frontend/customer/
# Install deps for the whole workspace (only prod ones needed later)
RUN pnpm install --frozen-lockfile
# Now copy source files
COPY ./shared-lib ./frontend/shared-lib
COPY ./customer ./frontend/customer
# Build and bundle shared-lib to customer frontend (SSR-ready)
RUN pnpm --filter ./frontend/shared-lib build
RUN pnpm --filter ./frontend/customer build

###############################################
# 2️⃣ PRODUCTION RUNTIME STAGE — Optimised image with node-slim (SSR server)
###############################################
FROM node:20-slim AS server

# Create a non-root user
RUN groupadd -r deploygroup && useradd -r -g deploygroup deployuser
# Following best practice to use a WORKDIR called /app inside the deployment image/container
WORKDIR /app
# Add pnpm via corepack (safe for runtime)
RUN corepack enable




# Copy only built artifacts and minimal runtime dependencies
COPY --from=build /app/frontend/customer/dist ./dist
COPY --from=build /app/frontend/customer/package.json ./
COPY --from=build /app/pnpm-lock.yaml ./
# Install only production dependencies (SSR server only)
RUN pnpm install --prod --frozen-lockfile
# Run as non-root
USER nodejs
EXPOSE 3000
# Healthcheck for SSR server
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node ./dist/healthcheck.js || exit 1
CMD ["node", "dist/server.js"]










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
