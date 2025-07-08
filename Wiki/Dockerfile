# Dockerfile
FROM node:18-bullseye

# Set working directory
WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && apt-get clean

# Clone Wiki.js source code
RUN git clone https://github.com/requarks/wiki.git .

# Install dependencies
RUN yarn install --production

# Expose the Wiki.js default port
EXPOSE 3000

# Start Wiki.js
CMD ["node", "server"]
