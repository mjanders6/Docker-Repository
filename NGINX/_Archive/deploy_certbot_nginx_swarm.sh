#!/bin/bash

# === CONFIG ===
DOMAINS=("rpi0.example.com" "rpi1.example.com" "rpi2.example.com" "rpi3.example.com")
HOSTNAMES=("rpi0-server" "rpi1-server" "rpi2-server" "rpi3-server")
EMAIL="your-email@example.com"
BASE_DIR="/srv/certbot"
COMPOSE_FILE="docker-compose.yml"

# === Step 1: Create Directories & Configs ===
mkdir -p $BASE_DIR

echo "Preparing directories and configs..."
for i in "${!DOMAINS[@]}"; do
  DOMAIN=${DOMAINS[$i]}
  HOST=${HOSTNAMES[$i]}
  NODE_DIR="$BASE_DIR/$HOST"
  CERT_DIR="$NODE_DIR/certs"
  WWW_DIR="$NODE_DIR/www"
  NGINX_CONF="$NODE_DIR/nginx.conf"
  CONF_DIR="$NODE_DIR/conf.d"

  mkdir -p "$CERT_DIR" "$WWW_DIR" "$CONF_DIR"

  # Create nginx.conf
  cat > "$NGINX_CONF" <<EOF
worker_processes 1;
events { worker_connections 1024; }

http {
    include       mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name $DOMAIN;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://\$host\$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name $DOMAIN;

        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

        location / {
            return 200 'Secure Hello from $HOST';
        }
    }
}
EOF

  # Create conf.d/site.conf for NGINX (empty or further config if needed)
  echo "# site.conf for $HOST" > "$CONF_DIR/site.conf"
done

# === Step 2: Generate Docker Compose Swarm File ===
echo "Creating $COMPOSE_FILE..."

cat > $COMPOSE_FILE <<EOF
version: "3.9"

services:
EOF

for i in "${!DOMAINS[@]}"; do
  DOMAIN=${DOMAINS[$i]}
  HOST=${HOSTNAMES[$i]}
  SERVICE_SUFFIX=$(echo "$HOST" | tr '-' '_')

  cat >> $COMPOSE_FILE <<EOF
  nginx_${SERVICE_SUFFIX}:
    image: nginx:alpine
    volumes:
      - $BASE_DIR/$HOST/nginx.conf:/etc/nginx/nginx.conf:ro
      - $BASE_DIR/$HOST/conf.d:/etc/nginx/conf.d:ro
      - $BASE_DIR/$HOST/certs:/etc/letsencrypt:ro
      - $BASE_DIR/$HOST/www:/var/www/certbot:ro
    ports:
      - "${i}080:80"
      - "${i}443:443"
    deploy:
      placement:
        constraints: [node.hostname == $HOST]

  certbot_${SERVICE_SUFFIX}:
    image: certbot/certbot
    volumes:
      - $BASE_DIR/$HOST/certs:/etc/letsencrypt
      - $BASE_DIR/$HOST/www:/var/www/certbot
    command: > 
      certonly --webroot --webroot-path=/var/www/certbot 
      --email $EMAIL --agree-tos --no-eff-email 
      -d $DOMAIN
    deploy:
      placement:
        constraints: [node.hostname == $HOST]
EOF

done

# === Step 3: Deploy the Stack ===
echo "Deploying stack to Docker Swarm..."
docker stack deploy -c $COMPOSE_FILE certbot-nginx-swarm

echo "Initial certificate issuance complete. For auto-renewal, use cron or add renew service."
