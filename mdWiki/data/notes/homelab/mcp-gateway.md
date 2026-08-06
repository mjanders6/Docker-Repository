---
title: Docker MCP Gateway
class: service
tags:
- homelab
- mcp
date: '2026-07-31'
host: docker-mcp-gateway
port: '8811'
status: running
---

## Purpose

Brokers access from Claude Desktop to self-hosted tools (Obsidian, Firefly, Minecraft server)
via the Docker MCP Toolkit Profiles system.

## Configuration

Runs with `--profile default`. Individual tool servers are registered as MCP Toolkit profiles.

## Notes

- Obsidian Local REST API plugin had to be bound to `0.0.0.0` instead of `127.0.0.1` for the
  container to reach it.
