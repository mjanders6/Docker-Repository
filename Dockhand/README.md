# Dockhand & Hawser Docker Swarm Deployment

This package provides a production-ready Docker Swarm deployment for **Dockhand** and **Hawser agents**.

## 🏗 Architecture

- **Dockhand Service**
  - Runs as a single replicated service on a **manager node**.
  - Provides centralized orchestration and management.
  - Exposes a web interface on port **8080**.

- **Hawser Agents**
  - Deployed in **global mode**, ensuring one agent runs on every node in the swarm.
  - Each agent connects to the Dockhand service.
  - Requires access to the Docker socket for monitoring and orchestration.

## 📦 Included Files

```
dockhand-deployment/
├── docker-compose.yml
├── Makefile
└── README.md
```

## 🖥 Prerequisites

1. **Docker Engine** installed on all nodes.
2. **Docker Swarm** initialized on the manager node.
3. Network connectivity between the following hosts:
   - 192.168.1.20 (Manager)
   - 192.168.1.21
   - 192.168.1.22
   - 192.168.1.23

## 🚀 Step-by-Step Deployment

### 1️⃣ Initialize Docker Swarm (Manager Node)

```bash
docker swarm init --advertise-addr 192.168.1.20
```

### 2️⃣ Join Worker Nodes

Run the join command displayed from the previous step on each worker node:

```bash
docker swarm join --token <WORKER_TOKEN> 192.168.1.20:2377
```

### 3️⃣ Verify Nodes

```bash
docker node ls
```

### 4️⃣ Deploy the Stack

```bash
docker stack deploy -c docker-compose.yml dockhand
```

### 5️⃣ Verify Services

```bash
docker service ls
docker service ps dockhand_dockhand
docker service ps dockhand_hawser-agent
```

### 6️⃣ Access Dockhand

Open a browser and navigate to:

```
http://<manager-ip>:8080
```

Example:

```
http://192.168.1.20:8080
```

## 🔄 Updating the Stack

```bash
docker stack deploy -c docker-compose.yml dockhand
```

## 🧹 Removing the Stack

```bash
docker stack rm dockhand
```

## 📊 Monitoring

```bash
docker service logs -f dockhand_dockhand
docker service logs -f dockhand_hawser-agent
```

## 🔐 Security Considerations

- The Docker socket is mounted read-only for the Hawser agent. Restrict access to trusted nodes.
- Consider using Docker secrets for sensitive configuration.
- Enable TLS for production environments if supported by Dockhand.

## 🛠 Customization

- Adjust resource limits in `docker-compose.yml` as needed.
- Increase Dockhand replicas if high availability is required.
- Add node labels for more granular placement constraints.

## 📄 License

This deployment template is provided as-is for educational and operational use.
