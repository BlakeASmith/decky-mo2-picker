# Agent & contributor guide

Instructions for humans and coding agents working on this Decky plugin. Not tied to a specific AI product—use whatever tools you prefer.

## Project layout

- `main.py` — Decky Python RPC entrypoint
- `py_modules/mo2_launcher/` — discovery, prefixes, launcher
- `src/` — React QAM UI (`@decky/ui`, `@decky/api`)
- `tests/` — pytest (run from repo root)

## Build & verify

```bash
pnpm install
pnpm run build
pnpm test                 # pytest
pnpm run package:zip      # optional local zip
```

Python changes need pytest. Frontend changes need `pnpm run build` with no TypeScript errors.

## Conventions

- Python 3.11+ stdlib in backend (no extra pip deps in the plugin bundle)
- Pytest: module-level test functions, not classes, unless OOP is required
- Match existing naming and patterns in neighboring files
- GPL-3.0-or-later: preserve LICENSE and third-party notices
- Keep user-facing install/docs accurate for **https://github.com/BlakeASmith/decky-mo2-picker**

## Scope

- Minimize diffs; avoid unrelated refactors
- Do not commit secrets, tokens, or machine-specific paths
- Decky plugins with this launcher may run as **root**—be careful with subprocess and privileges in `launcher.py`

## Contributions

Open pull requests against the **public** GitHub repository. Maintainers reconcile changes into the private development fork when needed.

For end-user install steps, see [README.md](README.md) on the public default branch.