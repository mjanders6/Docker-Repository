#!/bin/bash

envsubst < /opt/minecraft/server/server.properties.template > /opt/minecraft/server/server.properties

# Print the resolved file
echo "==== FINAL server.properties ===="
cat /opt/minecraft/server/server.properties
echo "================================="

# Start Minecraft server
java -Xmx4096M -Xms2048M -jar server.jar nogui