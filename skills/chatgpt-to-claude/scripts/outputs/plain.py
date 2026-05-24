#!/usr/bin/env python3
"""
Plain markdown output — flat folder of <title>.md files.

Usage:
    python3 parse_export.py <dir> | python3 outputs/plain.py <target-dir>
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
        print("Usage: plain.py <target-dir>", file=sys.stderr)
        sys.exit(1)

    target = Path(sys.argv[1])
    target.mkdir(parents=True, exist_ok=True)

    count = 0
    used_names: set[str] = set()
    for line in sys.stdin:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue

        base = safe_filename(r["title"])
        name = base
        i = 2
        while name in used_names:
            name = f"{base} ({i})"
            i += 1
        used_names.add(name)

        with open(target / f"{name}.md", "w", encoding="utf-8") as f:
            f.write(f"# {r['title']}\n\n")
            f.write(f"_{r['created']}_\n\n")
            for role, text in r["messages"]:
                label = "**You:**" if role == "user" else "**Assistant:**"
                f.write(f"{label}\n\n{text}\n\n---\n\n")
        count += 1

    print(f"Wrote {count} files to {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
