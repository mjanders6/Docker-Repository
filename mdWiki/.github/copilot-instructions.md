# Project: mdWiki

## Core Purpose
mdWiki is a minimal, self-hosted, Docker-based markdown wiki. Everything is
flat files — no database, no third-party services, no telemetry. FastAPI +
Jinja2 render server-side. Full data ownership and portability are the point.

## Architecture (source of truth — do not assume otherwise)
* **Storage:** plain `.md` files with YAML frontmatter under `data/notes/`,
  plain `.yml` class definitions under `data/classes/`. No database of any
  kind. Do not introduce PostgreSQL, SQLite, or an ORM.
* **Auth:** none, intentionally. Access control is expected to be handled
  by a reverse proxy or VPN in front of the app, not by mdWiki itself.
* **Collaboration/history:** none built in. If versioning is needed, the
  user runs git directly against the `data/` directory. Do not build
  in-app version history or real-time collaborative editing.
* **Notebooks:** persistent top-level folders under `data/notes/`. Notes
  can nest under a parent note via the `parent` frontmatter field.
* **Classes:** `.yml` files in `data/classes/` defining a note type's
  `label`, `icon`, `fields` (each with `name`, `label`, `default`, `type`),
  and a starter `template`. Field `type` controls the editor widget
  (`text`, `textarea`, `number`, `date`, `checkbox`, `url`,
  `multiselect`); fields predating `type` default to `text`.
* **Wikilinks:** `[[Note Title]]`, `[[slug]]`, `[[target|display text]]`
  resolve to other notes. Linking to a non-existent title renders a
  "not created" link that creates an empty note on click.
* **Task lists:** `- [ ]` / `- [x]` render as live checkboxes that write
  back to the `.md` file on click.
* Changes to `data/` are picked up on next page load — no rebuild needed
  for content edits, only for code changes.

## What mdWiki DOES
* Create, edit, and organize markdown notes with YAML frontmatter.
* Class-based custom fields per note type, defined in `.yml` files.
* Notebook hierarchy via folders and parent/child note links.
* Wikilink resolution and link-first-write-later note creation.
* Inline task-list checkboxes, saved instantly from the view or editor.

## Explicitly Out of Scope (do not add without being asked)
* Any form of user authentication or login (GitHub OAuth, etc.)
* Real-time collaborative editing
* A database of any kind
* In-app version history (git in `data/` covers this)
* Role-based access control
* Full-text search, backlinks panel, image/file uploads — these are
  acknowledged "phase 2" ideas in the README, not current requirements.
  Don't implement them speculatively; ask first.

## Tech Stack
* Python, FastAPI, Jinja2 (server-side rendering)
* Docker / docker-compose for packaging and running
* Flat-file storage: `.md` (notes) + `.yml` (classes), bind-mounted for
  persistence

## Working Style
* Don't restate these instructions or summarize what you're about to do
  before doing it — just make the change and briefly note what changed.
* Keep changes minimal and consistent with the flat-file, no-database,
  no-auth architecture above. If a request seems to require a database,
  auth system, or real-time sync, flag the conflict with this
  architecture before implementing anything.