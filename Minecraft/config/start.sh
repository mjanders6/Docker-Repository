#!/bin/bash

envsubst < /opt/minecraft/server/server.properties.template > /opt/minecraft/server/server.properties

# Start Minecraft server
java -Xmx4096M -Xms2048M -jar server.jar nogui