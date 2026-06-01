# Travel Planner Plugin — Handoff 2 (Local Claude Code Session)

## Goal
Install the travel-planner Claude Code plugin from the GitHub marketplace at
`cookiesncache/travel-planner`, then iterate on it over time.

## What's already done
- `cookiesncache/travel-planner` on GitHub has the full plugin structure on `main`:
  ```
  .claude-plugin/plugin.json        ← plugin manifest (name, version, description)
  .claude-plugin/marketplace.json   ← marketplace catalog (added in previous session)
  skills/travel-workflow/SKILL.md   ← the skill
  skills/travel-workflow/references/*.md
  README.md
  ROADMAP.md
  ```
- The `marketplace.json` registers this repo as a marketplace with `"source": "./"`,
  pointing to the plugin at the repo root. Both files are on `main`.

## What to do in this session

### 1. Check your Claude Code version
```bash
claude --version
```
The `/plugin` command requires v2.1.143 or newer. Update if needed before continuing.

### 2. Install the marketplace and plugin
Run these in the Claude Code chat (local session):
```
/plugin marketplace add cookiesncache/travel-planner
/plugin install travel-planner@travel-planner-marketplace
```

### 3. If install fails
Run validation on a local clone to get specific error output:
```bash
git clone https://github.com/cookiesncache/travel-planner
claude plugin validate ./travel-planner
```
Paste the output — it will give a specific error rather than the generic "Failed to install".

### 4. Using the plugin once installed
Invoke as `/travel-planner:travel-workflow` or just mention a trip — it auto-triggers.
Requires a task manager (Todoist etc.) and calendar connector. Email is optional.

## Iteration loop (once installed and working)
1. Edit `skills/travel-workflow/SKILL.md` or `references/*.md`
2. Bump `version` in `.claude-plugin/plugin.json` (e.g. `0.1.0` → `0.1.1`)
3. Commit and push to `main`
4. Refresh in Claude Code:
   ```
   /plugin marketplace update travel-planner-marketplace
   /plugin uninstall travel-planner@travel-planner-marketplace
   /plugin install travel-planner@travel-planner-marketplace
   ```

## What we learned / ruled out
- The web-based Claude Code session (code.claude.com) does **not** support `/plugin` commands —
  `"/plugin isn't available in this environment"` — so plugin management must be done locally.
- The consumer Claude desktop app (claude.ai/download) is a separate product and does not
  support this plugin system.
- The `/plugin` command is built into **Claude Code CLI / Claude Code desktop app** only.
- Log files for Claude Code on Windows: `%LOCALAPPDATA%\Claude\logs\` or for MSIX installs
  `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\`

## References
- Plugin marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Plugins reference: https://code.claude.com/docs/en/plugins-reference
- Discover and install: https://code.claude.com/docs/en/discover-plugins
