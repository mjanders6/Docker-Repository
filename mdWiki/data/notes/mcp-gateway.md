---
class: service
date: '2026-08-03'
host: ''
port: ''
status: running
tags:
- homelab
title: Docker MCP Gateway
---

## Purpose

Brokers access from Claude Desktop to self-hosted tools (Obsidian, Firefly, Minecraft server)
via the Docker MCP Toolkit Profiles system.

## Configuration

Runs with `--profile default`. Individual tool servers are registered as MCP Toolkit profiles.

## Notes

- Obsidian Local REST API plugin had to be bound to `0.0.0.0` instead of `127.0.0.1` for the
  container to reach it.