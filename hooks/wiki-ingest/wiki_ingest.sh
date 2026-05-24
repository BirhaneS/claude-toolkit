#!/usr/bin/env bash
# LLM Wiki ingest hook — fires on Claude Code Stop.
#
# Extracts the session transcript and hands it to claude CLI for categorization
# and note creation in a Karpathy-style LLM Wiki vault.
#
# Configuration via environment variables (set in ~/.claude/settings.json env):
#   WIKI_VAULT       — Absolute path to vault root (required)
#   WIKI_CATEGORIES  — Newline-separated list of category names (optional)
#                      If unset, claude picks freely.
#
# Or override at the top of this script.

set -euo pipefail

# === Config ===
VAULT="${WIKI_VAULT:-/mnt/c/code/mine}"
PROJECTS="$HOME/.claude/projects"
CLAUDE="${CLAUDE_CLI:-$HOME/.local/bin/claude}"

# Default categories (override via WIKI_CATEGORIES env var)
DEFAULT_CATEGORIES="AI & Machine Learning
Business & Career
Personal Finance & Tax
Health & Medical
Home & DIY
Family & Parenting
Education
Software Development"

CATEGORIES="${WIKI_CATEGORIES:-$DEFAULT_CATEGORIES}"

# === Sanity checks ===
[ ! -d "$VAULT" ] && exit 0
[ ! -x "$CLAUDE" ] && exit 0

# === Read session_id from hook stdin ===
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)
[ -z "$SESSION_ID" ] && exit 0

# === Find the transcript file ===
TRANSCRIPT=$(find "$PROJECTS" -name "${SESSION_ID}.jsonl" 2>/dev/null | head -1)
[ -z "$TRANSCRIPT" ] && exit 0

# === Extract user + assistant messages from the JSONL ===
CONVERSATION=$(python3 - "$TRANSCRIPT" <<'PYEOF'
import json, sys

path = sys.argv[1]
messages = []
with open(path, encoding="utf-8") as f:
    for line in f:
        try:
            e = json.loads(line)
            if e.get("type") not in ("user", "assistant"):
                continue
            content = e.get("message", {}).get("content", "")
            if isinstance(content, list):
                text = " ".join(
                    b.get("text", "") for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                ).strip()
            elif isinstance(content, str):
                text = content.strip()
            else:
                continue
            if not text or "<local-command" in text or len(text) < 10:
                continue
            role = "You" if e["type"] == "user" else "Assistant"
            messages.append(f"[{role}]: {text[:600]}")
        except Exception:
            continue

# Skip trivial sessions
if len(messages) >= 4:
    print("\n\n".join(messages[:16]))
PYEOF
)

[ -z "$CONVERSATION" ] && exit 0

DATE=$(date +%Y-%m-%d)
CATEGORY_LIST=$(echo "$CATEGORIES" | sed 's/^/- /')

# === Hand off to claude CLI ===
echo "$CONVERSATION" | "$CLAUDE" -p "$(cat <<PROMPT
You are maintaining a personal LLM wiki vault at $VAULT following Karpathy's LLM wiki pattern.

The vault has these raw source categories under $VAULT/raw/:
$CATEGORY_LIST

You will be given a Claude Code conversation. Do the following:

1. Pick the best matching category from the list above. If none fit, create a new folder name.
2. Create a title (5-7 words).
3. Write a 2-3 sentence summary.
4. Create the note file at: $VAULT/raw/<category>/<date> - <title>.md
   Use this frontmatter format:
   ---
   tags: [<category-kebab-case>]
   created: $DATE
   status: seed
   source: claude-code-session
   session_id: $SESSION_ID
   ---

   # <title>

   ## Summary
   <summary>

   ## Conversation
   <include the key exchanges, truncated to essentials>

5. Append this entry to $VAULT/log.md (append only, never overwrite):
   ## [$DATE] ingest | <title>
   - **Category:** <category>
   - **File:** raw/<category>/<filename>

Do not explain. Just create the files and output one line: "Wiki: <title> → <category>"
PROMPT
)" --dangerously-skip-permissions 2>/dev/null

exit 0
