#!/bin/bash

set -e

mkdir -p nginx-swarm/configs
mkdir -p nginx-swarm/certs

./setup-compose.sh

NODES=(rpi0 rpi1 rpi2 rpi3)

# Generate nginx.conf files
for NODE in "${NODES[@]}"; do
  cat > nginx-swarm/configs/${NODE}-nginx.conf <<EOF
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 443 ssl;
        server_name ${NODE}-server;

        ssl_certificate /etc/ssl/certs/server.crt;
        ssl_certificate_key /etc/ssl/private/server.key;

        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
        }
    }
}
EOF
done

# Default conf (optional)
cat > nginx-swarm/configs/default.conf <<EOF
server {
    listen 80;
    server_name _;

    location / {
        return 444;
    }
}
EOF

# Generate SSL certs with openssl
for NODE in "${NODES[@]}"; do
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx-swarm/certs/${NODE}.key \
    -out nginx-swarm/certs/${NODE}.crt \
    -subj "/CN=${NODE}-server"
done

# Create Docker configs
# Remove configs
# docker config rm rpi0-nginx.conf rpi1-nginx.conf rpi2-nginx.conf rpi3-nginx.conf
for NODE in "${NODES[@]}"; do
  docker config create ${NODE}-nginx.conf nginx-swarm/configs/${NODE}-nginx.conf || true
done

# Create Docker secrets for certs
# Remove certs
# docker secret rm rpi0.crt rpi0.key rpi1.crt rpi1.key rpi2.crt rpi2.key rpi3.crt rpi3.key
for NODE in "${NODES[@]}"; do
  docker secret create ${NODE}.crt nginx-swarm/certs/${NODE}.crt || true
  docker secret create ${NODE}.key nginx-swarm/certs/${NODE}.key || true
done

echo "Docker configs and secrets created."
