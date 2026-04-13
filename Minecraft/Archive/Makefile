IMAGE_NAME=<docker-hub-username>/<repository-name>
IMAGE_TAG=<tag>
CONTAINER_NAME=minecraft
BACKUP_DATE=$(shell date +%Y-%m-%d_%H-%M-%S)

VOLUMES = minecraft_server minecraft_server_backups

# -------------------------------------------------------
# Help - Display available make commands
# -------------------------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "🧱 Minecraft Docker Management"
	@echo "-------------------------------------------"
	@echo "Usage: make <target> [OPTIONS]"
	@echo ""
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "Variables:"
	@echo "  IMAGE_NAME       Docker image name (default: $(IMAGE_NAME))"
	@echo "  IMAGE_TAG        Docker image tag (default: $(IMAGE_TAG))"
	@echo "  CONTAINER_NAME   Container name (default: $(CONTAINER_NAME))"
	@echo "  BACKUP_DATE      Timestamp used for backups"
	@echo ""
	@echo "Examples:"
	@echo "  make init-volumes"
	@echo "  make build"
	@echo "  make backup"
	@echo "  make restore FILE=mc-backup-YYYY-MM-DD_HH-MM-SS.tar.gz"
	@echo "  make start"
	@echo "  make stop"
	@echo "  make update"
	@echo ""

# -------------------------------------------------------
# Initialize Docker volumes
# -------------------------------------------------------
init-volumes: ## Create required Docker volumes if they do not exist
	@for vol in $(VOLUMES); do \
		if ! docker volume inspect $$vol >/dev/null 2>&1; then \
			echo "📦 Creating volume $$vol..."; \
			docker volume create $$vol; \
		else \
			echo "✔ Volume $$vol already exists"; \
		fi \
	done

# -------------------------------------------------------
# Build and push image
# -------------------------------------------------------
build: init-volumes ## Build and push the Docker image
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "✔ Image built and pushed: $(IMAGE_NAME):$(IMAGE_TAG)"

# -------------------------------------------------------
# Backup minecraft_server volume (stored inside minecraft_server_backups)
# -------------------------------------------------------
backup: ## Create a timestamped backup of the minecraft_server volume
	@echo "📦 Creating backup of minecraft_server volume..."
	docker run --rm \
		-v minecraft_server_backups:/opt/minecraft/backups \
		-v minecraft_server:/opt/minecraft/server:ro \
		alpine sh -c "\
			cd /opt/minecraft && \
			tar czf /opt/minecraft/backups/mc-backup-$(BACKUP_DATE).tar.gz server \
		"
	@echo "✔ Backup created: mc-backup-$(BACKUP_DATE).tar.gz"

# -------------------------------------------------------
# Restore selected directories from backup into volume
# How to run:
#   make restore FILE=mc-backup-file.tar.gz
# -------------------------------------------------------
restore: ## Restore world data from a backup (requires FILE variable)
ifndef FILE
	$(error Must provide FILE=mc-backup-file.tar.gz)
endif
	@echo "♻ Restoring selected worlds from $(FILE) into minecraft_server..."
	docker run --rm \
		-v minecraft_server_backups:/opt/minecraft/backups \
		-v minecraft_server:/opt/minecraft/server \
		alpine sh -c "\
			tar xzf /opt/minecraft/backups/$(FILE) -C /opt/minecraft/server \
				--strip-components=1 \
				server/world \
				server/world_nether \
				server/world_the_end \
		"
	@echo "✔ Restore complete"

# -------------------------------------------------------
# Start container
# -------------------------------------------------------
start: ## Start the Minecraft server using docker compose
	docker compose up -d

# -------------------------------------------------------
# Stop container
# -------------------------------------------------------
stop: ## Stop the Minecraft server
	docker compose down

# -------------------------------------------------------
# Full workflow: backup → build → push → restart
# -------------------------------------------------------
update: backup build stop start ## Full workflow: backup → build → push → restart
