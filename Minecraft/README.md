# Minecraft Server: Java Edition with Forge MOD Extension

# Build Instructions 
1. Create a .env file using the variables in the [Environment Variables](#environment-variables)
2. Set the [Variables](#makefile-variables) in the Makefile 
3. Run: `make build`
   - This will initialize the volumes if not already created
4. Run: `make start`

## Tutorial: Setting up a Java Edition Server
[Tutorial Link](https://minecraft.wiki/w/Tutorial:Setting_up_a_Java_Edition_server)

## MOD | Minecraft Forge
[Minecraft Forge Installer](https://files.minecraftforge.net/net/minecraftforge/forge/)

## Environment Variables
- GAME_MODE=creative
- SERVER_IP=
- RCON_PASSWORD=up-to-you

## Makefile Variables
- IMAGE_NAME=docker-hub-username/repository-name
- IMAGE_TAG=tag
- CONTAINER_NAME=minecraft

## Historical Projects
- [None MOD Minecraft](https://github.com/mjanders6/Docker-Repository/tree/main/Minecraft/Archive)
- [Python Minecraft Installer](https://github.com/mjanders6/Minecraft-Installer) - Please note that this is no longer being maintained. 
- [Docker Images](https://hub.docker.com/u/mjanders6)