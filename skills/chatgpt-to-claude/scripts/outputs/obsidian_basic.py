#!/usr/bin/env python3
"""
Obsidian basic vault — categorized + YAML frontmatter + tags.

Usage:
    python3 parse_export.py <dir> | python3 categorize.py | \\
        python3 outputs/obsidian_basic.py <vault-dir>

The output is a valid Obsidian vault. Open <vault-dir> as a vault in Obsidian.
"""

import json
import re
import sys
from pathlib import Path


def safe_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", title).strip()
    return name[:80]


def tag_from(cat: str) -> str:
    return (cat.lower()
            .replace(" & ", "-")
            .replace(" ", "-")
            .replace("#", "sharp"))


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: obsidian_basic.py <vault-dir>", file=sys.stderr)
        sys.exit(1)

    vault = Path(sys.argv[1])
    vault.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    used_names: dict[str, set[str]] = {}

    for line in sys.stdin:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue

        cat = r.get("category", "Uncategorized")
        cat_dir = vault / cat
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
            f.write("source: chatgpt-export\n")
            f.write("---\n\n")
            f.write(f"# {r['title']}\n\n")
            for role, text in r["messages"]:
                if len(text) > 2000:
                    text = text[:2000] + "\n\n_[truncated]_"
                label = "**You:**" if role == "user" else "**Assistant:**"
                f.write(f"{label}\n\n{text}\n\n---\n\n")

        counts[cat] = counts.get(cat, 0) + 1

    # Write a Home.md
    with open(vault / "Home.md", "w", encoding="utf-8") as f:
        f.write("# Home\n\n")
        f.write("ChatGPT conversation archive, organized by category.\n\n")
        f.write("## Categories\n\n")
        for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
            f.write(f"- **{cat}** ({n} notes)\n")

    print(f"Wrote Obsidian vault to {vault}", file=sys.stderr)
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  [{n:4d}] {cat}", file=sys.stderr)
    print("\nOpen this folder as a vault in Obsidian to use it.", file=sys.stderr)


if __name__ == "__main__":
    main()
