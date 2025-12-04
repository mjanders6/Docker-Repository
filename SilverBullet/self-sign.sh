mkdir -p silverbullet/nginx/certs
cd silverbullet/nginx/certs

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout selfsigned.key \
  -out selfsigned.crt \
  -subj "/CN=your-local-domain"
