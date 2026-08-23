# mdWiki Roadmap

Planned features, organized by sprint. This file is speculative/in-progress —
`copilot-instructions.md` describes the current, decided architecture only.
When an item here actually ships, move its "out of scope" line in
`copilot-instructions.md` accordingly so the two files don't contradict.

## Sprint 1 — UI/UX, no architecture changes
Low risk, no dependency on the database decision below. This will up the version to 3.2.0 across the app.

* **Home screen → notebook flow:** landing page lists notebooks; selecting
  one shows its notes. Notes without a notebook get filed under a default
  "Unfiled" (or similar) notebook rather than floating with no home.
* **Better landing page and navbar:** the landing page needs a better look and feel. The navbar should be some type of dropdown so that it does not span across the top of the page.
* **Code block copy button:** add a copy-to-clipboard control on rendered
  code blocks.

## Sprint 2 — Data layer decision (blocking)
This needs to be resolved before Sprint 3, since the dropdown/query
feature depends on the answer. This will up the version to 4.0.0 across the app.

* **Open question: persist the existing query layer vs. add an external
  DB (Postgres)?** Note: the app already has an in-memory SQLite database
  for the `query`/`sql` embedded-query feature -- it's rebuilt from the
  flat files on every render and never written to disk. The real question
  for select-driven dropdown options isn't "add a database," it's whether
  that data needs to be *written back* and persisted (e.g. a user managing
  a shared options list through the UI), which the current read-only,
  ephemeral SQLite can't do. Trade-off to weigh: external Postgres gives
  real persistent, writable storage, but breaks the current "no persistent
  database, pure flat files" architecture and adds an operational
  dependency (a service to run, back up, migrate). Extending the existing
  SQLite layer to also persist to disk is a smaller change but blurs the
  "flat files are the only source of truth" guarantee.
* **If Postgres:** add it as a docker-compose service, plus a Makefile
  and setup scripts to automate DB/table creation on first run (and
  probably a migration path for schema changes later).
* **Enable HTTPS** for the app itself (reverse proxy with TLS termination,
  or certs directly) — independent of the DB decision, can happen in
  parallel.

## Sprint 3 — Structured fields (depends on Sprint 2)
This will up the version to 4.1.0 across the app.
* **Select / multi-select dropdowns backed by data tables** for classes,
  notes, and queries — e.g. a class field whose options come from a
  queryable table rather than a static YAML list. This is the piece that
  most directly needs Sprint 2's DB decision settled first, since it's
  the feature most likely to actually use Postgres if you go that route.

## Notes
* Sequencing above assumes Sprint 1 can ship independent of the DB call.
  If you'd rather resolve the DB question first, Sprints 1 and 2 could
  run in either order.
