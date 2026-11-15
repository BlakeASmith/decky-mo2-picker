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