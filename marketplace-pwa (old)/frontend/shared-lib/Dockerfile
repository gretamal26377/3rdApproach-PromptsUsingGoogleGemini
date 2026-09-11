# Use Node.js to build Storybook
FROM node:22-alpine AS build

# Remember this will run in a new and isolated container, so
# it doesn't matter if container folder doesn't match the host same path
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build-storybook

# Use Nginx to serve the static Storybook files
FROM nginx:alpine
COPY --from=build /app/storybook-static /usr/share/nginx/html
# Only for documentation purposes. To make port available
# it would typically use docker "run -p" or "docker-compose up"
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]