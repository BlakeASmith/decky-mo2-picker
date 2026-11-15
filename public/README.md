# MO2 Universal Launcher (Decky)

Decky Loader plugin for SteamOS: discover Mod Organizer 2 instances (Steam, Heroic, Lutris, portable), open MO2, or launch modded games via MO2’s `moshortcut://` protocol inside the matching Wine/Proton prefix.

## Install

1. Open **[Releases](https://github.com/BlakeASmith/decky-mo2-picker/releases)**.
2. Download the latest **`mo2-universal-launcher-v*.zip`** (stable tags) or the **`continuous`** prerelease for bleeding-edge builds.
3. In **Decky Loader → Settings**, use **Install plugin from URL** (paste the release asset URL) or install from the zip on your Deck.

Example URL (replace version as needed):

```text
https://github.com/BlakeASmith/decky-mo2-picker/releases/download/v0.1.0/mo2-universal-launcher-v0.1.0.zip
```

Release assets on this **public** repository are anonymous downloads—no GitHub sign-in required in the browser or on Deck.

## Features

- Scans portable MO2 folders and global MO2 instances under Wine prefixes
- Matches game installs to Steam compatdata, Heroic, and Lutris prefixes
- Launch MO2 GUI or a configured executable (F4SE, SKSE, etc.) from Gaming Mode
- Per-instance overrides for prefix, Proton build, and `WINEDLLOVERRIDES`

## Build from source

```bash
pnpm install
pnpm run build
pnpm test
pnpm run package:zip   # outputs out/*.zip
```

## License

GPL-3.0-or-later — see [LICENSE](LICENSE). Template scaffolding is credited in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contributing

Pull requests welcome. Agents and automated tooling should read [AGENTS.md](AGENTS.md).

## Support

Open an issue on this repository for bugs and feature requests related to the released plugin.