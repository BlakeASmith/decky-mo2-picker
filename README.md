# MO2 Universal Launcher (Decky) — internal

Private **Origin** development tree. End users install from the **public** repo only:

**https://github.com/BlakeASmith/decky-mo2-picker**

## Maintainers & agents

- Process and rules: [docs/agents/PUBLIC_REPOSITORY.md](docs/agents/PUBLIC_REPOSITORY.md)
- Implementation spec (not public): [SPEC.md](SPEC.md)

### Publish to GitHub (when ready)

```bash
PUSH=1 ./scripts/publish-public-branch.sh   # builds release/public from main
git push origin release/public              # triggers sync → GitHub main + release zips
```

Or run the **Prepare public release branch** workflow on Origin (after setting `PUBLIC_GITHUB_PUSH_TOKEN`).

## Develop locally

```bash
pnpm install && pnpm run build && pnpm test
pnpm run package:zip
```

## License

GPL-3.0-or-later — [LICENSE](LICENSE). See [LLM-DISCLAIMER.md](LLM-DISCLAIMER.md) (internal tree only).