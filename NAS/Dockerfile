# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Install necessary packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin && \
    rm -rf /var/lib/apt/lists/*

# Environment variables for admin setup
ENV USERNAME=admin \
    PASSWORD=changeme \
    SHARE_NAME=nas \
    SHARE_PATH=/mnt/ssd

# Create shared directory and set permissions
RUN mkdir -p ${SHARE_PATH} && chmod 777 ${SHARE_PATH}

# Setup Samba configuration
RUN mv /etc/samba/smb.conf /etc/samba/smb.conf.bak && \
    echo '[global]\n   workgroup = WORKGROUP\n   server string = Samba Server\n   security = user\n\n[${SHARE_NAME}]\n   path = ${SHARE_PATH}\n   browseable = yes\n   read only = no\n   writable = yes\n   guest ok = no' > /etc/samba/smb.conf

# Entrypoint script for initial setup
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo 'if [ ! -f "/etc/samba/.initialized" ]; then' >> /entrypoint.sh && \
    echo '    echo "Initializing Samba..."' >> /entrypoint.sh && \
    echo '    useradd -M -s /sbin/nologin $USERNAME' >> /entrypoint.sh && \
    echo '(echo $PASSWORD; echo $PASSWORD) | smbpasswd -s -a $USERNAME' >> /entrypoint.sh && \
    echo '    touch /etc/samba/.initialized' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo '/usr/sbin/smbd --foreground --no-process-group' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Expose Samba ports
EXPOSE 139 445

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
