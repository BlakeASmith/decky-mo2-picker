# MO2 Universal Launcher (Decky) — internal

Private **Origin** development tree. End users install from the **public** repo only:

**https://github.com/BlakeASmith/decky-mo2-picker**

## Maintainers

- Mirror, publish, ingesting public PRs: [docs/agents/PUBLIC_REPOSITORY.md](docs/agents/PUBLIC_REPOSITORY.md)
- Cursor agents: [.cursor/rules/maintainers.mdc](.cursor/rules/maintainers.mdc)
- Generic agent/contributor guide (public too): [AGENTS.md](AGENTS.md)
- Implementation spec (private): [SPEC.md](SPEC.md)

### Publish to GitHub (when ready)

```bash
PUSH=1 ./scripts/publish-public-branch.sh   # builds release/public from main
git push origin release/public              # triggers sync → GitHub main + release zips
```

Requires `gh auth login` (or SSH) on your machine for the GitHub push step. Public release CI uses the repo’s built-in `GITHUB_TOKEN`.

## Develop locally

```bash
pnpm install && pnpm run build && pnpm test
pnpm run package:zip
```

## License

GPL-3.0-or-later — [LICENSE](LICENSE). See [LLM-DISCLAIMER.md](LLM-DISCLAIMER.md) (internal tree only).