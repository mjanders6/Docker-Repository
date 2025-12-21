IMAGE_NAME=mjanders6/minecraft
IMAGE_TAG=latest
CONTAINER_NAME=minecraft
BACKUP_DATE=$(shell date +%Y-%m-%d_%H-%M-%S)

VOLUMES = world_data world_nether_data world_the_end_data config_data tools_data backups_data server_root_data mods_data

# -------------------------------------------------------
# Initialize Docker volumes
# -------------------------------------------------------
init-volumes:
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
build: init-volumes
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "✔ Image built and pushed: $(IMAGE_NAME):$(IMAGE_TAG)"

# -------------------------------------------------------
# Backup world data (stored inside backups_data volume)
# -------------------------------------------------------
backup:
	@echo "📦 Creating backup inside backups_data volume..."
	docker run --rm \
		-v backups_data:/backup \
		-v world_data:/world \
		-v world_nether_data:/world_nether \
		-v world_the_end_data:/world_the_end \
		-v config_data:/config \
		ubuntu bash -c "\
			apt-get update >/dev/null && apt-get install -y tar >/dev/null && \
			tar czf /backup/mc-backup-$(BACKUP_DATE).tar.gz /world /world_nether /world_the_end /config \
		"
	@echo "✔ Backup created: mc-backup-$(BACKUP_DATE).tar.gz"

# -------------------------------------------------------
# Restore from backup into volumes
# -------------------------------------------------------
restore:
ifndef FILE
	$(error Must provide FILE=mc-backup-file.tar.gz)
endif
	@echo "♻ Restoring backup $(FILE)..."
	docker run --rm \
		-v backups_data:/backup \
		-v world_data:/world \
		-v world_nether_data:/world_nether \
		-v world_the_end_data:/world_the_end \
		-v config_data:/config \
		ubuntu bash -c "\
			apt-get update >/dev/null && apt-get install -y tar >/dev/null && \
			tar xzf /backup/$(FILE) -C / \
		"
	@echo "✔ Restore complete"

# -------------------------------------------------------
# Start container
# -------------------------------------------------------
start:
	docker compose up -d

# -------------------------------------------------------
# Stop container
# -------------------------------------------------------
stop:
	docker compose down

# -------------------------------------------------------
# Full workflow: backup → build → push → restart
# -------------------------------------------------------
update: backup build stop start
