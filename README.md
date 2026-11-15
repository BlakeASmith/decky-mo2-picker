# MO2 Universal Launcher (Decky)

Decky Loader plugin for SteamOS: discover Mod Organizer 2 instances (Steam, Heroic, Lutris, portable), open MO2, or launch modded games via MO2’s `moshortcut://` protocol inside the matching Wine/Proton prefix.

## Install

1. In **Decky Loader → Settings**, use **Install plugin from URL** and paste the **Latest** URL below (same link for every update), **or** download from **[Releases](https://github.com/BlakeASmith/decky-mo2-picker/releases)**.
2. For pinned versions, use a **`v*`** tag release and its versioned zip.

**Latest (rolling updates — fixed URL):**

```text
https://github.com/BlakeASmith/decky-mo2-picker/releases/download/latest/mo2-universal-launcher-latest.zip
```

Re-running install from that URL after each publish pulls the newest build. The zip still contains `plugin.json` `version` for tools that compare versions.

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
