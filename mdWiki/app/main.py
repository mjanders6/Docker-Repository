import re
from datetime import datetime

import markdown as md
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import query_engine, store

app = FastAPI(title="Markdown Wiki")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["dt"] = lambda ts: datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

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
    html_out = md.markdown(text, extensions=MD_EXTENSIONS)

    def _splice(m: re.Match) -> str:
        idx = int(m.group(1))
        return blocks[idx] if idx < len(blocks) else ""

    return _QUERY_PLACEHOLDER_RE.sub(_splice, html_out)


def _parse_fields_form(form) -> list[dict]:
    """Zip the repeated field_name/field_label/field_default inputs from a
    class form into the list-of-dicts shape store.save_class expects. Rows
    with a blank name are dropped (lets the "+ Add field" UI leave a
    trailing empty row without producing junk fields)."""
    names = form.getlist("field_name")
    labels = form.getlist("field_label")
    defaults = form.getlist("field_default")
    fields = []
    for n, l, d in zip(names, labels, defaults):
        n = (n or "").strip()
        if not n:
            continue
        fields.append({"name": n, "label": (l or "").strip() or n, "default": d or ""})
    return fields


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
    return templates.TemplateResponse("edit.html", {
        "request": request, "note": note, "cls": cls, "classes": classes,
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
            if fname and fname in form:
                metadata[fname] = form.get(fname, "")

    store.save_note(slug, metadata, body)
    return RedirectResponse(f"/note/{slug}", status_code=303)


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
