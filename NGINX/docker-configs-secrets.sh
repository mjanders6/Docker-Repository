# rpi0-server configs
docker config create nginx_conf_rpi0 nginx-configs/rpi0-server/nginx.conf
docker config create site_conf_rpi0 nginx-configs/rpi0-server/site.conf

docker secret create cert_fullchain_rpi0 nginx-configs/rpi0-server/fullchain.pem
docker secret create cert_privkey_rpi0 nginx-configs/rpi0-server/privkey.pem

# rpi1-server configs
docker config create nginx_conf_rpi1 nginx-configs/rpi1-server/nginx.conf
docker config create site_conf_rpi1 nginx-configs/rpi1-server/site.conf

docker secret create cert_fullchain_rpi1 nginx-configs/rpi1-server/fullchain.pem
docker secret create cert_privkey_rpi1 nginx-configs/rpi1-server/privkey.pem

# rpi2-server configs
docker config create nginx_conf_rpi2 nginx-configs/rpi2-server/nginx.conf
docker config create site_conf_rpi2 nginx-configs/rpi2-server/site.conf

docker secret create cert_fullchain_rpi2 nginx-configs/rpi2-server/fullchain.pem
docker secret create cert_privkey_rpi2 nginx-configs/rpi2-server/privkey.pem

# rpi3-server configs
docker config create nginx_conf_rpi3 nginx-configs/rpi3-server/nginx.conf
docker config create site_conf_rpi3 nginx-configs/rpi3-server/site.conf

docker secret create cert_fullchain_rpi3 nginx-configs/rpi3-server/fullchain.pem
docker secret create cert_privkey_rpi3 nginx-configs/rpi3-server/privkey.pem