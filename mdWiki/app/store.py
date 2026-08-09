"""
Handles reading/writing .md notes (with YAML frontmatter) and .yml class
definitions from disk. No database -- the filesystem is the source of truth.
"""
import os
import re
from datetime import date
from pathlib import Path

import frontmatter
import yaml

NOTES_DIR = Path(os.environ.get("NOTES_DIR", "/data/notes"))
CLASSES_DIR = Path(os.environ.get("CLASSES_DIR", "/data/classes"))

SLUG_RE = re.compile(r"[^a-z0-9\-/]+")
CLASS_NAME_RE = re.compile(r"[^a-z0-9_\-]+")

# Recognized field types for class-defined fields. Anything else read from
# disk (or submitted by a form) falls back to "text" -- this is what keeps
# older class .yml files (saved before field types existed) working
# unchanged: every field on them simply normalizes to "text", identical to
# their previous untyped behavior.
FIELD_TYPES = ["text", "textarea", "number", "date", "checkbox", "url"]
DEFAULT_FIELD_TYPE = "text"


def _normalize_fields(fields: list[dict] | None) -> list[dict]:
    out = []
    for f in fields or []:
        f = dict(f)
        f.setdefault("default", "")
        if f.get("type") not in FIELD_TYPES:
            f["type"] = DEFAULT_FIELD_TYPE
        out.append(f)
    return out


def is_truthy(value) -> bool:
    """Interpret a stored checkbox-field value (which is always a plain
    string like everything else in frontmatter) as a boolean."""
    return str(value).strip().lower() in ("true", "1", "on", "yes")


def slugify(text: str) -> str:
    text = text.lower().strip().replace(" ", "-")
    return SLUG_RE.sub("", text) or "note"


def slugify_class_name(text: str) -> str:
    text = (text or "").lower().strip().replace(" ", "-")
    return CLASS_NAME_RE.sub("", text)


# ---------- Classes (.yml schema files) ----------

def list_classes() -> list[dict]:
    """Return all class definitions, sorted by name."""
    classes = []
    if not CLASSES_DIR.exists():
        return classes
    for path in sorted(CLASSES_DIR.glob("*.yml")):
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        data.setdefault("name", path.stem)
        data["fields"] = _normalize_fields(data.get("fields"))
        classes.append(data)
    return classes


def get_class(name: str) -> dict | None:
    if not name:
        return None
    path = CLASSES_DIR / f"{name}.yml"
    if not path.exists():
        return None
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("name", name)
    data["fields"] = _normalize_fields(data.get("fields"))
    return data


def class_exists(name: str) -> bool:
    return bool(name) and (CLASSES_DIR / f"{name}.yml").exists()


def count_notes_by_class(name: str) -> int:
    return sum(1 for n in list_notes() if n["class"] == name)


def save_class(name: str, label: str, icon: str, fields: list[dict], template: str):
    """Create or overwrite a class definition. `name` must already be a
    validated slug (see slugify_class_name) — this does not re-validate it,
    since callers need to distinguish "empty after slugify" from other
    errors before reaching here."""
    CLASSES_DIR.mkdir(parents=True, exist_ok=True)
    path = CLASSES_DIR / f"{name}.yml"
    data = {
        "name": name,
        "label": label.strip() if label else name,
        "icon": icon.strip() if icon else "",
        "fields": fields,
        "template": template or "",
    }
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def delete_class(name: str) -> bool:
    path = CLASSES_DIR / f"{name}.yml"
    if not path.exists():
        return False
    path.unlink()
    return True


# ---------- Notes (.md files with YAML frontmatter) ----------

def _note_path(slug: str) -> Path:
    # notes may live in subfolders; slug can contain "/"
    return (NOTES_DIR / f"{slug}.md").resolve()


def _is_safe(path: Path) -> bool:
    try:
        path.relative_to(NOTES_DIR.resolve())
        return True
    except ValueError:
        return False


def list_notes() -> list[dict]:
    """Return lightweight metadata for every note, for the index page."""
    notes = []
    if not NOTES_DIR.exists():
        return notes
    for path in sorted(NOTES_DIR.rglob("*.md")):
        try:
            post = frontmatter.load(path)
        except Exception:
            continue
        slug = str(path.relative_to(NOTES_DIR)).removesuffix(".md")
        notes.append({
            "slug": slug,
            "title": post.metadata.get("title", slug),
            "class": post.metadata.get("class", ""),
            "tags": post.metadata.get("tags", []) or [],
            "date": post.metadata.get("date", ""),
            "mtime": path.stat().st_mtime,
        })
    return notes


def list_all_tags() -> list[str]:
    """Return every distinct tag in use across all notes, sorted."""
    tags = set()
    for n in list_notes():
        tags.update(n["tags"])
    return sorted(tags)


def get_note(slug: str):
    path = _note_path(slug)
    if not _is_safe(path) or not path.exists():
        return None
    post = frontmatter.load(path)
    return {"slug": slug, "metadata": post.metadata, "body": post.content}


def save_note(slug: str, metadata: dict, body: str):
    path = _note_path(slug)
    if not _is_safe(path):
        raise ValueError("Invalid note path")
    path.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(body, **metadata)
    with open(path, "wb") as f:
        frontmatter.dump(post, f)


def delete_note(slug: str) -> bool:
    path = _note_path(slug)
    if not _is_safe(path) or not path.exists():
        return False
    path.unlink()
    return True


def new_note_defaults(class_name: str, title: str) -> tuple[dict, str]:
    """Build starting frontmatter + body for a new note of a given class."""
    cls = get_class(class_name)
    metadata = {
        "title": title or "Untitled",
        "class": class_name or "",
        "tags": [],
        "date": date.today().isoformat(),
    }
    body = ""
    if cls:
        for field in cls.get("fields", []):
            fname = field.get("name")
            if fname and fname not in metadata:
                metadata[fname] = field.get("default", "")
        body = cls.get("template", "") or ""
    return metadata, body
