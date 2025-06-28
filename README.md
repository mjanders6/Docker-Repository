# Purpose 
This Repository is to manage home lab Docker files and compose files

## Kali 
- sudo nvidia-ctk runtime configure --runtime=docker --set-as-default
- sudo service docker restart

## Minecraft
### Link to initial project for hard python installer: [Minecraft-Installer](https://github.com/mjanders6/Minecraft-Installer)

### Docker Image
This is the Docker image I created to run on my Raspberry Pi 4/5 is hosted at [mjanders6/minecraft](https://hub.docker.com/repository/docker/mjanders6/minecraft/general). The Dockerfile is included in the Minecraft repository if a custom image is needed. 

### Minecraft Jar Files: 
Get the server link at: [Java Edition server](https://www.minecraft.net/en-us/download/server)

Current link to MInecraft Java jar file:
- [1.21.5](https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar)
- [1.21.6](https://piston-data.mojang.com/v1/objects/6e64dcabba3c01a7271b4fa6bd898483b794c59b/server.jar)


## Temp-API
Ensure ports for the following are opened
- sudo ufw allow 2377/tcp
- sudo ufw allow 7946/tcp
- sudo ufw allow 7946/udp
- sudo ufw allow 4789/udp
