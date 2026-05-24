---
name: chatgpt-to-claude
description: Migrate a ChatGPT conversation export into a structured knowledge base for use with Claude. Use when the user has downloaded their ChatGPT data export (a folder with conversations-NNN.json files) and wants to convert it into categorized markdown notes, an Obsidian vault, or a Karpathy-style LLM Wiki.
---

# ChatGPT to Claude

Convert a ChatGPT data export into a knowledge base you can work with in Claude.

## When to use

The user has:
- Downloaded their ChatGPT data export (from ChatGPT Settings → Data Controls → Export data)
- Wants to convert it into a structured, searchable, persistent format

## What this skill does

1. Locates and parses the ChatGPT export JSON files
2. Categorizes conversations using keyword matching
3. Generates output in one of four formats (user chooses)
4. Reports what was created

## How to use

### Step 1 — Locate the export

Ask the user for the path to their ChatGPT export directory. It will contain files like:
- `conversations-000.json`, `conversations-001.json`, etc. (the conversations)
- `user.json`, `message_feedback.json` (metadata, not needed)
- Various `.dat` files (attachments, not used)

If the user is on Windows + WSL, paths like `C:\Users\...` map to `/mnt/c/Users/...`.

### Step 2 — Show categories and confirm

Read `scripts/categorize.py` to see the default categories. Show the user the list and ask if they want to:
- Use the defaults
- Customize the categories (edit the script or pass overrides)
- Skip auto-categorization (just flat output)

### Step 3 — Pick output format

Ask which format they want:

| Option | When to choose |
|--------|----------------|
| **`plain`** | Flat folder of `<title>.md` files. No structure. Quick dump. |
| **`categorized`** | Folders by topic with markdown notes inside. Good middle ground. |
| **`obsidian-basic`** | Categorized + YAML frontmatter + `[[wikilinks]]`. For Obsidian users who want a simple vault. |
| **`obsidian-karpathy`** | Full Karpathy LLM Wiki: `raw/`, `wiki/`, `CLAUDE.md` schema, `index.md`, `log.md`. For users who want a persistent, AI-maintainable knowledge base. |

### Step 4 — Run the migration

Use `scripts/parse_export.py` to extract conversations, then invoke the chosen output script from `scripts/outputs/`:

```bash
python3 scripts/parse_export.py <export-dir> | \
  python3 scripts/outputs/<format>.py <target-dir>
```

Or call them directly — the output scripts read parsed JSON from stdin and write files to the target directory.

### Step 5 — Report

After completion, tell the user:
- How many conversations were processed
- How many landed in each category
- Where the output is
- What to do next (for Obsidian formats: open the folder as a vault; for Karpathy: also set up the auto-ingest hook — see `hooks/wiki-ingest/` if available)

## Edge cases

- **Blank "New chat" titles** — skip these; they're empty sessions with no useful content
- **Very long conversations** — truncate individual messages to ~2000 chars; full content stays in the raw JSON
- **Non-English titles** (Amharic, Vietnamese, etc.) — preserve as-is, don't transliterate
- **Duplicate titles** — disambiguate with a date suffix

## Customizing categories

The default categories in `scripts/categorize.py` are general-purpose. To customize:

1. Read the user's actual conversation titles first
2. Suggest a tailored category list based on what's in their export
3. Update the `CATEGORIES` dict in `scripts/categorize.py` before running

This is the most important step — the right categories make the output useful.
