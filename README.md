# MO2 Universal Launcher (Decky)

Decky Loader plugin for SteamOS that discovers Mod Organizer 2 instances across Steam, Heroic, Lutris, and portable installs, then launches MO2 or modded games via `moshortcut://` inside the matching Wine/Proton prefix.

## Install from release

1. Open [Releases](https://github.com/blake-smith/decky-mo2-picker/releases) on this repo.
2. Download the latest `.zip`:
   - **Tagged** `v*` builds = stable releases.
   - **`continuous`** prerelease = latest `main` build (auto-published on every push).
3. In Decky Loader → Settings → **Install plugin from URL** or copy the zip to the Deck and install from file.

Direct install URL pattern (replace tag/filename as needed):

```text
https://github.com/blake-smith/decky-mo2-picker/releases/download/v0.1.0/mo2-universal-launcher-v0.1.0.zip
```

## Develop locally

```bash
pnpm install
pnpm run build
pnpm test
pnpm run package:zip   # writes out/*.zip (no Docker required)
```

CI runs on every push to `main` (artifact + `continuous` prerelease) and on version tags `v*` (GitHub Release with zip).

See `SPEC.md` for the full technical specification.