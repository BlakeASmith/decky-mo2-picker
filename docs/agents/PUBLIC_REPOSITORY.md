# Public GitHub repository (agents — internal only)

This file lives on **private Origin `main` only**. It is **excluded** from the public mirror. Do not copy it to `release/public` or GitHub.

## Repositories

| Forge | Remote | Branch | Audience |
|-------|--------|--------|----------|
| **Origin (private)** | `origin` → `https://origin.cursor.com/…/decky-mo2-picker.git` | `main` | You, agents, internal work |
| **Public mirror branch** | same Origin remote | `release/public` | Sanitized tree; triggers sync |
| **GitHub (public)** | `public` → `https://github.com/BlakeASmith/decky-mo2-picker.git` | `main` | End users, releases, issues |

Never push internal-only docs, agent prompts, or `SPEC.md` to `release/public` or GitHub `main`.

## What belongs on the public repo

- Shipped plugin code (`main.py`, `py_modules/`, `src/`, `dist/` is build output only in CI)
- User-facing `README` (from `public/README.md`)
- `LICENSE`, `THIRD_PARTY_NOTICES.md`
- Tests, CI **build/release** workflow only
- `plugin.json`, `package.json`, assets needed to build

## What stays private (`main` only)

- This file and everything under `docs/agents/`
- `SPEC.md`, `LLM-DISCLAIMER.md`
- Publish/sync workflow definitions and `scripts/publish-public-branch.sh`
- Internal notes in the root `README.md` (Agent section)

## Publishing (when a release is ready)

1. Merge or commit work on **`main`** (Origin).
2. Run:

   ```bash
   ./scripts/publish-public-branch.sh
   git push origin release/public
   ```

3. CI on **`release/public`** force-syncs that commit to **GitHub `main`** (secret `PUBLIC_GITHUB_PUSH_TOKEN`).
4. GitHub **Build and Release** workflow produces the installable zip and GitHub Releases.

Do **not** push `main` directly to the public GitHub remote.

## One-time GitHub setup (human)

1. Create a fine-grained PAT or classic token with **contents: write** on `BlakeASmith/decky-mo2-picker` only.
2. In **Origin** repo settings → Actions secrets: `PUBLIC_GITHUB_PUSH_TOKEN`.
3. Confirm GitHub repo visibility is **Public**.

## Agent rules

- Default all implementation work to **Origin `main`**.
- Before marking a user-visible release done, run **`publish-public-branch.sh`** and push **`release/public`** (or ask the user to approve publish).
- Use **`public/README.md`** for user-facing doc changes intended for GitHub; keep internal process in `docs/agents/` or root README “Maintainers” section.
- Update release URLs to `https://github.com/BlakeASmith/decky-mo2-picker/...` only in public-facing files.
- Do not add Cursor/Cloud Agent setup, Origin auth, or private infra to `public/` or files included in the manifest.