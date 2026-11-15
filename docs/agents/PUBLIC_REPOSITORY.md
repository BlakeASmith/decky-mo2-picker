# Public GitHub mirror (maintainers — internal only)

Excluded from `release/public`. Cursor-specific automation notes live under **`.cursor/`** (also excluded).

## Repositories

| Forge | Branch | Audience |
|-------|--------|----------|
| **Origin (private)** | `main` | Primary development |
| **Origin** | `release/public` | Sanitized snapshot; triggers GitHub sync |
| **GitHub (public)** | `main` | Contributors, users, releases |

Public tree includes generic **[AGENTS.md](../AGENTS.md)** at repo root (copied on publish from `main`).

## What the public repo sees

- Plugin source, tests, `LICENSE`, `THIRD_PARTY_NOTICES.md`, **`AGENTS.md`**
- User README from **`public/README.md`**
- **`build-release.yml`** only (not internal CI or publish/sync workflows)

## Stays private on `main`

- This directory (`docs/agents/`), **`SPEC.md`**, **`LLM-DISCLAIMER.md`**
- **`.cursor/`**, publish scripts, sync workflows
- Internal **[README.md](../README.md)** maintainer section

## Publish private → public

**Public visibility** lets anyone **download** releases without signing in. **Pushing** still uses your normal GitHub auth (`gh auth login`, SSH, or git credential helper)—there is no separate “public repo push token.”

```bash
PUSH=1 ./scripts/publish-public-branch.sh
```

With `PUSH=1`, the script pushes **`release/public`** to Origin and **`release/public` → GitHub `main`** using your ambient GitHub credentials (`gh auth setup-git`).

On **public GitHub**, the **Build and Release** workflow uses the repo’s built-in **`GITHUB_TOKEN`** to attach zips—no extra secret.

Never push Origin `main` directly to GitHub.

## When contributors land work on **public `main`**

Pull into private `main` before more internal work or the next publish:

```bash
git remote add public https://github.com/BlakeASmith/decky-mo2-picker.git  # once
git fetch public main
git checkout main
git merge public/main -m "chore: sync contributions from public main"
# resolve conflicts; prefer contributor intent for user-facing files, re-apply public/README.md mapping if README conflict
pnpm run build && pnpm test
```

Then continue on Origin `main` and publish when ready with `publish-public-branch.sh`.

**Reminder for Cursor / cloud agents:** after notifying the user of merged public PRs, or when the user mentions GitHub contributions, **fetch and merge `public/main`** into Origin `main` unless they explicitly want otherwise.

## Doc split

| Topic | Location |
|-------|----------|
| Generic agent/contributor rules | `AGENTS.md` (public) |
| Mirror, publish, ingest public | This file |
| Implementation spec | `SPEC.md` |
| Cursor Cloud Agent branch/PR rules | `.cursor/rules/maintainers.mdc` |