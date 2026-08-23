# Project: mdWiki

## Core Purpose
mdWiki is a minimal, self-hosted, Docker-based markdown wiki. Everything is
flat files on disk — no persistent database, no third-party services, no
telemetry. FastAPI + Jinja2 render server-side. Full data ownership and
portability are the point.

## Architecture (source of truth — do not assume otherwise)
* **Storage:** plain `.md` files with YAML frontmatter under `data/notes/`,
  plain `.yml` class definitions under `data/classes/`. This is the only
  persistent store. Do not introduce PostgreSQL or an ORM, and do not make
  the query engine below (or any other SQLite use) persistent — see
  **Embedded queries**.
* **Embedded queries:** notes can contain fenced ```query``` or ```sql```
  code blocks, rendered as a results table wherever they appear (view page
  and edit-page preview). Both run against an **in-memory SQLite database
  rebuilt from the flat files on every render** — never written to disk,
  connection is read-only (`PRAGMA query_only`), only `SELECT` is permitted
  for `sql` blocks. `query` blocks are a simple `key: value` mini-language
  (`class`, `tag`, `contains`, `sort`, `limit`, `columns`); `contains` does
  a case-insensitive search across a note's title **and full body**. `sql`
  blocks query a `notes` table exposing `slug`, `title`, `class`, `tags`,
  `date`, `body`, plus every class's custom fields. This is why "no
  database" above means no *persistent* one — the in-memory SQLite layer
  is intentional and existing; don't treat it as something to remove, and
  don't make it write-capable or persist it to disk.
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
* Embedded `query`/`sql` blocks in notes, including full-text search of
  note bodies via `contains:` — see **Embedded queries** above.

## Explicitly Out of Scope (do not add without being asked)
* Any form of user authentication or login (GitHub OAuth, etc.)
* Real-time collaborative editing
* A *persistent* database of any kind (Postgres, a written-to-disk SQLite
  file, etc.) — the existing in-memory, rebuilt-per-render SQLite used for
  embedded queries is not this; see **Embedded queries** above.
* In-app version history (git in `data/` covers this)
* Role-based access control
* A backlinks panel, image/file uploads — acknowledged "phase 2" ideas in
  the README, not current requirements. Don't implement them
  speculatively; ask first.

## Tech Stack
* Python, FastAPI, Jinja2 (server-side rendering)
* Docker / docker-compose for packaging and running
* Flat-file storage: `.md` (notes) + `.yml` (classes), bind-mounted for
  persistence
* SQLite, in-memory only, rebuilt per render, powering embedded
  `query`/`sql` blocks — not a persistence layer

## Working Style
* Don't restate these instructions or summarize what you're about to do
  before doing it — just make the change and briefly note what changed.
* Keep changes minimal and consistent with the flat-file, no-database,
  no-auth architecture above. If a request seems to require a database,
  auth system, or real-time sync, flag the conflict with this
  architecture before implementing anything.