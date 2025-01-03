#!/bin/bash

# Create a named pipe:
mkfifo /tmp/minecraft-pipe

# Start Minecraft server
cat /tmp/minecraft-pipe | java -Xmx1024M -Xms1024M -jar server.jar nogui
