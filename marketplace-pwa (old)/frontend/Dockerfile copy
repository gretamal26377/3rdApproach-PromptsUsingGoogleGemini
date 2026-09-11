# Notice: In Dockerfiles can't have inline comments, just above or below the code
# Use the official Node.js ver 18 with Alpine lightweight Linux
FROM node:18-alpine

# This is default ARG if it's not set in docker-compose.yml.
# If Dockerfile is run directly, it will use "customer" as default ARG
ARG APP_TYPE=customer

WORKDIR /marketplace-pwa/frontend/src/${APP_TYPE}

COPY ./package*.json /marketplace-pwa/frontend/
# Ensure all dependencies in package.json copied inside the container in /marketplace-pwa/frontend/
# are installed in the container in /marketplace-pwa/frontend/
RUN npm install --prefix /marketplace-pwa/frontend/
# Copy the rest of the frontend source code into the container using the current build context
# Build Context: Folder specified as context: in your docker-compose.yml or with docker build when Dockerfile is run directly
COPY . /marketplace-pwa/frontend/

# Build only the selected frontend
RUN npm run build --prefix /marketplace-pwa/frontend/src/${APP_TYPE}

# Only for documentation purposes, docker-compose.yml really will expose the port in the container
EXPOSE 3000
# Start the selected frontend app
CMD ["npm", "start", "--prefix", "/marketplace-pwa/frontend/src/${APP_TYPE}"]