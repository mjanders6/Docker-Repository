#!/bin/bash

# Setup Docker Configs
docker config create rpi0-nginx.conf configs/rpi0-nginx.conf
docker config create rpi1-nginx.conf configs/rpi1-nginx.conf
docker config create rpi2-nginx.conf configs/rpi2-nginx.conf
docker config create rpi3-nginx.conf configs/rpi3-nginx.conf

# Create Docker Certs and Keys
docker secret create rpi0.crt certs/rpi0.crt
docker secret create rpi0.key certs/rpi0.key

docker secret create rpi1.crt certs/rpi1.crt
docker secret create rpi1.key certs/rpi1.key

docker secret create rpi2.crt certs/rpi2.crt
docker secret create rpi2.key certs/rpi2.key

docker secret create rpi3.crt certs/rpi3.crt
docker secret create rpi3.key certs/rpi3.key
