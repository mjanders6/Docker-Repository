# Use the official Ubuntu 22.04 image as the base
FROM ubuntu:22.04

# Set the working directory
WORKDIR /minecraft

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    wget \
    curl \
    tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose the Minecraft server port
EXPOSE ${SERVER_PORT}

# Add a non-root user to run the Minecraft server
RUN useradd -m -s /bin/bash minecraft


# Set environment variables
ENV EULA=true \
    SERVER_PORT=25565

# Download and prepare Minecraft server
RUN wget -O server.jar https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar

# Set permissions for the minecraft user
RUN chown -R minecraft:minecraft /minecraft

COPY broadcast.sh /minecraft/broadcast.sh
RUN chmod +x /minecraft/broadcast.sh

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
