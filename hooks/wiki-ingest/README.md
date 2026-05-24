# wiki-ingest hook

Auto-ingest every Claude Code session into a Karpathy-style LLM Wiki vault.

When a session ends, this hook:
1. Extracts the conversation transcript
2. Pipes it to `claude` CLI for categorization
3. Creates a markdown note in `<vault>/raw/<category>/<date> - <title>.md`
4. Appends an entry to `<vault>/log.md`

## Requirements

- A vault already set up following the Karpathy LLM Wiki pattern
  (see the [`chatgpt-to-claude`](../../skills/chatgpt-to-claude) skill for one-shot vault setup)
- `claude` CLI installed and authenticated
- `python3` available

## Install

1. Symlink (or copy) the script:
   ```bash
   ln -s ~/code/claude-toolkit/hooks/wiki-ingest/wiki_ingest.sh ~/.claude/wiki_ingest.sh
   chmod +x ~/code/claude-toolkit/hooks/wiki-ingest/wiki_ingest.sh
   ```

2. Add the hook to `~/.claude/settings.json`:
   ```json
   {
     "hooks": {
       "Stop": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "bash ~/.claude/wiki_ingest.sh",
               "timeout": 60,
               "statusMessage": "Saving to wiki..."
             }
           ]
         }
       ]
     },
     "env": {
       "WIKI_VAULT": "/path/to/your/vault"
     }
   }
   ```

3. Restart Claude Code for the hook to take effect.

## Configuration

Override via environment variables in `~/.claude/settings.json` under `env`:

| Variable | Purpose | Default |
|----------|---------|---------|
| `WIKI_VAULT` | Absolute path to vault root | `/mnt/c/code/mine` |
| `WIKI_CATEGORIES` | Newline-separated category names | A general-purpose default list |
| `CLAUDE_CLI` | Path to `claude` binary | `$HOME/.local/bin/claude` |

Example with custom categories:
```json
{
  "env": {
    "WIKI_VAULT": "/home/me/notes",
    "WIKI_CATEGORIES": "Work\nPersonal\nResearch\nIdeas"
  }
}
```

## Behavior

- Sessions with fewer than 4 real exchanges are skipped (trivial chats)
- The hook is fail-silent — if anything goes wrong, the session ends normally
- The vault must already exist; the hook won't create the structure for you
- Uses `--dangerously-skip-permissions` since `claude -p` runs non-interactively

## Disabling

Remove the `Stop` hook block from `~/.claude/settings.json` or run `/hooks` in
Claude Code to manage it interactively.
