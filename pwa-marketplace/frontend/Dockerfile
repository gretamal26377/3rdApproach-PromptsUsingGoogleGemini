# Notice: In Dockerfiles can't have inline comments, just above or below the code

###############################################
# 1️⃣ BUILD STAGE — Production build with full node + pnpm
###############################################
FROM node:20 AS build

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm --activate

# Following best practice to use a WORKDIR called /app
WORKDIR /app

# Copy workspace definition files first (cache-friendly)
# These are the main definition files placed at context root that when pnpm install is executed
# will install all dependencies for both frontends and shared-lib declared in respective package.json files
COPY ./pnpm-workspace.yaml ./
COPY ./package.json ./
COPY ./pnpm-lock.yaml ./

# Copy ONLY package.json of shared-lib + customer (no source yet)
COPY ./shared-lib/package.json ./shared-lib/
# This is default ARG if it's not set in docker-compose.yml.
# If Dockerfile is run directly, it will use "customer" as default ARG
ARG APP_TYPE=customer
COPY ./${APP_TYPE}/package.json ./${APP_TYPE}/

# Only for debugging purposes, list the files in the current WORKDIR
# RUN ls -l && ls -l admin && ls -l customer && ls -l shared-lib

# Install deps for the whole workspace (only prod ones needed later)
RUN pnpm install --frozen-lockfile

# Now copy source files
COPY ./shared-lib ./shared-lib

# (GRL: This must be reviewed again)
# Copy the rest of app's source code from docker-compose build context folder as starting point/path
# to defined WORKDIR inside the container as destination path uses relative path ("./")
# Despite Admin and Customer Frontends run in different containers, it's needed to copy
# both Frontends (Admins + Customer) to each container, because main package.json at context root folder declares
# both, if only relevant Frontend + shared-lib source code are copied the missing one
# declared in main package.json will cause npm install to fail, as it will try to install it.
# This was best solution advised by vsCode Copilot (there're others but more error prone)
COPY ./${APP_TYPE} ./${APP_TYPE}

# Build and bundle shared-lib to SSR customer frontend app
RUN pnpm --filter ./shared-lib build
RUN pnpm --filter ./${APP_TYPE} build

# Remove dev deps listed in package.json devDependencies, keep production modules only (so node_modules contains prod deps)
RUN pnpm prune --prod

###############################################
# 2️⃣ PRODUCTION RUNTIME STAGE — Optimised image with node-slim
###############################################
FROM node:20-slim AS server

# Create a non-root user
RUN groupadd -r deploygroup && useradd -r -g deploygroup deployuser

# Following best practice to use a WORKDIR called /app inside the deployment image/container
WORKDIR /app

# Add pnpm via corepack (safe for runtime)
# RUN corepack enable

ARG APP_TYPE=customer
# Copy only built artifacts and minimal runtime dependencies (client + server bundles)
COPY --from=build /app/${APP_TYPE}/dist ./dist
# (Optional) If your server entry is a separate file at root of customer build, copy it: (# issue?: Not sure if needed)
COPY --from=build /app/${APP_TYPE}/server.js ./${APP_TYPE}/server.js
# Copy production node_modules from build stage (pruned to prod only)
COPY --from=build /app/node_modules ./node_modules
# Copy package manifest + lockfile into runtime (useful for reproducibility & runtime metadata)
COPY --from=build /app/${APP_TYPE}/package.json ./
COPY --from=build /app/pnpm-lock.yaml ./

# Install only production dependencies (commented out because we already copied pruned node_modules)
# RUN pnpm install --prod --frozen-lockfile

# Ensure permissions to non-root user
RUN chown -R deployuser:deployuser /app
# Run as non-root
USER deployuser

# Only for documentation purposes, docker-compose.yml will really define/set the port where the container to listen to
EXPOSE 3000

# Healthcheck for SSR server (Commented out because we haven't created healthcheck.js yet)
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#    CMD node ./dist/healthcheck.js || exit 1

RUN echo "APP_TYPE is $APP_TYPE"
# Start the SSR server (adjust path if your SSR server entry differs)
# CMD ["node", "dist/server.js"]
CMD ["sh", "-c", "if [ \"$APP_TYPE\" = \"customer\" ]; then node ./dist/server.js; else npm start; fi"]
