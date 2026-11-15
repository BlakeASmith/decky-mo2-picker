# Public GitHub mirror (maintainers — internal only)

Excluded from `release/public`. Cursor-specific automation notes live under **`.cursor/`** (also excluded).

## Repositories

| Forge | Branch | Audience |
|-------|--------|----------|
| **Origin (private)** | `main` | Primary development |
| **Origin** | `release/public` | Sanitized snapshot |
| **GitHub (public)** | `main` | Contributors, users, releases |

Public tree includes generic **[AGENTS.md](../AGENTS.md)** at repo root (copied on publish from `main`).

## What the public repo sees

- Plugin source, tests, `LICENSE`, `THIRD_PARTY_NOTICES.md`, **`AGENTS.md`**
- User README from **`public/README.md`**
- **`build-release.yml`** only (not internal CI or publish workflows)

## Stays private on `main`

- This directory (`docs/agents/`), **`SPEC.md`**, **`LLM-DISCLAIMER.md`**
- **`.cursor/`**, publish scripts, sync workflows
- Internal **[README.md](../README.md)** maintainer section

## Publish private → public (no `gh` CLI)

### One-time setup

1. **Fine-grained PAT** (your GitHub account):
   - **Repository access:** `BlakeASmith/decky-mo2-picker` only
   - **Permissions:** Contents **Read and write**, Metadata **Read**
2. **Origin repo secret** (`blake-smith/decky-mo2-picker` on Origin):
   - Name: **`PUBLIC_MIRROR_TOKEN`**
   - Value: the PAT above

### Each release

1. Merge work into **Origin `main`** (as usual).
2. On Origin: **Actions → Prepare public release branch → Run workflow** (defaults are fine).

The workflow:

- Builds **`release/public`** from `main` (strips internal paths, copies `public/README.md` → `README.md`).
- Pushes **`release/public`** to Origin.
- Pushes **`release/public` → GitHub `main`** using `PUBLIC_MIRROR_TOKEN`.

On **public GitHub**, **Build and Release** runs on `main` push and uploads the Decky zip to the **continuous** prerelease—using the repo’s built-in **`GITHUB_TOKEN`** (no extra secret on the public repo).

Never push Origin `main` directly to GitHub.

### Local / agent override

Only if you cannot use the workflow:

```bash
./scripts/publish-public-branch.sh          # build release/public only
PUBLIC_MIRROR_TOKEN='…' PUSH_PUBLIC_ONLY=1 ./scripts/publish-public-branch.sh
```

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

Then continue on Origin `main` and publish via the workflow when ready.

**Reminder for Cursor / cloud agents:** after merged public PRs, **fetch and merge `public/main`** into Origin `main` unless the user says otherwise. **Do not** mirror to GitHub with MCP batch uploads—use the Origin workflow.

## Doc split

| Topic | Location |
|-------|----------|
| Generic agent/contributor rules | `AGENTS.md` (public) |
| Mirror, publish, ingest public | This file |
| Implementation spec | `SPEC.md` |
| Cursor Cloud Agent branch/PR rules | `.cursor/rules/maintainers.mdc` |