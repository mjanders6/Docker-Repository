# mdWiki Roadmap

Planned features, organized by sprint. This file is speculative/in-progress —
`copilot-instructions.md` describes the current, decided architecture only.
When an item here actually ships, move its "out of scope" line in
`copilot-instructions.md` accordingly so the two files don't contradict.

## Sprint 1 — UI/UX, no architecture changes
Low risk, no dependency on the database decision below.

* **Home screen → notebook flow:** landing page lists notebooks; selecting
  one shows its notes. Notes without a notebook get filed under a default
  "Unfiled" (or similar) notebook rather than floating with no home.
* **Better landing page and navbar.**
* **Code block copy button:** add a copy-to-clipboard control on rendered
  code blocks.

## Sprint 2 — Data layer decision (blocking)
This needs to be resolved before Sprint 3, since the dropdown/query
feature depends on the answer.

* **Open question: in-app (embedded, e.g. SQLite) vs. external DB
  (Postgres)?** Trade-off to weigh: external Postgres gives real query/
  join capability for select-driven fields, but breaks the current
  "no database, pure flat files" architecture and adds an operational
  dependency (a service to run, back up, migrate). An embedded option
  keeps things closer to zero-infra but is more limited for relational
  queries across classes.
* **If Postgres:** add it as a docker-compose service, plus a Makefile
  and setup scripts to automate DB/table creation on first run (and
  probably a migration path for schema changes later).
* **Enable HTTPS** for the app itself (reverse proxy with TLS termination,
  or certs directly) — independent of the DB decision, can happen in
  parallel.

## Sprint 3 — Structured fields (depends on Sprint 2)
* **Select / multi-select dropdowns backed by data tables** for classes,
  notes, and queries — e.g. a class field whose options come from a
  queryable table rather than a static YAML list. This is the piece that
  most directly needs Sprint 2's DB decision settled first, since it's
  the feature most likely to actually use Postgres if you go that route.

## Notes
* Sequencing above assumes Sprint 1 can ship independent of the DB call.
  If you'd rather resolve the DB question first, Sprints 1 and 2 could
  run in either order.
