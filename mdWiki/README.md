# Markdown Wiki

A minimal, self-hosted, Docker-based markdown wiki. No database, no
third-party service, no telemetry — just `.md` files with YAML frontmatter
and `.yml` class definitions on disk. FastAPI + Jinja2 render everything
server-side.

## How it works

- **Notes** live under `data/notes/` as plain `.md` files with YAML
  frontmatter at the top (title, class, tags, date, plus any fields defined
  by the note's class). Subfolders are supported (e.g. `data/notes/homelab/mcp-gateway.md`).
- **Classes** live under `data/classes/` as `.yml` files. A class defines:
  - `label` / `icon` — how it's displayed
  - `fields` — extra frontmatter fields notes of this class have, each with
    a `name`, `label`, and `default`
  - `template` — starter markdown body for new notes of this class
- A note references its class with `class: meeting` in its frontmatter.
  The editor reads the class file to know which extra fields to show.

Because it's all flat files, you can edit notes directly with any text
editor (or sync the `data/` folder with git, Syncthing, etc.) and the app
will pick up changes on next page load.

## Running it

```bash
docker compose up -d --build
```

Then visit http://localhost:8000 (or your host's IP/port if run on a
homelab server).

`data/notes/` and `data/classes/` are bind-mounted, so everything you
create persists on the host and survives container rebuilds.

## Adding a new note class

Create a file like `data/classes/book.yml`:

```yaml
name: book
label: Book
icon: "📚"
fields:
  - name: author
    label: Author
    default: ""
  - name: rating
    label: Rating (1-5)
    default: ""
template: |
  ## Summary

  ## Notes
```

It'll immediately show up as an option on the "New Note" page and in the
sidebar filter — no code changes needed.

## What's intentionally NOT here (v1 scope)

- No auth/login (put it behind your reverse proxy / VPN, e.g. what you're
  likely already using for other homelab services)
- No full-text search (can add a simple filename/content grep-based search
  next)
- No wikilinks / backlinks between notes (straightforward to add — parse
  `[[note-slug]]` syntax in the markdown renderer)
- No image/file uploads (attach via a `static/uploads` mount + `<img>` in
  markdown for now)
- No live-collaboration or version history (git in the data dir handles
  this if you want it)

All of these are natural "phase 2" additions once the core is solid.
