# Use lightweight Node.js image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --only=production

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
