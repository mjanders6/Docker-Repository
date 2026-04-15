# Makefile for Dockhand & Hawser Docker Swarm Deployment

STACK_NAME := dockhand
COMPOSE_FILE := docker-compose.yml
SECRET_NAME := dockhand_agent_token
SECRET_FILE := .agent_token
MANAGER_IP ?= 192.168.1.20

.PHONY: help init-swarm create-secret deploy update remove logs status clean

help:
	@echo ""
	@echo "Dockhand & Hawser Deployment Commands"
	@echo "--------------------------------------"
	@echo "make init-swarm     Initialize Docker Swarm"
	@echo "make create-secret  Create Dockhand agent token secret"
	@echo "make deploy         Deploy the Dockhand stack"
	@echo "make update         Update the deployed stack"
	@echo "make remove         Remove the deployed stack"
	@echo "make logs           Stream logs for all services"
	@echo "make status         Show status of services and nodes"
	@echo "make clean          Remove local secret file"
	@echo ""

init-swarm:
	docker swarm init --advertise-addr $(MANAGER_IP) || true

create-secret:
	@if [ ! -f $(SECRET_FILE) ]; then \
		echo "Generating random agent token..."; \
		head -c 32 /dev/urandom | base64 > $(SECRET_FILE); \
	fi
	@docker secret rm $(SECRET_NAME) 2>/dev/null || true
	@docker secret create $(SECRET_NAME) $(SECRET_FILE)
	@echo "Docker secret '$(SECRET_NAME)' created."

deploy:
	docker stack deploy -c $(COMPOSE_FILE) $(STACK_NAME)

update:
	docker stack deploy -c $(COMPOSE_FILE) $(STACK_NAME)

remove:
	docker stack rm $(STACK_NAME)

logs:
	@echo "Streaming Dockhand logs..."
	docker service logs -f $(STACK_NAME)_dockhand &
	@echo "Streaming Hawser agent logs..."
	docker service logs -f $(STACK_NAME)_hawser-agent

status:
	@echo "Docker Nodes:"
	docker node ls
	@echo ""
	@echo "Docker Services:"
	docker service ls
	@echo ""
	@echo "Dockhand Tasks:"
	docker service ps $(STACK_NAME)_dockhand
	@echo ""
	@echo "Hawser Agent Tasks:"
	docker service ps $(STACK_NAME)_hawser-agent

clean:
	rm -f $(SECRET_FILE)
	@echo "Local secret file removed."