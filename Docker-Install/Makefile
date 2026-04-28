.PHONY: help install check swarm-init swarm-join-worker swarm-join-manager docker-remove docker-reinstall docker-clean swarm-leave portainer-setup portainer-deploy portainer-remove full-setup

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

## help: Show this help message
help: ## Show this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-25s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## install: Install Docker with error handling
install: ## Install Docker with error handling
	@echo "🔧 Starting Docker installation..."

	if ! sudo apt update && sudo apt upgrade -y; then
		echo "❌ Error: System update/upgrade failed"; exit 1
	fi

	if ! sudo apt install -y ca-certificates curl gnupg; then
		echo "❌ Error: Failed to install prerequisites"; exit 1
	fi

	if ! sudo install -m 0755 -d /etc/apt/keyrings; then
		echo "❌ Error: Failed to create keyrings directory"; exit 1
	fi

	if ! curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
		sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; then
		echo "❌ Error: Failed to install Docker GPG key"; exit 1
	fi

	if ! sudo chmod a+r /etc/apt/keyrings/docker.gpg; then
		echo "❌ Error: Failed to set permissions on GPG key"; exit 1
	fi

	if ! echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu noble stable" | \
		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; then
		echo "❌ Error: Failed to add Docker repo"; exit 1
	fi

	if ! sudo apt update; then
		echo "❌ Error: apt update failed"; exit 1
	fi

	if ! sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; then
		echo "❌ Error: Docker installation failed"; exit 1
	fi

	if ! sudo usermod -aG docker $$USER; then
		echo "❌ Error: Failed to add user to docker group"; exit 1
	fi

	@echo "✅ Docker installed. Log out/in to use without sudo."

## check: Verify Docker installation
check: ## Verify Docker installation
	@echo "🔍 Checking Docker..."
	@if command -v docker >/dev/null 2>&1; then \
		docker --version; \
	else \
		echo "❌ Docker not installed"; exit 1; \
	fi

## swarm-init: Initialize Docker Swarm as manager
swarm-init: ## Initialize Docker Swarm as manager
	@echo "🚀 Initializing Swarm (manager)..."
	if ! docker info >/dev/null 2>&1; then
		echo "❌ Error: Docker is not running"; exit 1
	fi

	if docker info | grep -q "Swarm: active"; then
		echo "⚠️ Swarm already initialized"; exit 0
	fi

	if ! docker swarm init; then
		echo "❌ Error: Failed to initialize swarm"; exit 1
	fi

	@echo "✅ Swarm initialized as manager"
	@echo "👉 Worker join command:"
	@docker swarm join-token worker
	@echo "👉 Manager join command:"
	@docker swarm join-token manager

## swarm-join-worker: Join an existing swarm as worker (requires TOKEN and MANAGER)
swarm-join-worker: ## Join an existing swarm as worker (requires TOKEN and MANAGER)
	@if [ -z "$$TOKEN" ] || [ -z "$$MANAGER" ]; then
		echo "❌ Usage: make swarm-join-worker TOKEN=<token> MANAGER=<ip:port>"; exit 1
	fi

	@echo "🔗 Joining swarm as worker..."
	if ! docker swarm join --token $$TOKEN $$MANAGER; then
		echo "❌ Error: Failed to join swarm as worker"; exit 1
	fi

	@echo "✅ Joined swarm as worker"

## swarm-join-manager: Join an existing swarm as manager (requires TOKEN and MANAGER)
swarm-join-manager: ## Join an existing swarm as manager (requires TOKEN and MANAGER)
	@if [ -z "$$TOKEN" ] || [ -z "$$MANAGER" ]; then
		echo "❌ Usage: make swarm-join-manager TOKEN=<token> MANAGER=<ip:port>"; exit 1
	fi

	@echo "🔗 Joining swarm as manager..."
	if ! docker swarm join --token $$TOKEN $$MANAGER; then
		echo "❌ Error: Failed to join swarm as manager"; exit 1
	fi

	@echo "✅ Joined swarm as manager"

