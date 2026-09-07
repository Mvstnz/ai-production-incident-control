FROM node:24.12.0-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY dashboard/package.json ./dashboard/package.json
RUN npm ci --ignore-scripts
COPY dashboard ./dashboard
RUN npm run build

FROM nginx:1.28.0-alpine
COPY dashboard/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dashboard/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD wget -q --spider http://127.0.0.1/ || exit 1
