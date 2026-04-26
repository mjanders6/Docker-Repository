.PHONY: help install check swarm-init swarm-join-worker swarm-join-manager

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

## help: Show this help message
help: ## Show this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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