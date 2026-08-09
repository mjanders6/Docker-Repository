import re
from datetime import datetime
from itertools import zip_longest

import markdown as md
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import help_content, query_engine, render_extras, store

app = FastAPI(title="Markdown Wiki")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["dt"] = lambda ts: datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
templates.env.filters["truthy"] = store.is_truthy

MD_EXTENSIONS = ["extra", "toc", "sane_lists", "fenced_code"]

_QUERY_PLACEHOLDER_RE = re.compile(r'<div class="query-placeholder" data-qidx="(\d+)"></div>')


def render_markdown(text: str) -> str:
    """Render note markdown to HTML, resolving any ```query``` / ```sql```
    fenced blocks along the way. Query blocks are pulled out and replaced
    with a raw-HTML placeholder *before* markdown processing (so python-
    markdown doesn't mangle the eventual result table), then the rendered
    query output is spliced back in afterward."""
    text = text or ""
    blocks: list[str] = []

    def _stash(m: re.Match) -> str:
        kind, body = m.group(1), m.group(2)
        blocks.append(query_engine.render_query_block(kind, body))
        idx = len(blocks) - 1
        return f'\n\n<div class="query-placeholder" data-qidx="{idx}"></div>\n\n'

    text = query_engine.QUERY_BLOCK_RE.sub(_stash, text)
    text = render_extras.render_wikilinks(text)
    text = render_extras.render_tasks(text)
    html_out = md.markdown(text, extensions=MD_EXTENSIONS)

    def _splice(m: re.Match) -> str:
        idx = int(m.group(1))
        return blocks[idx] if idx < len(blocks) else ""

    return _QUERY_PLACEHOLDER_RE.sub(_splice, html_out)


def _parse_fields_form(form) -> list[dict]:
    """Zip the repeated field_name/field_label/field_default/field_type
    inputs from a class form into the list-of-dicts shape store.save_class
    expects. Rows with a blank name are dropped (lets the "+ Add field"
    UI leave a trailing empty row without producing junk fields). Missing
    or unrecognized types fall back to "text"; itertools.zip_longest
    guards against the lists ever coming back mismatched in length."""
    names = form.getlist("field_name")
    labels = form.getlist("field_label")
    defaults = form.getlist("field_default")
    types = form.getlist("field_type")
    fields = []
    for n, l, d, t in zip_longest(names, labels, defaults, types, fillvalue=""):
        n = (n or "").strip()
        if not n:
            continue
        t = t if t in store.FIELD_TYPES else store.DEFAULT_FIELD_TYPE
        fields.append({"name": n, "label": (l or "").strip() or n, "default": d or "", "type": t})
    return fields


@app.get("/help", response_class=HTMLResponse)
def help_page(request: Request):
    """Static in-app documentation. Rendered with plain markdown (no query-
    block interception) so the example ```query/```sql snippets in the
    docs display as code instead of trying to execute."""
    html = md.markdown(help_content.HELP_MARKDOWN, extensions=MD_EXTENSIONS)
    return templates.TemplateResponse("help.html", {"request": request, "html": html})


@app.get("/", response_class=HTMLResponse)
def index(request: Request, class_filter: str = "", tag: str = "", q: str = ""):
    notes = store.list_notes()
    if class_filter:
        notes = [n for n in notes if n["class"] == class_filter]
    if tag:
        notes = [n for n in notes if tag in (n["tags"] or [])]
    if q:
        needle = q.lower()
        notes = [
            n for n in notes
            if needle in n["title"].lower()
            or needle in n["slug"].lower()
            or any(needle in t.lower() for t in n["tags"])
        ]
    notes.sort(key=lambda n: n["mtime"], reverse=True)

    classes = store.list_classes()
    class_counts = {c["name"]: store.count_notes_by_class(c["name"]) for c in classes}
    all_tags = store.list_all_tags()

    return templates.TemplateResponse("index.html", {
        "request": request, "notes": notes, "classes": classes,
        "class_counts": class_counts, "all_tags": all_tags,
        "class_filter": class_filter, "tag": tag, "q": q,
        "total_notes": len(store.list_notes()),
    })


@app.get("/note/{slug:path}/edit", response_class=HTMLResponse)
def edit_note_form(request: Request, slug: str):
    note = store.get_note(slug)
    if not note:
        return HTMLResponse(f"Note '{slug}' not found", status_code=404)
    cls = store.get_class(note["metadata"].get("class", ""))
    classes = store.list_classes()
    all_notes = [n for n in store.list_notes() if n["slug"] != slug]
    return templates.TemplateResponse("edit.html", {
        "request": request, "note": note, "cls": cls, "classes": classes,
        "values": note["metadata"], "all_notes": all_notes,
    })


@app.get("/classes/{name}/fields-partial", response_class=HTMLResponse)
def class_fields_partial(request: Request, name: str):
    """Returns just the extra-fields markup for a class, so the edit page
    can swap it in via AJAX when the user picks a different class from the
    dropdown (letting the class be changed after a note already exists)."""
    cls = store.get_class(name)
    return templates.TemplateResponse("_class_fields.html", {
        "request": request, "cls": cls, "values": {},
    })


@app.post("/note/{slug:path}/save")
async def save_note_submit(slug: str, request: Request):
    form = await request.form()
    title = form.get("title", slug)
    class_name = form.get("class", "")
    tags = [t.strip() for t in form.get("tags", "").split(",") if t.strip()]
    date_val = form.get("date", "")
    body = form.get("body", "")

    metadata = {"title": title, "class": class_name, "tags": tags, "date": date_val}
    cls = store.get_class(class_name)
    if cls:
        for field in cls.get("fields", []):
            fname = field.get("name")
            if not fname:
                continue
            if field.get("type") == "checkbox":
                # Unchecked checkboxes aren't submitted at all, so absence
                # from the form IS the "false" state, not "leave as-is".
                metadata[fname] = "true" if fname in form else "false"
            elif fname in form:
                metadata[fname] = form.get(fname, "")

    store.save_note(slug, metadata, body)
    return RedirectResponse(f"/note/{slug}", status_code=303)


