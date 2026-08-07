"""
Static content for the in-app /help page. Kept as plain markdown (rendered
with the same MD_EXTENSIONS as notes) rather than hand-written HTML so it's
easy to edit, and kept in its own module so main.py doesn't get cluttered.

Note: this is rendered with plain markdown.markdown(), NOT through
query_engine's ```query/```sql interceptor -- so the example blocks below
show up as inert code samples instead of actually running as live queries.
"""

HELP_MARKDOWN = r"""
# How to use this wiki

## Notes

Every note is a plain `.md` file with YAML frontmatter (title, class, tags,
date, plus whatever fields its class defines) and a markdown body. Click
**+ New Note**, give it a title and (optionally) a class, and you're taken
straight to the editor with a live preview alongside what you type.

## Classes

A **class** is a reusable schema: a set of extra fields, an icon, and a
starter template for new notes. Manage them from **Manage Classes** in the
top nav -- add a `book` class with `author`/`rating` fields, a `meeting`
class with `attendees`, whatever fits how you organize things.

**Changing a note's class:** open a note and hit **Edit**. The Class
dropdown can be changed at any time, even long after the note was created.
Switching it swaps in that class's fields immediately (no page reload).
Saving drops any fields from the old class that the new class doesn't
define -- only the current class's fields are kept.

## Embedded queries

Drop a fenced code block into any note's body using `query` or `sql` as
the language tag. It's replaced with a results table when the note is
viewed (and live in the edit page's preview pane too).

### Simple `query` blocks

Plain `key: value` lines, one per line:

````
```query
class: book
tag: fiction
sort: -rating
limit: 10
columns: title, author, rating
```
````

Supported keys, all optional:

| Key | What it does |
|---|---|
| `class` | Only notes of this class |
| `tag` | Only notes with this tag |
| `contains` | Case-insensitive text search across each note's title **and full markdown body** -- headings, paragraphs, everything |
| `sort` | Field to sort by; prefix with `-` for descending (e.g. `-date`). Defaults to `-date` |
| `limit` | Max rows returned. Defaults to 50, capped at 200 |
| `columns` | Comma-separated columns to display. Defaults to `title, class, date, tags` -- or `title, class, date, snippet` automatically when `contains` is set |

A `snippet` column (used automatically with `contains`, or add it to
`columns` yourself) shows a short excerpt of matched text in context,
rather than dumping the whole note body into the table.

**Search example** -- find every note mentioning a phrase, wherever it
appears in the note:

````
```query
contains: raspberry pi
```
````

### `sql` blocks

Real SQL, read-only, against a `notes` table rebuilt from your files every
time the note renders:

````
```sql
SELECT title, author, rating FROM notes WHERE class = 'book' AND rating >= 4 ORDER BY rating DESC
```
````

Columns available: `slug`, `title`, `class`, `tags`, `date`, `body` (the
full markdown text), plus every custom field any class defines (`author`,
`rating`, `attendees`, ...) -- so you can query a field without needing to
know which class owns it.

Search headings and paragraphs directly with `LIKE`:

````
```sql
SELECT slug, title FROM notes WHERE body LIKE '%raspberry pi%'
```
````

Include `slug` in a SQL query's `SELECT` list and the `title` column
auto-links back to that note.

**Safety notes:**

- Only `SELECT` statements run. Anything else (`PRAGMA`, `ATTACH`,
  `INSERT`, `DROP`, ...) is rejected and shown as an inline error instead
  of crashing the page.
- The database connection itself is set read-only (`PRAGMA query_only`),
  and it's rebuilt fresh in memory for every render -- nothing a query
  does ever touches the files on disk.
- Results are capped at 200 rows.

## Search & filters

The home page's search box matches title, slug, and tags across all
notes. The sidebar lets you filter by class or tag with one click. For
searching inside note *content* -- headings and paragraphs, not just
metadata -- use a `contains:` query block as described above.

## Tips

- Tags are comma-separated in the editor (`fiction, scifi`).
- The `data/notes/` and `data/classes/` folders are plain files on disk --
  edit them directly with any text editor, or sync with git/Syncthing/etc.
  and the app picks up changes on next page load.
- Deleting a class doesn't delete its notes -- they keep their `class:`
  value in frontmatter but lose the extra fields/template until you
  recreate the class or reassign them.
"""
