"""Index Steam, Heroic, and Lutris game prefixes."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .path_utils import drive_c_path
from .vdf_utils import parse_vdf

HEROIC_CONFIG_ROOTS = [
    os.path.expanduser("~/.config/heroic"),
    os.path.expanduser("~/.var/app/com.heroicgameslauncher.hgl/config/heroic"),
]

SCRIPT_EXTENDER_TITLES = frozenset(
    {"F4SE", "SKSE", "NVSE", "OBSE", "SFSE", "SKSE64", "f4se", "skse"}
)


@dataclass
class PrefixEntry:
    install_path: str
    title: str
    launcher_source: str
    prefix_path: str
    proton_binary_path: str = ""
    env_overrides: dict[str, str] = field(default_factory=dict)
    appid: str = ""


class PrefixIndexer:
    def __init__(self, steam_home: str | None = None):
        self.steam_home = steam_home or os.path.expanduser(
            "~/.local/share/Steam"
        )
        self.entries: list[PrefixEntry] = []
        self.by_install_path: dict[str, PrefixEntry] = {}

    def build(self) -> None:
        self.entries.clear()
        self.by_install_path.clear()
        self._index_steam()
        self._index_heroic()
        self._index_lutris()
        for entry in self.entries:
            self.by_install_path[entry.install_path.rstrip("/")] = entry

    def match_install_path(self, game_path_linux: str) -> PrefixEntry | None:
        if not game_path_linux:
            return None
        norm = os.path.normpath(game_path_linux)
        if norm in self.by_install_path:
            return self.by_install_path[norm]
        best: PrefixEntry | None = None
        best_len = -1
        for path, entry in self.by_install_path.items():
            if norm == path or norm.startswith(path + os.sep):
                if len(path) > best_len:
                    best_len = len(path)
                    best = entry
            elif path.startswith(norm + os.sep):
                if len(norm) > best_len:
                    best_len = len(norm)
                    best = entry
        return best

    def _index_steam(self) -> None:
        lib_folders = self._steam_libraries()
        proton_map = self._steam_compat_tools()
        default_proton = self._fallback_proton()

        for lib in lib_folders:
            steamapps = os.path.join(lib, "steamapps")
            if not os.path.isdir(steamapps):
                continue
            for name in os.listdir(steamapps):
                if not name.startswith("appmanifest_") or not name.endswith(".acf"):
                    continue
                manifest = os.path.join(steamapps, name)
                meta = self._parse_acf(manifest)
                if not meta:
                    continue
                appid = meta.get("appid", "")
                installdir = meta.get("installdir", "")
                if not installdir:
                    continue
                install_path = os.path.join(steamapps, "common", installdir)
                compat = os.path.join(lib, "steamapps", "compatdata", appid)
                if not os.path.isdir(compat):
                    compat = os.path.join(
                        self.steam_home, "steamapps", "compatdata", appid
                    )
                proton = proton_map.get(appid) or default_proton
                entry = PrefixEntry(
                    install_path=install_path,
                    title=meta.get("name", installdir),
                    launcher_source="steam",
                    prefix_path=compat if os.path.isdir(compat) else "",
                    proton_binary_path=proton or "",
                    appid=appid,
                )
                if entry.prefix_path:
                    self.entries.append(entry)

    def _steam_libraries(self) -> list[str]:
        libs = [self.steam_home]
        vdf_path = os.path.join(self.steam_home, "steamapps", "libraryfolders.vdf")
        if not os.path.isfile(vdf_path):
            return libs
        try:
            with open(vdf_path, encoding="utf-8", errors="ignore") as f:
                data = parse_vdf(f.read())
        except OSError:
            return libs
        folders = data.get("libraryfolders", data.get("LibraryFolders", {}))
        if isinstance(folders, dict):
            for key, val in folders.items():
                if key.isdigit() and isinstance(val, dict):
                    path = val.get("path")
                    if path and os.path.isdir(path):
                        libs.append(path)
                elif isinstance(val, str) and os.path.isdir(val):
                    libs.append(val)
        return list(dict.fromkeys(libs))

    def _steam_compat_tools(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        cfg = os.path.join(self.steam_home, "config", "config.vdf")
        if not os.path.isfile(cfg):
            return mapping
        try:
            with open(cfg, encoding="utf-8", errors="ignore") as f:
                data = parse_vdf(f.read())
        except OSError:
            return mapping
        compat = (
            data.get("InstallConfig", {})
            .get("Software", {})
            .get("Valve", {})
            .get("Steam", {})
            .get("CompatToolMapping", {})
        )
        if not isinstance(compat, dict):
            compat = data.get("CompatToolMapping", {})
        for appid, tool_info in compat.items():
            if not isinstance(tool_info, dict):
                continue
            name = tool_info.get("name", "")
            proton = self._resolve_proton_name(name)
            if proton:
                mapping[str(appid)] = proton
        return mapping

    def _resolve_proton_name(self, name: str) -> str:
        if not name:
            return ""
        candidates = [
            os.path.join(self.steam_home, "compatibilitytools.d", name, "proton"),
            os.path.join(self.steam_home, "compatibilitytools.d", name, "proton"),
        ]
        folder_map = {
            "proton_experimental": "Proton - Experimental",
            "proton_9": "Proton 9.0",
        }
        mapped = folder_map.get(name, name)
        candidates.append(
            os.path.join(
                self.steam_home, "steamapps", "common", mapped, "proton"
            )
        )
        for c in candidates:
            if os.path.isfile(c):
                return c
        tools = os.path.join(self.steam_home, "compatibilitytools.d", name)
        if os.path.isdir(tools):
            for root, _, files in os.walk(tools):
                if "proton" in files:
                    return os.path.join(root, "proton")
        return ""

    def _fallback_proton(self) -> str:
        common = os.path.join(self.steam_home, "steamapps", "common")
        if os.path.isdir(common):
            for name in sorted(os.listdir(common), reverse=True):
                if name.startswith("Proton"):
                    proton = os.path.join(common, name, "proton")
                    if os.path.isfile(proton):
                        return proton
        compat = os.path.join(self.steam_home, "compatibilitytools.d")
        if os.path.isdir(compat):
            for name in sorted(os.listdir(compat), reverse=True):
                proton = os.path.join(compat, name, "proton")
                if os.path.isfile(proton):
                    return proton
        return ""

    @staticmethod
    def _parse_acf(path: str) -> dict[str, str]:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                data = parse_vdf(f.read())
        except OSError:
            return {}
        appstate = data.get("AppState", data)
        if not isinstance(appstate, dict):
            return {}
        return {
            "appid": str(appstate.get("appid", "")),
            "name": str(appstate.get("name", "")),
            "installdir": str(appstate.get("installdir", "")),
        }

    def _index_heroic(self) -> None:
        for root in HEROIC_CONFIG_ROOTS:
            if not os.path.isdir(root):
                continue
            libs = self._heroic_libraries(root)
            games_cfg = os.path.join(root, "GamesConfig")
            for install_path, meta in libs.items():
                app_name = meta.get("appName") or meta.get("folder_name", "")
                cfg = self._heroic_game_config(games_cfg, app_name)
                prefix = cfg.get("winePrefix", "")
                if not prefix or not os.path.isdir(prefix):
                    continue
                proton = self._heroic_proton_path(root, cfg)
                env = self._heroic_env(cfg)
                self.entries.append(
                    PrefixEntry(
                        install_path=install_path,
                        title=meta.get("title", app_name or install_path),
                        launcher_source="heroic",
                        prefix_path=prefix,
                        proton_binary_path=proton,
                        env_overrides=env,
                    )
                )

    def _heroic_libraries(self, root: str) -> dict[str, dict[str, str]]:
        out: dict[str, dict[str, str]] = {}
        for rel in (
            "sideload_apps/library.json",
            "gog_store/library.json",
            "store_cache/legendary_library.json",
        ):
            path = os.path.join(root, rel)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            items = data if isinstance(data, list) else data.values()
            if isinstance(data, dict) and "games" in data:
                items = data["games"].values() if isinstance(data["games"], dict) else data["games"]
            for item in items:
                if not isinstance(item, dict):
                    continue
                install = item.get("install_path") or item.get("installPath") or ""
                if install:
                    out[install.rstrip("/")] = {
                        "title": item.get("title") or item.get("app_title") or "",
                        "appName": item.get("app_name") or item.get("appName") or "",
                        "folder_name": item.get("folder_name", ""),
                    }
        return out

    def _heroic_game_config(self, games_cfg: str, app_name: str) -> dict[str, Any]:
        for name in (f"{app_name}.json", "default.json"):
            path = os.path.join(games_cfg, name)
            if os.path.isfile(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        return json.load(f)
                except (OSError, json.JSONDecodeError):
                    pass
        return {}

    def _heroic_proton_path(self, root: str, cfg: dict[str, Any]) -> str:
        wine = cfg.get("wineVersion", {})
        if isinstance(wine, dict):
            bin_path = wine.get("bin", "")
            if bin_path and os.path.isfile(bin_path):
                return bin_path
            name = wine.get("name", "")
            if name:
                for base in (
                    os.path.join(root, "tools", "proton"),
                    os.path.expanduser("~/.local/share/Steam/compatibilitytools.d"),
                ):
                    candidate = os.path.join(base, name, "proton")
                    if os.path.isfile(candidate):
                        return candidate
        return self._fallback_proton()

    def _heroic_env(self, cfg: dict[str, Any]) -> dict[str, str]:
        env: dict[str, str] = {}
        if cfg.get("enableEsync") is False:
            env["PROTON_NO_ESYNC"] = "1"
        if cfg.get("enableFsync") is False:
            env["PROTON_NO_FSYNC"] = "1"
        for opt in cfg.get("enviromentOptions", cfg.get("environmentOptions", [])):
            if isinstance(opt, dict):
                key = opt.get("key")
                val = opt.get("value")
                if key and val is not None:
                    env[str(key)] = str(val)
        return env

    def _index_lutris(self) -> None:
        games_dir = os.path.expanduser("~/.config/lutris/games")
        if not os.path.isdir(games_dir):
            return
        for name in os.listdir(games_dir):
            if not name.endswith((".yml", ".yaml")):
                continue
            path = os.path.join(games_dir, name)
            parsed = self._parse_lutris_yml(path)
            if not parsed:
                continue
            self.entries.append(
                PrefixEntry(
                    install_path=parsed["install_path"],
                    title=parsed["title"],
                    launcher_source="lutris",
                    prefix_path=parsed["prefix"],
                    proton_binary_path=parsed.get("proton", "") or self._fallback_proton(),
                )
            )

    @staticmethod
    def _parse_lutris_yml(path: str) -> dict[str, str]:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            return {}
        title_m = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        game_m = re.search(r"^game:\s*(.+)$", text, re.MULTILINE)
        prefix_m = re.search(r"^prefix:\s*(.+)$", text, re.MULTILINE)
        if not prefix_m:
            return {}
        prefix = os.path.expanduser(prefix_m.group(1).strip().strip('"\''))
        install = ""
        if game_m:
            game_exe = game_m.group(1).strip()
            if ":" in game_exe:
                install = os.path.dirname(game_exe.split(":")[-1])
        return {
            "title": (title_m.group(1).strip() if title_m else Path(path).stem),
            "prefix": prefix,
            "install_path": install or prefix,
        }


def list_all_prefixes(indexer: PrefixIndexer) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for entry in indexer.entries:
        if not entry.prefix_path or entry.prefix_path in seen:
            continue
        seen.add(entry.prefix_path)
        label = f"{entry.launcher_source.title()}: {entry.title}"
        if entry.appid:
            label += f" ({entry.appid})"
        result.append(
            {
                "id": entry.prefix_path,
                "label": label,
                "launcherSource": entry.launcher_source,
                "installPath": entry.install_path,
            }
        )
    return result


def list_installed_protons(steam_home: str | None = None) -> list[dict[str, str]]:
    steam_home = steam_home or os.path.expanduser("~/.local/share/Steam")
    found: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(path: str, label: str) -> None:
        if path in seen or not os.path.isfile(path):
            return
        seen.add(path)
        found.append({"id": path, "label": label})

    compat = os.path.join(steam_home, "compatibilitytools.d")
    if os.path.isdir(compat):
        for name in sorted(os.listdir(compat)):
            proton = os.path.join(compat, name, "proton")
            add(proton, name)

    common = os.path.join(steam_home, "steamapps", "common")
    if os.path.isdir(common):
        for name in sorted(os.listdir(common)):
            if "Proton" in name or "GE-Proton" in name:
                add(os.path.join(common, name, "proton"), name)

    for heroic_root in HEROIC_CONFIG_ROOTS:
        tools = os.path.join(heroic_root, "tools", "proton")
        if os.path.isdir(tools):
            for name in sorted(os.listdir(tools)):
                add(os.path.join(tools, name, "proton"), f"Heroic: {name}")

    return found