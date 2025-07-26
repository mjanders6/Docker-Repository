#!/bin/bash

# Output YAML file
OUTPUT_FILE="docker-compose.yml"
NODES=(rpi0 rpi1 rpi2 rpi3)

# Start with top-level services section
echo "services:" > "$OUTPUT_FILE"

# Loop to generate service definitions
for NODE in "${NODES[@]}"; do
  cat >> "$OUTPUT_FILE" <<EOF
  nginx_${NODE}:
    image: nginx:alpine
    configs:
      - source: ${NODE}-nginx.conf
        target: /etc/nginx/nginx.conf
    secrets:
      - source: ${NODE}.crt
        target: /etc/ssl/certs/server.crt
      - source: ${NODE}.key
        target: /etc/ssl/private/server.key
    deploy:
      placement:
        constraints: [node.hostname == ${NODE}-server]
    ports:
      - target: 80
        published: 8080
        mode: host
      - target: 443
        published: 8443
        mode: host

EOF
done

# Add configs section
echo "configs:" >> "$OUTPUT_FILE"
for NODE in "${NODES[@]}"; do
  echo "  ${NODE}-nginx.conf:" >> "$OUTPUT_FILE"
  echo "    external: true" >> "$OUTPUT_FILE"
done

# Add secrets section
echo "" >> "$OUTPUT_FILE"
echo "secrets:" >> "$OUTPUT_FILE"
for NODE in "${NODES[@]}"; do
  echo "  ${NODE}.crt:" >> "$OUTPUT_FILE"
  echo "    external: true" >> "$OUTPUT_FILE"
  echo "  ${NODE}.key:" >> "$OUTPUT_FILE"
  echo "    external: true" >> "$OUTPUT_FILE"
done

