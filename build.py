#!/usr/bin/env python3
"""Build docs/index.html from recipes/*.md.

No dependencies. Run:  python3 build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
RECIPES = ROOT / "recipes"
OUT = ROOT / "docs" / "index.html"
TEMPLATE = ROOT / "template.html"


def parse_front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        meta[key.strip()] = value
    return meta, m.group(2)


RANGE = re.compile(r"(\d[\d.,½¼¾]*\s*–\s*\d[\d.,½¼¾]*)")


def isolate_ranges(s):
    """Keep '5–6' from flipping to '6–5' in right-to-left text."""
    return RANGE.sub("⁦\\1⁩", s)


def inline(s):
    s = isolate_ranges(html.escape(s, quote=False))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        s,
    )
    return s


def markdown(body):
    """Tiny markdown subset: ##/### headings, -/1. lists, | tables, paragraphs."""
    out, para, lst, table = [], [], None, []

    def flush():
        nonlocal para, lst, table
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if lst:
            tag, items = lst
            cls = ' class="ingredients"' if tag == "ul" and in_ingredients else ""
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None
        if table:
            rows = [r for r in table if not re.match(r"^\|[\s\-|:]+\|$", r)]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            head, *rest = cells
            t = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest)
            out.append(t + "</tbody></table>")
            table = []

    in_ingredients = False
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith("## "):
            flush()
            title = line[3:].strip()
            in_ingredients = title == "מצרכים"
            out.append(f"<h2>{inline(title)}</h2>")
        elif line.startswith("### "):
            flush()
            out.append(f"<h3>{inline(line[4:].strip())}</h3>")
        elif line.startswith("|"):
            if para or lst:
                flush()
            table.append(line)
        elif re.match(r"^- ", line):
            if para or table or (lst and lst[0] != "ul"):
                flush()
            lst = lst or ("ul", [])
            lst[1].append(line[2:])
        elif re.match(r"^\d+\. ", line):
            if para or table or (lst and lst[0] != "ol"):
                flush()
            lst = lst or ("ol", [])
            lst[1].append(re.sub(r"^\d+\. ", "", line))
        else:
            if lst or table:
                flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)


def main():
    recipes = []
    for path in sorted(RECIPES.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        recipes.append({
            "id": path.stem,
            "title": meta["title"],
            "emoji": meta.get("emoji", "🍽️"),
            "tags": tags,
            "time": isolate_ranges(meta.get("time", "")),
            "servings": isolate_ranges(meta.get("servings", "")),
            "source": meta.get("source", ""),
            "status": meta.get("status", "new"),
            "html": markdown(body),
            "text": re.sub(r"[#*|\-]", " ", body),
        })
    # Tried recipes first, then alphabetical.
    recipes.sort(key=lambda r: (r["status"] != "tried", r["title"]))
    data = json.dumps(recipes, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8").replace("/*__RECIPES__*/[]", data)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Built {OUT.relative_to(ROOT)} with {len(recipes)} recipes")


if __name__ == "__main__":
    main()
