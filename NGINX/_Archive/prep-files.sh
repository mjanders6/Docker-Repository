#!/bin/bash

# === CONFIG ===
HOSTNAMES=("rpi0-server" "rpi1-server" "rpi2-server" "rpi3-server")
DOMAINS=("rpi0.example.com" "rpi1.example.com" "rpi2.example.com" "rpi3.example.com")
BASE_DIR="nginx-configs"

# === Create Directories and Files ===
echo "Creating nginx-configs directory structure..."

mkdir -p "$BASE_DIR"

for i in "${!HOSTNAMES[@]}"; do
  HOST=${HOSTNAMES[$i]}
  DOMAIN=${DOMAINS[$i]}
  DIR="$BASE_DIR/$HOST"

  mkdir -p "$DIR"

  # nginx.conf
  cat > "$DIR/nginx.conf" <<EOF
worker_processes 1;
events { worker_connections 1024; }

http {
    include       mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name $DOMAIN;

        location / {
            return 301 https://\$host\$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name $DOMAIN;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        location / {
            return 200 'Secure Hello from $HOST';
        }
    }
}
EOF

  # site.conf (optional custom config per node)
  cat > "$DIR/site.conf" <<EOF
# site.conf for $HOST
# Add custom location blocks or settings here if needed
EOF

  # Generate placeholder dummy certs (can be replaced by real certs or Certbot)
  openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout "$DIR/privkey.pem" \
    -out "$DIR/fullchain.pem" \
    -subj "/CN=$DOMAIN"

  echo "Prepared config and dummy certs for $HOST"
done

echo "Done. Directory structure is ready in $BASE_DIR/"
