#!/usr/bin/env python3
"""
Categorized output — folders by topic with markdown notes inside.

Usage:
    python3 parse_export.py <dir> | python3 categorize.py | \\
        python3 outputs/categorized.py <target-dir>
"""

import json
import re
import sys
from pathlib import Path


def safe_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", title).strip()
    return name[:80]


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: categorized.py <target-dir>", file=sys.stderr)
        sys.exit(1)

    target = Path(sys.argv[1])
    target.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    used_names: dict[str, set[str]] = {}

    for line in sys.stdin:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue

        cat = r.get("category", "Uncategorized")
        cat_dir = target / cat
        cat_dir.mkdir(exist_ok=True)

        base = safe_filename(r["title"])
        used = used_names.setdefault(cat, set())
        name = base
        i = 2
        while name in used:
            name = f"{base} ({i})"
            i += 1
        used.add(name)

        with open(cat_dir / f"{name}.md", "w", encoding="utf-8") as f:
            f.write(f"# {r['title']}\n\n")
            f.write(f"_{r['created']} · {cat}_\n\n")
            for role, text in r["messages"]:
                label = "**You:**" if role == "user" else "**Assistant:**"
                f.write(f"{label}\n\n{text}\n\n---\n\n")

        counts[cat] = counts.get(cat, 0) + 1

    print(f"Wrote files to {target}", file=sys.stderr)
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  [{n:4d}] {cat}", file=sys.stderr)


if __name__ == "__main__":
    main()
