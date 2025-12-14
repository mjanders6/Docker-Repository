FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV MC_UID=1000 \
    MC_GID=1000 \
    MC_USER=minecraft \
    MC_GROUP=minecraft \
    EULA=true \
    SERVER_PORT=25565

USER root

RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    tar \
    unzip \
    gosu \
    git \
    openjdk-21-jre-headless \
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
    runtime

RUN git clone https://github.com/Tiiffi/mcrcon.git /server/tools

WORKDIR /server/tools
RUN gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

WORKDIR /server

EXPOSE ${SERVER_PORT}

COPY server.jar /server/server.jar
COPY config/ /server/config/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]