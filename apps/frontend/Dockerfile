FROM node:22-alpine AS base
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# Deployment Module hardening: run as a non-root user (node images ship a
# built-in unprivileged "node" user).
RUN chown -R node:node /app
USER node

EXPOSE 3000
CMD ["npm", "start"]
