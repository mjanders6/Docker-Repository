"""
Embedded note queries.

Two flavors, both triggered by a fenced code block in a note's markdown body:

    ```query
    class: book
    tag: fiction
    contains: hobbit
    sort: -date
    limit: 10
    columns: title, author, rating
    ```

    ```sql
    SELECT title, slug FROM notes WHERE body LIKE '%raspberry pi%'
    ```

`query` blocks are a small, safe key:value filter over the note index --
no injection surface at all. `contains:` does a case-insensitive full-text
search over each note's title and markdown body (headings, paragraphs,
everything), and pairs naturally with a `snippet` column showing the
matched text in context.

`sql` blocks run against a throwaway in-memory SQLite table (`notes`)
rebuilt from disk on every render, with the connection locked to read-only
(`PRAGMA query_only = ON`) and only a single SELECT statement permitted.
The table includes a `body` column with each note's full markdown text, so
`WHERE body LIKE '%phrase%'` searches headings and paragraphs directly.
Nothing is ever persisted to disk by a query.
"""
import html as html_lib
import re
import sqlite3

from . import store

# Matches ```query ... ``` or ```sql ... ``` fenced blocks in note markdown.
QUERY_BLOCK_RE = re.compile(r"```(query|sql)[ \t]*\r?\n(.*?)```", re.DOTALL | re.IGNORECASE)

MAX_ROWS = 200
DEFAULT_LIMIT = 50

# Base columns always present on the virtual `notes` table, plus every
# field name declared by any class (so `SELECT author FROM notes` works
# without the author having to know which class defines it). `body` holds
# the note's full markdown text (headings, paragraphs, everything) so it
# can be searched with LIKE.
_BASE_COLUMNS = ["slug", "title", "class", "tags", "date", "body"]

_SQL_FORBIDDEN = ("attach", "pragma", "vacuum", "detach", "reindex")


class QueryError(Exception):
    pass


def _all_field_names() -> list[str]:
    names = set()
    for c in store.list_classes():
        for f in c.get("fields", []):
            n = f.get("name")
            if n and n not in _BASE_COLUMNS:
                names.add(n)
    return sorted(names)


def _build_notes_db() -> sqlite3.Connection:
    field_names = _all_field_names()
    columns = _BASE_COLUMNS + field_names

    conn = sqlite3.connect(":memory:")
    col_defs = ", ".join(f'"{c}" TEXT' for c in columns)
    conn.execute(f"CREATE TABLE notes ({col_defs})")

    placeholders = ", ".join("?" for _ in columns)
    col_list = ", ".join(f'"{c}"' for c in columns)
    insert_sql = f"INSERT INTO notes ({col_list}) VALUES ({placeholders})"

    for n in store.list_notes():
        full = store.get_note(n["slug"])
        meta = (full or {}).get("metadata", {}) or {}
        note_body = (full or {}).get("body", "") or ""
        row = [n["slug"], n["title"], n["class"], ", ".join(n["tags"]), str(n["date"] or ""), note_body]
        for fname in field_names:
            row.append(str(meta.get(fname, "") or ""))
        conn.execute(insert_sql, row)

    conn.commit()
    # Belt-and-suspenders: even though every query here is user-supplied
    # from note bodies, the connection itself refuses any write.
    conn.execute("PRAGMA query_only = ON")
    return conn


def run_sql(sql: str) -> tuple[list[str], list[tuple]]:
    sql = (sql or "").strip().rstrip(";")
    if not sql:
        raise QueryError("Empty query")
    lowered = sql.lower()
    if not lowered.startswith("select"):
        raise QueryError("Only SELECT queries are allowed")
    if any(kw in lowered for kw in _SQL_FORBIDDEN):
        raise QueryError("Query contains a disallowed keyword")

    conn = _build_notes_db()
    try:
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(MAX_ROWS)
    except sqlite3.Error as e:
        raise QueryError(str(e))
    finally:
        conn.close()
    return cols, rows


def parse_simple_query(text: str) -> dict:
    params: dict[str, str] = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        params[key.strip().lower()] = val.strip()
    return params


def _snippet(text: str, needle: str, context: int = 50) -> str:
    """Return a short excerpt of `text` centered on the first occurrence
    of `needle` (case-insensitive), so search results show *where* a
    phrase showed up rather than dumping the whole note body."""
    if not text or not needle:
        return ""
    idx = text.lower().find(needle.lower())
    if idx == -1:
        return ""
    start = max(0, idx - context)
    end = min(len(text), idx + len(needle) + context)
    excerpt = " ".join(text[start:end].split())  # collapse newlines/whitespace
    prefix = "\u2026" if start > 0 else ""
    suffix = "\u2026" if end < len(text) else ""
    return f"{prefix}{excerpt}{suffix}"


