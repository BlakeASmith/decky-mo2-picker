"""Windows-to-Linux path translation and storage root discovery."""

from __future__ import annotations

import os
import re
from pathlib import Path

BYTEARRAY_PATTERN = re.compile(r"^@ByteArray\((.*)\)$", re.DOTALL)


def strip_bytearray(value: str) -> str:
    value = value.strip()
    match = BYTEARRAY_PATTERN.match(value)
    if match:
        return match.group(1)
    return value


def win_to_linux_path(win_path: str, prefix_path: str) -> str:
    """Resolve MO2 / Wine Windows paths to Linux paths."""
    if not win_path:
        return ""

    raw = strip_bytearray(win_path.strip().strip('"'))
    raw = raw.replace("\\\\", "\\").replace("\\", "/")

    lower = raw.lower()
    if lower.startswith("z:/"):
        linux = "/" + raw[3:].lstrip("/")
        return os.path.normpath(linux)
    if lower.startswith("c:/"):
        rel = raw[3:].lstrip("/")
        pfx = Path(prefix_path)
        if (pfx / "pfx" / "drive_c").is_dir():
            return os.path.normpath(str(pfx / "pfx" / "drive_c" / rel))
        if (pfx / "drive_c").is_dir():
            return os.path.normpath(str(pfx / "drive_c" / rel))
        return os.path.normpath(str(pfx / "drive_c" / rel))

    if raw.startswith("/"):
        return os.path.normpath(raw)

    return os.path.normpath(raw)


def get_storage_roots() -> list[str]:
    """Return home plus mounted external drives under /run/media."""
    roots = [os.path.expanduser("~")]
    media = Path("/run/media")
    if media.is_dir():
        for mount in media.iterdir():
            if mount.is_dir():
                roots.append(str(mount))
                for child in mount.iterdir():
                    if child.is_dir():
                        roots.append(str(child))
    return list(dict.fromkeys(roots))


def prefix_has_pfx(prefix_path: str) -> bool:
    return os.path.isdir(os.path.join(prefix_path, "pfx"))


def drive_c_path(prefix_path: str) -> str:
    if prefix_has_pfx(prefix_path):
        return os.path.join(prefix_path, "pfx", "drive_c")
    return os.path.join(prefix_path, "drive_c")


STEAM_INSTALL_ROOTS = (
    "~/.local/share/Steam",
    "~/.var/app/com.valvesoftware.Steam/data/Steam",
    "~/.steam/steam",
    "~/.steam/root",
)


def existing_steam_install_roots() -> list[str]:
    """Steam library roots (native, Flatpak, legacy symlinks)."""
    found: list[str] = []
    for candidate in STEAM_INSTALL_ROOTS:
        path = os.path.abspath(os.path.expanduser(candidate))
        if os.path.isdir(path) and path not in found:
            found.append(path)
    return found


HEROIC_CONFIG_ROOTS = (
    "~/.config/heroic",
    "~/.var/app/com.heroicgameslauncher.hgl/config/heroic",
)

HEROIC_PREFIX_ROOTS = (
    "~/Games/Heroic/Prefixes",
    "~/Games/Heroic/prefixes",
    "~/.config/heroic/Prefixes",
    "~/.var/app/com.heroicgameslauncher.hgl/config/heroic/Prefixes",
    "~/.var/app/com.heroicgameslauncher.hgl/Games/Heroic/Prefixes",
)


def existing_heroic_config_roots() -> list[str]:
    roots: list[str] = []
    for candidate in HEROIC_CONFIG_ROOTS:
        path = os.path.abspath(os.path.expanduser(candidate))
        if os.path.isdir(path) and path not in roots:
            roots.append(path)
    return roots


def iter_wine_user_profiles(drive_c: str):
    """Yield profile dirs under drive_c/users and drive_c/Users."""
    if not drive_c or not os.path.isdir(drive_c):
        return
    for folder in ("users", "Users"):
        base = os.path.join(drive_c, folder)
        if not os.path.isdir(base):
            continue
        try:
            for name in os.listdir(base):
                profile = os.path.join(base, name)
                if os.path.isdir(profile) and name not in (".", "..", "Public", "Default"):
                    yield profile
        except OSError:
            continue
