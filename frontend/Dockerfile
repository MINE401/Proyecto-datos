# Multi-stage Dockerfile optimized for OpenShift using Red Hat UBI images
# Stage 1: Build React app with Vite on UBI Node.js 22
FROM registry.access.redhat.com/ubi9/nodejs-22 AS build
WORKDIR /opt/app-root/src

# Install dependencies
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm ci --no-audit --no-fund

# Copy source and build
COPY . .
# Allow passing Supabase config at build time so Vite can inline it
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_API_BASE
ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

# Stage 2: Serve static files with UBI NGINX 1.20 (non-root, port 8080)
FROM registry.access.redhat.com/ubi9/nginx-120 AS runner

# Copy custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets to default app root (served by NGINX)
COPY --from=build /opt/app-root/src/dist /opt/app-root/src

# Ensure directories exist and are writable by arbitrary UID
RUN mkdir -p /opt/app-root/src/logs /opt/app-root/src/tmp \
  && chmod -R g=u /opt/app-root/src

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8080/ || exit 1

# Override S2I entrypoint to run nginx directly in runtime
CMD ["nginx", "-g", "daemon off;"]