## docker-remove: Remove Docker completely (including Swarm)
docker-remove: ## Remove Docker completely (including Swarm)
	@echo "⚠️  WARNING: This will remove Docker, Swarm, and ALL containers/volumes!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds..."
	@sleep 5
	@echo "Leaving Docker Swarm..."
	docker swarm leave --force 2>/dev/null || echo "Not in a Swarm or already left"
	@echo "Removing all stacks..."
	docker stack rm $$(docker stack ls -q) 2>/dev/null || echo "No stacks to remove"
	@sleep 5
	@echo "Stopping all containers..."
	sudo docker ps -aq | xargs -r sudo docker stop
	@echo "Removing all containers..."
	sudo docker ps -aq | xargs -r sudo docker rm
	@echo "Removing volumes..."
	sudo docker volume prune -f
	@echo "Removing networks..."
	sudo docker network prune -f
	@echo "Removing Docker packages..."
	sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	sudo apt-get purge -y docker-ce docker-ce-cli containerd.io
	sudo apt-get autoremove -y
	@echo "Removing Docker data directories..."
	sudo rm -rf /var/lib/docker
	sudo rm -rf /var/lib/containerd
	sudo rm -rf /etc/docker
	@echo "✅ Docker and Swarm removed successfully"

## docker-reinstall: Remove and reinstall Docker cleanly
docker-reinstall: docker-remove install ## Remove and reinstall Docker cleanly
	@echo "✅ Docker has been cleanly reinstalled!"

## docker-clean: Clean up stopped containers and dangling images
docker-clean: ## Clean up stopped containers and dangling images
	@echo "🧹 Cleaning up Docker..."
	docker container prune -f
	docker image prune -f
	@echo "✅ Docker cleanup complete"

## swarm-leave: Leave Docker Swarm
swarm-leave: ## Leave Docker Swarm
	@echo "⚠️  WARNING: This will leave the Swarm!"
	@echo "Press Ctrl+C to cancel, or wait 3 seconds..."
	@sleep 3
	docker swarm leave --force
	@echo "✅ Left Swarm"

## portainer-setup: Create Portainer secrets and volumes
portainer-setup: ## Create Portainer secrets and volumes
	@echo "📦 Setting up Portainer resources..."
	docker volume create portainer_data
	openssl rand -base64 32 | docker secret create agent_secret - 2>/dev/null || echo "ℹ️  Secret already exists"
	@echo "✅ Portainer resources created"

## portainer-deploy: Deploy Portainer as Swarm service
portainer-deploy: portainer-setup ## Deploy Portainer as Swarm service
	@echo "🚀 Deploying Portainer as Swarm service..."
	docker stack deploy -c portainer-swarm-server.yml portainer
	@sleep 10
	@echo ""
	@echo "✅ Portainer deployed!"
	@IP=$$(hostname -I | awk '{print $$1}'); \
	echo "🌐 Access Portainer at: http://$$IP:9000"; \
	echo ""; \
	docker service ps portainer_portainer

## portainer-remove: Remove Portainer stack and resources
portainer-remove: ## Remove Portainer stack and resources
	@echo "🗑️  Removing Portainer..."
	docker stack rm portainer
	docker volume rm portainer_data 2>/dev/null || echo "ℹ️  Volume already removed"
	docker secret rm agent_secret 2>/dev/null || echo "ℹ️  Secret already removed"
	@echo "✅ Portainer removed"

## full-setup: Complete setup (Docker + Swarm + Portainer)
full-setup: docker-reinstall swarm-init portainer-deploy ## Complete setup (Docker + Swarm + Portainer)
	@echo ""
	@echo "========================================="
	@echo "✅ FULL SETUP COMPLETE!"
	@echo "========================================="
	@echo "✓ Docker: Installed"
	@echo "✓ Swarm: Initialized"
	@echo "✓ Portainer: Deployed"
	@echo ""
	@IP=$$(hostname -I | awk '{print $$1}'); \
	echo "🌐 Access Portainer at: http://$$IP:9000"; \
	echo "Complete setup wizard in the browser"
