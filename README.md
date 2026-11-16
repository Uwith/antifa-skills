# my-skills

Personal AI agent skills, based on [runkids/my-skills](https://github.com/runkids/my-skills), managed and synced with [**skillshare**](https://github.com/runkids/skillshare).

## Local collection

This checkout includes 79 imported skills from the existing `.agents` collection, CodeBuddy, and native Pi plugin packages. Existing upstream skills are preserved. Imports use category folders, matching this repository's organization:

| Folder | Contents |
| --- | --- |
| `engineering/` | Development, architecture, debugging, Git, and Ponytail |
| `frontend/` | Existing frontend collection plus local UI skills |
| `design/` | Branding, design systems, slides, and generative art |
| `embedded/dejaos/` | DejaOS app and device workflows |
| `testing/` | Bruno, browser testing, and QA |
| `documentation/` | Documentation, editing, and knowledge tools |
| `productivity/` | Planning, handoff, and learning workflows |
| `misc/` | Supporting development tools |
| `in-progress/` | Existing local experimental skills |
| `utils/` | Skill authoring and utility skills |

When local installations differ, `.agents` takes precedence, followed by native Pi plugin skills, then CodeBuddy. All 28 other versions are retained under `_local-variants/` and excluded from sync through `.skillignore`. `utils/template-skill/` is also excluded because it is an authoring template. Both the upstream frontend prototype skill and the imported engineering prototype skill are retained in their respective categories.

[local-import.json](local-import.json) records each imported location, available upstream attribution, and SHA-256 hashes. Original installed skills were not moved or changed. Existing `.metadata.json` remains upstream Skillshare metadata; imported local files are recorded separately rather than pretending they were installed from a verified remote commit.

This collection is maintained in [Uwith/my-skills](https://github.com/Uwith/my-skills), with `runkids/my-skills` retained as the upstream repository. On this machine, Skillshare's global `sources.skills` points directly to this checkout. Use `skillshare sync` to distribute changes, `skillshare push -m "Update skills"` to commit and push, and `skillshare pull` to retrieve changes from the fork.

## Install

### [skillshare](https://github.com/runkids/skillshare)

One source of truth. Sync everywhere with one command.

```bash
# Install skillshare
curl -fsSL https://raw.githubusercontent.com/runkids/skillshare/main/install.sh | sh

# Install all skills from this repo
skillshare install Uwith/my-skills
skillshare sync

# Or pick a specific skill
skillshare install Uwith/my-skills -s frontend-design
skillshare sync
```

## How It Works

### Folder Organization

Skills are organized into category folders for easy browsing. On `skillshare sync`, nested paths **auto-flatten** into each target — no manual mapping needed.

```text
~/.config/skillshare/skills/
├── frontend/
│   ├── frontend-design/
│   ├── ui-skills/
│   ├── react/
│   │   ├── react-best-practices/
│   │   └── react-doctor/
│   └── vue/
│       ├── vue-best-practices/
│       ├── vue-debug-guides/
│       └── ...
├── devops/
│   └── docker-expert/
├── web-dev/
│   ├── accessibility/
│   ├── core-web-vitals/
│   ├── performance/
│   └── ...
└── utils/
    ├── ascii-box-check/
    ├── remotion/
    └── skill-creator/

         ↓ skillshare sync

├→ Claude Code   (~/.claude/skills/)
├→ Cursor        (~/.cursor/skills/)
├→ Codex         (~/.codex/skills/)
├→ OpenCode      (~/.config/opencode/skills/)
└→ 45+ more targets...
```

### .skillignore

Like `.gitignore`, but for skills. Exclude folders from sync without removing them from the repo.

```text
# .skillignore
skillshare       # meta tools — not a skill
feature-radar    # WIP, not ready to share
```

### Sync Modes

skillshare supports per-target sync modes:

| Mode | Behavior |
| ------ | ---------- |
| **symlink** | Link to source (default on macOS/Linux) |
| **copy** | Real files in target |
| **merge** | Preserve target's local skills, add shared ones |

### Security Audit

Every `skillshare install` runs a built-in audit to scan for prompt injection, data exfiltration, and credential theft.

```bash
# Manual audit anytime
skillshare audit
```

## Why skillshare?

> One source of truth for AI CLI skills. Sync everywhere with one command.

- **49+ AI tools** — Claude Code, Cursor, Codex, Copilot, Gemini, and more
- **Single binary** — written in Go, no runtime dependencies
- **Cross-machine sync** — Git-native `push` / `pull`
- **Privacy-first** — no telemetry, no central registry
- **Web dashboard** — `skillshare ui` for visual management

Learn more: [github.com/runkids/skillshare](https://github.com/runkids/skillshare)

## License

MIT
