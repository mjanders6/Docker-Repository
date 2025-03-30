# Purpose 
This Repository is to manage home lab Docker files and compose files

## Kali 
- sudo nvidia-ctk runtime configure --runtime=docker --set-as-default
- sudo service docker restart

## Minecraft
Current link to MInecraft Java jar file:
- [1.21.5](https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar)

## Temp-API
Ensure ports for the following are opened
- sudo ufw allow 2377/tcp
- sudo ufw allow 7946/tcp
- sudo ufw allow 7946/udp
- sudo ufw allow 4789/udp
