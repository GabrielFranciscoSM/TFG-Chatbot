# Stage 1: Build the React application
FROM node:22.14.0-alpine3.21 AS builder

WORKDIR /app

# Copy package files for dependency caching
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the frontend source
COPY frontend/ .

# Build arguments for API URL configuration
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

# Build the production bundle
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.27.4-alpine

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