def run_simple_query(params: dict) -> tuple[list[str], list[tuple[str, list[str]]]]:
    notes = store.list_notes()

    cls = params.get("class")
    if cls:
        notes = [n for n in notes if n["class"] == cls]

    tag = params.get("tag")
    if tag:
        notes = [n for n in notes if tag in n["tags"]]

    # Cache full note bodies as we touch them, since `contains` and the
    # `snippet`/`body` columns all need the same full-text lookups.
    body_cache: dict[str, str] = {}

    def _get_body(slug: str) -> str:
        if slug not in body_cache:
            full = store.get_note(slug)
            body_cache[slug] = (full or {}).get("body", "") or ""
        return body_cache[slug]

    contains = params.get("contains")
    if contains:
        needle = contains.lower()
        notes = [
            n for n in notes
            if needle in (n.get("title") or "").lower() or needle in _get_body(n["slug"]).lower()
        ]

    sort_spec = params.get("sort", "-date")
    reverse = sort_spec.startswith("-")
    sort_key = sort_spec.lstrip("-") or "date"
    if sort_key in ("title", "class", "date", "mtime", "slug"):
        notes.sort(key=lambda n: n.get(sort_key) or "", reverse=reverse)

    try:
        limit = int(params.get("limit", DEFAULT_LIMIT) or DEFAULT_LIMIT)
    except ValueError:
        raise QueryError(f"Invalid limit: {params.get('limit')!r}")
    notes = notes[: max(0, min(limit, MAX_ROWS))]

    columns_param = params.get("columns")
    if columns_param:
        columns = [c.strip() for c in columns_param.split(",") if c.strip()]
    elif contains:
        # A search naturally wants to show *why* each note matched.
        columns = ["title", "class", "date", "snippet"]
    else:
        columns = ["title", "class", "date", "tags"]

    rows = []
    for n in notes:
        full_meta = None
        row = []
        for col in columns:
            if col == "tags":
                row.append(", ".join(n.get("tags", [])))
            elif col in ("title", "class", "date", "slug"):
                row.append(str(n.get(col, "")))
            elif col == "body":
                row.append(_get_body(n["slug"]))
            elif col == "snippet":
                needle = contains or ""
                snippet = _snippet(_get_body(n["slug"]), needle) if needle else ""
                if not snippet and needle and needle.lower() in (n.get("title") or "").lower():
                    snippet = n.get("title", "")
                row.append(snippet)
            else:
                if full_meta is None:
                    full = store.get_note(n["slug"])
                    full_meta = (full or {}).get("metadata", {}) or {}
                row.append(str(full_meta.get(col, "")))
        rows.append((n["slug"], row))

    return columns, rows


def _table_html(columns: list[str], rows: list[list[str]], slugs: list[str] | None) -> str:
    if not rows:
        return '<div class="query-empty">No results.</div>'

    display_cols = columns
    slug_col_idx = None
    if slugs is None and "slug" in [c.lower() for c in columns]:
        slug_col_idx = [c.lower() for c in columns].index("slug")

    thead = "".join(f"<th>{html_lib.escape(str(c))}</th>" for c in display_cols)
    body_rows = []
    for i, row in enumerate(rows):
        row_slug = slugs[i] if slugs is not None else (row[slug_col_idx] if slug_col_idx is not None else None)
        cells = []
        for j, val in enumerate(row):
            text = html_lib.escape(str(val))
            if display_cols[j].lower() == "title" and row_slug:
                text = f'<a href="/note/{row_slug}">{text}</a>'
            cells.append(f"<td>{text}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return (
        '<table class="query-table"><thead><tr>' + thead + "</tr></thead>"
        "<tbody>" + "".join(body_rows) + "</tbody></table>"
    )


def render_query_block(kind: str, body: str) -> str:
    """Run a `query` or `sql` block and return an HTML fragment (table or
    error/empty message) suitable for splicing into rendered note HTML."""
    kind = (kind or "").strip().lower()
    try:
        if kind == "sql":
            cols, raw_rows = run_sql(body)
            rows = [list(r) for r in raw_rows]
            return _table_html(cols, rows, slugs=None)
        else:
            cols, slug_rows = run_simple_query(parse_simple_query(body))
            slugs = [s for s, _ in slug_rows]
            rows = [r for _, r in slug_rows]
            return _table_html(cols, rows, slugs=slugs)
    except QueryError as e:
        return f'<div class="query-error">Query error: {html_lib.escape(str(e))}</div>'
