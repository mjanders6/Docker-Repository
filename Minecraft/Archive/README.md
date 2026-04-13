# Minecraft Server: Java Edition  

# Build Instructions 
1. Create a .env file using the variables in the [Environment Variables](#environment-variables)
2. Set the [Variables](#makefile-variables) in the Makefile 
3. Run: $make build$
   - This will initialize the volumes if not already created
4. Run: $make start$

## Tutorial: Setting up a Java Edition Server
[Tutorial Link](https://minecraft.wiki/w/Tutorial:Setting_up_a_Java_Edition_server)

## Environment Variables
- GAME_MODE=creative
- SERVER_IP=
- RCON_PASSWORD=up-to-you

## Makefile Variables
IMAGE_NAME=docker-hub-username/repository-name
IMAGE_TAG=tag
CONTAINER_NAME=minecraft

## Historical Projects
- [None MOD Minecraft](https://github.com/mjanders6/Docker-Repository/tree/main/Minecraft/Archive)
- [Python Minecraft Installer](https://github.com/mjanders6/Minecraft-Installer) - Please note that this is no longer being maintained. 
- [Docker Images](https://hub.docker.com/u/mjanders6)

## Minecraft Jar Files: 
Get the server link at: [Java Edition Server Download](https://www.minecraft.net/en-us/download/server)

Current link to Minecraft Java jar file:
- [1.21.5](https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar)
- [1.21.6](https://piston-data.mojang.com/v1/objects/6e64dcabba3c01a7271b4fa6bd898483b794c59b/server.jar)
- [1.21.7](https://piston-data.mojang.com/v1/objects/05e4b48fbc01f0385adb74bcff9751d34552486c/server.jar)
- [1.21.8](https://piston-data.mojang.com/v1/objects/6bce4ef400e4efaa63a13d5e6f6b500be969ef81/server.jar)
- [1.21.10](https://piston-data.mojang.com/v1/objects/95495a7f485eedd84ce928cef5e223b757d2f764/server.jar)
- [1.21.11](https://piston-data.mojang.com/v1/objects/64bb6d763bed0a9f1d632ec347938594144943ed/server.jar)
- [1.26.1.2](https://piston-data.mojang.com/v1/objects/97ccd4c0ed3f81bbb7bfacddd1090b0c56f9bc51/server.jar)
