FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV MC_UID=1000 \
    MC_GID=1000 \
    MC_USER=minecraft \
    MC_GROUP=minecraft \
    EULA=true \
    SERVER_PORT=25565 \
    MC_VERSION=26.1.2 \
    FORGE_VERSION=64.0.1

USER root

RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    tar \
    unzip \
    gosu \
    git \
    openjdk-25-jre-headless \
    wget \
    curl \
    gcc \
    tzdata \
    gettext-base \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${MC_GID} ${MC_GROUP} && \
    useradd -u ${MC_UID} -g ${MC_GID} -m ${MC_USER}

WORKDIR /server

RUN mkdir -p \
    world \
    world_nether \
    world_the_end \
    config \
    tools \
    backups \
    runtime \
    mods

RUN git clone https://github.com/Tiiffi/mcrcon.git /server/tools

WORKDIR /server/tools
RUN gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

WORKDIR /server

EXPOSE ${SERVER_PORT}

# Download Forge installer
RUN wget -O forge-installer.jar \
    https://maven.minecraftforge.net/net/minecraftforge/forge/${MC_VERSION}-${FORGE_VERSION}/forge-${MC_VERSION}-${FORGE_VERSION}-installer.jar

# Install Forge server
RUN java -jar forge-installer.jar --installServer && \
    rm forge-installer.jar

COPY config/ /server/config/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