@app.get("/link/{slug:path}")
def follow_wikilink(slug: str, title: str = ""):
    """Followed when a [[wikilink]] points at a note that doesn't exist
    yet -- creates an empty note (title = the link text, no class) and
    drops straight into the editor, mirroring the "link now, write later"
    flow most wiki tools use. If the note has since been created (e.g. two
    links to the same new title), just goes to it instead of overwriting."""
    existing = store.get_note(slug)
    if existing:
        return RedirectResponse(f"/note/{slug}", status_code=303)
    metadata, body = store.new_note_defaults("", title or slug)
    store.save_note(slug, metadata, body)
    return RedirectResponse(f"/note/{slug}/edit", status_code=303)


@app.post("/note/{slug:path}/toggle-task")
async def toggle_task_route(slug: str, request: Request):
    """Flip a single task-list checkbox's [ ]/[x] marker directly in the
    stored note body. `index` is the 0-based position of the checkbox
    among all task items in the note, assigned in the same left-to-right,
    top-to-bottom order render_tasks() renders them in."""
    form = await request.form()
    try:
        index = int(form.get("index", "-1"))
    except ValueError:
        index = -1
    note = store.get_note(slug)
    if not note or index < 0:
        return HTMLResponse("Invalid request", status_code=400)
    new_body, found = render_extras.toggle_task(note["body"], index)
    if not found:
        return HTMLResponse("Task not found", status_code=404)
    store.save_note(slug, note["metadata"], new_body)
    return HTMLResponse("ok")


@app.get("/note/{slug:path}", response_class=HTMLResponse)
def view_note(request: Request, slug: str):
    note = store.get_note(slug)
    if not note:
        return HTMLResponse(f"Note '{slug}' not found", status_code=404)
    cls = store.get_class(note["metadata"].get("class", ""))
    html = render_markdown(note["body"])
    return templates.TemplateResponse("view.html", {
        "request": request, "note": note, "html": html, "cls": cls,
    })


@app.get("/new", response_class=HTMLResponse)
def new_note_form(request: Request, class_name: str = ""):
    classes = store.list_classes()
    return templates.TemplateResponse("new.html", {
        "request": request, "classes": classes, "class_name": class_name,
    })


@app.post("/new")
async def create_note(request: Request):
    form = await request.form()
    title = form.get("title", "Untitled")
    class_name = form.get("class", "")
    slug = store.slugify(title)

    if store.get_note(slug):
        i = 2
        while store.get_note(f"{slug}-{i}"):
            i += 1
        slug = f"{slug}-{i}"

    metadata, body = store.new_note_defaults(class_name, title)
    store.save_note(slug, metadata, body)
    return RedirectResponse(f"/note/{slug}/edit", status_code=303)


@app.post("/note/{slug:path}/delete")
def delete_note_route(slug: str):
    store.delete_note(slug)
    return RedirectResponse("/", status_code=303)


@app.post("/preview", response_class=HTMLResponse)
async def preview(request: Request):
    form = await request.form()
    return render_markdown(form.get("body", ""))


# ---------- Classes (create / update / delete) ----------

@app.get("/classes", response_class=HTMLResponse)
def list_classes_route(request: Request):
    classes = store.list_classes()
    counts = {c["name"]: store.count_notes_by_class(c["name"]) for c in classes}
    return templates.TemplateResponse("classes.html", {
        "request": request, "classes": classes, "counts": counts,
    })


@app.get("/classes/new", response_class=HTMLResponse)
def new_class_form(request: Request):
    return templates.TemplateResponse("class_form.html", {
        "request": request, "cls": None, "is_new": True, "error": None,
    })


@app.post("/classes/new")
async def create_class_submit(request: Request):
    form = await request.form()
    raw_name = form.get("name", "")
    name = store.slugify_class_name(raw_name)
    label = form.get("label", "")
    icon = form.get("icon", "")
    template = form.get("template", "")
    fields = _parse_fields_form(form)

    error = None
    if not name:
        error = "Class name is required and must contain at least one letter, number, - or _."
    elif store.class_exists(name):
        error = f"A class named '{name}' already exists."

    if error:
        return templates.TemplateResponse("class_form.html", {
            "request": request, "is_new": True, "error": error,
            "cls": {"name": raw_name, "label": label, "icon": icon,
                    "fields": fields, "template": template},
        }, status_code=400)

    store.save_class(name, label, icon, fields, template)
    return RedirectResponse("/classes", status_code=303)


@app.get("/classes/{name}/edit", response_class=HTMLResponse)
def edit_class_form(request: Request, name: str):
    cls = store.get_class(name)
    if not cls:
        return HTMLResponse(f"Class '{name}' not found", status_code=404)
    return templates.TemplateResponse("class_form.html", {
        "request": request, "cls": cls, "is_new": False, "error": None,
    })


@app.post("/classes/{name}/save")
async def save_class_submit(name: str, request: Request):
    if not store.class_exists(name):
        return HTMLResponse(f"Class '{name}' not found", status_code=404)
    form = await request.form()
    fields = _parse_fields_form(form)
    store.save_class(name, form.get("label", ""), form.get("icon", ""), fields, form.get("template", ""))
    return RedirectResponse("/classes", status_code=303)


@app.post("/classes/{name}/delete")
def delete_class_route(name: str):
    store.delete_class(name)
    return RedirectResponse("/classes", status_code=303)
