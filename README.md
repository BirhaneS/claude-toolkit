# claude-toolkit

Personal collection of Claude Code skills, hooks, and configs.

## Skills

### `chatgpt-to-claude`
Migrate a ChatGPT data export into a structured knowledge base. Supports four
output formats:

- **Plain markdown** — flat folder of notes
- **Categorized** — folders by topic
- **Obsidian (basic)** — vault with frontmatter and tags
- **Obsidian (Karpathy LLM Wiki)** — full pattern with `raw/`, `wiki/`, schema, index, log

See [`skills/chatgpt-to-claude/SKILL.md`](skills/chatgpt-to-claude/SKILL.md).

## Installation

To use the skills in Claude Code:

```bash
# Clone this repo
git clone https://github.com/BirhaneS/claude-toolkit.git ~/code/claude-toolkit

# Symlink the skills into your Claude config
mkdir -p ~/.claude/skills
ln -s ~/code/claude-toolkit/skills/chatgpt-to-claude ~/.claude/skills/chatgpt-to-claude
```

Then in any Claude Code session, the skill will be available — invoke with
`/chatgpt-to-claude` or let Claude discover it automatically when relevant.
