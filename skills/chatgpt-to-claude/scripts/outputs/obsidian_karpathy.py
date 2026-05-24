#!/usr/bin/env python3
"""
Obsidian Karpathy LLM Wiki vault — full pattern with raw/, wiki/, CLAUDE.md,
index.md, log.md following https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

Usage:
    python3 parse_export.py <dir> | python3 categorize.py | \\
        python3 outputs/obsidian_karpathy.py <vault-dir>

Output:
    <vault-dir>/
        CLAUDE.md        — schema / agent instructions
        Home.md          — entry point
        index.md         — wiki page catalog
        log.md           — append-only activity log
        raw/             — immutable source notes (one .md per conversation)
            <category>/
                <date> - <title>.md
        wiki/            — synthesized knowledge pages (empty, to grow over time)
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


def safe_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", title).strip()
    return name[:60]


def tag_from(cat: str) -> str:
    return (cat.lower()
            .replace(" & ", "-")
            .replace(" ", "-")
            .replace("#", "sharp"))


CLAUDE_MD = """# CLAUDE.md — LLM Wiki Schema

This file is the schema for a personal LLM wiki, following Andrej Karpathy's
LLM Wiki pattern (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Directory structure

```
/raw/        — Immutable source documents. Never modify these.
/wiki/       — LLM-generated synthesized pages. You own this layer.
index.md     — Catalog of all wiki pages with one-line summaries.
log.md       — Append-only chronological record of ingests/queries/lints.
CLAUDE.md    — This schema file. Co-evolve as the wiki grows.
Home.md      — Human-facing entry point.
```

## Wiki page conventions

Every wiki page should have YAML frontmatter:

```yaml
---
tags: [tag1, tag2]
created: YYYY-MM-DD
status: seed | growing | evergreen
sources: N
---
```

Use `[[WikiLinks]]` to link related pages. Every page should link to at least 2 others.

## Operations

### Ingest
When given a new source, read it, write/update wiki pages, update index.md,
append to log.md.

### Query
Read index.md, drill into relevant wiki pages, synthesize an answer with citations.
If the answer is valuable, offer to file it back as a new wiki page.

### Lint
Flag contradictions, orphan pages, missing cross-references, stale claims.
Append a lint entry to log.md.

## Log format

```
## [YYYY-MM-DD] <type> | <title>
```

Types: ingest | query | lint | restructure
"""


HOME_MD_TEMPLATE = """# My LLM Wiki

Personal knowledge base following [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
Obsidian is the IDE. The LLM is the programmer. The wiki is the codebase.

## Navigate

- [[index]] — full catalog of wiki pages
- [[log]] — history of ingests, queries, lint passes
- [[CLAUDE]] — schema and agent instructions

## Wiki (synthesized knowledge)

Empty — first ingest pass pending. Pages will appear here as wiki/ is built out.

## Raw Sources

{total} conversation notes seeded from a ChatGPT export, organized by category:

{category_table}

## Status: 🌱 Seed
Sources are loaded. Ready for first ingest pass.
"""


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: obsidian_karpathy.py <vault-dir>", file=sys.stderr)
        sys.exit(1)

    vault = Path(sys.argv[1])
    (vault / "raw").mkdir(parents=True, exist_ok=True)
    (vault / "wiki").mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    used_names: dict[str, set[str]] = {}

    for line in sys.stdin:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue

        cat = r.get("category", "Uncategorized")
        cat_dir = vault / "raw" / cat
        cat_dir.mkdir(exist_ok=True)

        base = safe_filename(r["title"])
        used = used_names.setdefault(cat, set())
        name = base
        i = 2
        while name in used:
            name = f"{base} ({i})"
            i += 1
        used.add(name)

        tag = tag_from(cat)

        with open(cat_dir / f"{name}.md", "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"tags: [{tag}]\n")
            f.write(f"created: {r['created']}\n")
            f.write("status: seed\n")
            f.write("source: chatgpt-export\n")
            f.write("---\n\n")
            f.write(f"# {r['title']}\n\n")
            for role, text in r["messages"]:
                if len(text) > 2000:
                    text = text[:2000] + "\n\n_[truncated]_"
                label = "**You:**" if role == "user" else "**Assistant:**"
                f.write(f"{label}\n\n{text}\n\n---\n\n")

        counts[cat] = counts.get(cat, 0) + 1

    # Write CLAUDE.md
    (vault / "CLAUDE.md").write_text(CLAUDE_MD, encoding="utf-8")

    # Write index.md
    today = datetime.now().strftime("%Y-%m-%d")
    index_lines = ["# Wiki Index\n",
                   "Catalog of all synthesized wiki pages. Updated on every ingest.\n",
                   "For raw source material see `/raw/`. For navigation see [[Home]].\n",
                   "\n---\n"]
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        index_lines.append(f"\n## {cat}")
        index_lines.append(f"_No wiki pages yet — {n} raw sources pending ingest from raw/{cat}/_\n")
    (vault / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

    # Write log.md
    total = sum(counts.values())
    log_content = f"""# Wiki Log

Append-only chronological record of all wiki activity.
Format: `## [YYYY-MM-DD] <type> | <title>`

---

## [{today}] restructure | Initial vault setup

- Seeded from ChatGPT export
- {total} conversation notes loaded into raw/ across {len(counts)} categories
- Wiki/ empty — ready for first ingest pass
"""
    (vault / "log.md").write_text(log_content, encoding="utf-8")

    # Write Home.md
    cat_table = "\n".join(
        f"| {cat} | {n} |" for cat, n in sorted(counts.items(), key=lambda x: -x[1])
    )
    cat_table = "| Category | Notes |\n|----------|-------|\n" + cat_table
    home = HOME_MD_TEMPLATE.format(total=total, category_table=cat_table)
    (vault / "Home.md").write_text(home, encoding="utf-8")

    print(f"Wrote Karpathy-style Obsidian vault to {vault}", file=sys.stderr)
    print(f"Total notes: {total}", file=sys.stderr)
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  [{n:4d}] {cat}", file=sys.stderr)
    print(f"\nNext: open {vault} as an Obsidian vault.", file=sys.stderr)


if __name__ == "__main__":
    main()
