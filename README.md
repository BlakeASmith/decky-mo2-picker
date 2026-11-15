# MO2 Universal Launcher (Decky) — internal

Private **Origin** development tree. End users install from the **public** repo only:

**https://github.com/BlakeASmith/decky-mo2-picker**

## Maintainers

- Mirror, publish, ingesting public PRs: [docs/agents/PUBLIC_REPOSITORY.md](docs/agents/PUBLIC_REPOSITORY.md)
- Cursor agents: [.cursor/rules/maintainers.mdc](.cursor/rules/maintainers.mdc)
- Generic agent/contributor guide (public too): [AGENTS.md](AGENTS.md)
- Implementation spec (private): [SPEC.md](SPEC.md)

### Publish to GitHub (when ready)

Origin: **Actions → Prepare public release branch → Run workflow**.

One-time: add repo secret **`PUBLIC_MIRROR_TOKEN`** (fine-grained PAT, Contents write on `BlakeASmith/decky-mo2-picker`). Details: [docs/agents/PUBLIC_REPOSITORY.md](docs/agents/PUBLIC_REPOSITORY.md).

Public **Build and Release** uses the repo’s built-in `GITHUB_TOKEN` for zips—no `gh` CLI on your machine.

## Develop locally

```bash
pnpm install && pnpm run build && pnpm test
pnpm run package:zip
```

## License

GPL-3.0-or-later — [LICENSE](LICENSE). See [LLM-DISCLAIMER.md](LLM-DISCLAIMER.md) (internal tree only).