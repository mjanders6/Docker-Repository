"""
Two small markdown pre-processing passes applied to a note's body before
python-markdown ever sees it (see main.render_markdown):

  - Wikilinks:  [[Note Title]]  or  [[Note Title|display text]]
    Resolved against existing notes by slug or title (case-insensitive).
    A match links straight to the note; no match renders a "create this
    note" link that goes through the /link/{slug} route, which creates an
    empty note (title = the link text) and drops the user into the editor
    -- the same "link now, write later" flow most wiki tools use.

  - Task lists:  - [ ] do the thing   /   - [x] done
    Rendered as *live* checkboxes (not disabled), each tagged with its
    0-based position among all task items in the note
    (data-task-index="N"). Clicking one in note view POSTs to
    /note/{slug}/toggle-task, which flips the matching marker in the
    stored file via toggle_task() below. In the editor's preview pane,
    the same index is used client-side to flip the marker directly in the
    textarea (see edit.html) since the note may not be saved yet.

Both passes skip the contents of ``` fenced code blocks, so documentation
that *shows* `[[...]]` or `- [ ]` syntax as an example doesn't get
rewritten into a live link/checkbox.
"""
import html as html_lib
import re
from urllib.parse import quote

from . import store

WIKILINK_RE = re.compile(r"\[\[([^\]|\n]+)(?:\|([^\]\n]+))?\]\]")
TASK_RE = re.compile(r"^(\s*[-*+] )\[([ xX])\] (.*)$", re.MULTILINE)

# Splits text into alternating [non-code, code, non-code, code, ...] parts
# on generic ``` fences, so callers can transform only the non-code parts.
_FENCE_RE = re.compile(r"(```.*?```)", re.DOTALL)


def _map_outside_fences(text: str, fn) -> str:
    parts = _FENCE_RE.split(text or "")
    return "".join(fn(p) if i % 2 == 0 else p for i, p in enumerate(parts))


# ---------- Wikilinks ----------

def resolve_wikilink(target: str) -> tuple[str, bool]:
    """Return (slug, exists) for a wikilink target, matching against an
    existing note's slug first, then title (case-insensitive)."""
    target = (target or "").strip()
    if not target:
        return "", False
    candidate_slug = store.slugify(target)
    if store.get_note(candidate_slug):
        return candidate_slug, True
    lowered = target.lower()
    for n in store.list_notes():
        if n["slug"] == target or n["title"].strip().lower() == lowered:
            return n["slug"], True
    return candidate_slug, False


def render_wikilinks(text: str) -> str:
    def _sub_segment(segment: str) -> str:
        def _repl(m: re.Match) -> str:
            target = m.group(1).strip()
            label = (m.group(2) or target).strip()
            label_html = html_lib.escape(label)
            slug, exists = resolve_wikilink(target)
            if not slug:
                return m.group(0)
            if exists:
                return f'<a class="wikilink" href="/note/{slug}">{label_html}</a>'
            create_href = f"/link/{slug}?title={quote(target)}"
            return (
                f'<a class="wikilink wikilink-new" href="{create_href}" '
                f'title="This note doesn\u2019t exist yet \u2014 click to create it">'
                f"{label_html}</a>"
            )
        return WIKILINK_RE.sub(_repl, segment)

    return _map_outside_fences(text, _sub_segment)


# ---------- Task lists ----------

def render_tasks(text: str) -> str:
    counter = [0]

    def _sub_segment(segment: str) -> str:
        def _repl(m: re.Match) -> str:
            prefix, mark, rest = m.groups()
            idx = counter[0]
            counter[0] += 1
            checked_attr = " checked" if mark.lower() == "x" else ""
            return (
                f'{prefix}<input type="checkbox" class="task-checkbox" '
                f'data-task-index="{idx}"{checked_attr}> '
                f'<span class="task-text">{rest}</span>'
            )
        return TASK_RE.sub(_repl, segment)

    return _map_outside_fences(text, _sub_segment)


def toggle_task(text: str, index: int) -> tuple[str, bool]:
    """Flip the [ ]/[x] marker of the `index`-th task item (0-based, same
    counting order as render_tasks) in raw markdown `text`. Returns
    (new_text, found)."""
    counter = [0]
    found = [False]

    def _sub_segment(segment: str) -> str:
        def _repl(m: re.Match) -> str:
            prefix, mark, rest = m.groups()
            if counter[0] == index:
                found[0] = True
                counter[0] += 1
                new_mark = " " if mark.lower() == "x" else "x"
                return f"{prefix}[{new_mark}] {rest}"
            counter[0] += 1
            return m.group(0)
        return TASK_RE.sub(_repl, segment)

    new_text = _map_outside_fences(text, _sub_segment)
    return new_text, found[0]
