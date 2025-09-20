# Use Node.js as the base image for serving static files
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy the frontend files
COPY . .

# Install http-server globally
RUN npm install -g http-server

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Start http-server
CMD ["http-server", "-p", "8080", "-a", "0.0.0.0"]
