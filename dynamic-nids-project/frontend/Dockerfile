# frontend/Dockerfile

# --- Stage 1: Build the React Application ---
FROM node:18-alpine AS build

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json for dependency installation
COPY package.json ./
COPY package-lock.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the React application for production
RUN npm run build

# --- Stage 2: Serve the Application using Nginx ---
FROM nginx:1.25-alpine

# Copy the built static assets from the 'build' stage to the Nginx server directory
COPY --from=build /app/build /usr/share/nginx/html

# Copy the custom Nginx configuration file
# This is critical for handling client-side routing in a React app
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to allow traffic to the Nginx server
EXPOSE 80

# The default command for the nginx image is to start the server.
# This command ensures it runs in the foreground, which is required by Docker.
CMD ["nginx", "-g", "daemon off;"]
