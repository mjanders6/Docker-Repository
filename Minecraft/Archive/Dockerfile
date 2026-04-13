# Use the official Ubuntu 22.04 image as the base
FROM ubuntu:22.04

# Set environment variable to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    git \
    openjdk-25-jre-headless \
    wget \
    curl \
    gcc \
    tzdata \
    gettext-base \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add a non-root user to run the Minecraft server
RUN useradd -r -m -U -d /opt/minecraft -s /bin/bash minecraft
#RUN groupadd -g $HOST_GID minecraft && useradd -u $HOST_UID -g minecraft -s /bin/bash minecraft

# Switch to the non-root user
USER minecraft
# Set environment variables
ENV EULA=true \
    SERVER_PORT=25565

# Setup directories
RUN mkdir -p /opt/minecraft/backups /opt/minecraft/tools /opt/minecraft/server

# Install and setup mcrcon
RUN git clone https://github.com/Tiiffi/mcrcon.git /opt/minecraft/tools

# Set the working directory
WORKDIR /opt/minecraft/tools
RUN gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

# Expose the Minecraft server port
EXPOSE ${SERVER_PORT}

WORKDIR /opt/minecraft/server
# Download and prepare Minecraft server
RUN wget -O server.jar https://piston-data.mojang.com/v1/objects/97ccd4c0ed3f81bbb7bfacddd1090b0c56f9bc51/server.jar

# Copy start script to container
COPY ./config/start.sh /opt/minecraft/server/start.sh
COPY ./config/server.properties.template /opt/minecraft/server/server.properties.template

# Switch to root to mame the start.sh executable 
USER root

# Ensure we're working in the correct directory before chmod/chown
WORKDIR /opt/minecraft/server

RUN chmod +x /opt/minecraft/server/start.sh
RUN chown minecraft:minecraft start.sh
RUN chown minecraft:minecraft server.properties.template
RUN chown -R minecraft:minecraft .

USER minecraft

# Automatically accept the EULA
RUN echo "eula=${EULA}" > /opt/minecraft/server/eula.txt

# Set the default command to run the Minecraft server
WORKDIR /opt/minecraft/server

CMD ["./start.sh"]
