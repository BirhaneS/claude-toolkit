#!/usr/bin/env python3
"""
Parse a ChatGPT data export directory into a normalized JSON stream.

Usage:
    python3 parse_export.py <export-dir>

Emits JSON to stdout, one conversation per line:
    {"title": "...", "created": "YYYY-MM-DD", "messages": [["user","..."], ["assistant","..."]]}

Skips blank "New chat" sessions and conversations with no extractable messages.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def walk_messages(mapping: dict, current_node_id: str) -> list[tuple[str, str]]:
    """Walk the conversation tree from current_node back to root."""
    chain = []
    node_id = current_node_id
    visited = set()
    while node_id and node_id not in visited:
        visited.add(node_id)
        node = mapping.get(node_id)
        if not node:
            break
        msg = node.get("message")
        if msg:
            parts = msg.get("content", {}).get("parts", [])
            text = "\n".join(p for p in parts if isinstance(p, str)).strip()
            role = msg.get("author", {}).get("role", "")
            if text and role in ("user", "assistant"):
                chain.append((role, text))
        node_id = node.get("parent")
    chain.reverse()
    return chain


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: parse_export.py <export-dir>", file=sys.stderr)
        sys.exit(1)

    export_dir = Path(sys.argv[1])
    if not export_dir.is_dir():
        print(f"Not a directory: {export_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(export_dir.glob("conversations-*.json"))
    if not files:
        # Fall back to a single conversations.json (older export format)
        single = export_dir / "conversations.json"
        if single.exists():
            files = [single]

    if not files:
        print(f"No conversation files found in {export_dir}", file=sys.stderr)
        sys.exit(1)

    total = 0
    emitted = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for convo in data:
            total += 1
            title = (convo.get("title") or "").strip()
            if not title or title.lower() == "new chat":
                continue

            messages = walk_messages(
                convo.get("mapping", {}),
                convo.get("current_node", ""),
            )
            if not messages:
                continue

            ts = convo.get("create_time")
            date_str = (
                datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                if ts else "1970-01-01"
            )

            print(json.dumps({
                "title": title,
                "created": date_str,
                "messages": messages,
            }, ensure_ascii=False))
            emitted += 1

    print(f"Parsed {total} conversations, emitted {emitted} (skipped blanks/empty)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
