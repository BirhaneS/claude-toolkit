# claude-toolkit

Personal collection of Claude Code skills, hooks, and configs.

## Skills

### `chatgpt-to-claude`
Migrate a ChatGPT data export into a structured knowledge base. Supports four
output formats: plain markdown, categorized folders, basic Obsidian vault, or
full Karpathy-style LLM Wiki vault.

See [`skills/chatgpt-to-claude/SKILL.md`](skills/chatgpt-to-claude/SKILL.md).

## Hooks

### `wiki-ingest`
Auto-ingest every Claude Code session into a Karpathy-style LLM Wiki vault.
Fires on the `Stop` event, categorizes the conversation via `claude` CLI, and
files it into `<vault>/raw/<category>/`.

See [`hooks/wiki-ingest/README.md`](hooks/wiki-ingest/README.md).

## Installation

```bash
# Clone the repo
git clone git@github.com:BirhaneS/claude-toolkit.git ~/code/claude-toolkit

# Install a skill (symlink into ~/.claude/skills)
mkdir -p ~/.claude/skills
ln -s ~/code/claude-toolkit/skills/chatgpt-to-claude ~/.claude/skills/chatgpt-to-claude

# Install a hook (symlink + add to ~/.claude/settings.json — see each hook's README)
```

Skills become available in any Claude Code session — invoke with `/<skill-name>`
or let Claude discover them automatically when relevant.
