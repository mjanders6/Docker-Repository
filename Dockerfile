# Use the official Ubuntu 22.04 image as the base
FROM ubuntu:22.04

# Set the working directory
WORKDIR /minecraft

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    curl \
    tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose the Minecraft server port
EXPOSE ${SERVER_PORT}

# Add a non-root user to run the Minecraft server
RUN useradd -m -s /bin/bash minecraft


# Set environment variables
ENV MINECRAFT_VERSION=1.21.4 \
    EULA=true \
    SERVER_PORT=25565

# Download and prepare Minecraft server
RUN wget -O server.jar https://launcher.mojang.com/v1/objects/$(curl -s https://launchermeta.mojang.com/mc/game/version_manifest.json | \
    jq -r ".versions[] | select(.id==\"${MINECRAFT_VERSION}\") | .url" | \
    xargs curl -s | jq -r '.downloads.server.url')

# Set permissions for the minecraft user
RUN chown -R minecraft:minecraft /minecraft

# Switch to the non-root user
USER minecraft

# Copy start script to container
COPY start.sh /minecraft/start.sh
COPY server.properties /minecraft/server.properties
#RUN chmod +x /minecraft/start.sh

# Automatically accept the EULA
RUN echo "eula=${EULA}" > /minecraft/eula.txt

# Set the default command to run the Minecraft server
CMD ["./start.sh"]
