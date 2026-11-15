"""Persist user overrides and custom search paths."""

from __future__ import annotations

import json
import os
from typing import Any

try:
    import decky
except ImportError:  # unit tests / dev
    decky = None  # type: ignore

DEFAULT_SETTINGS: dict[str, Any] = {
    "custom_search_paths": [],
    "instance_overrides": {},
}


def settings_path() -> str:
    if decky is not None:
        base = decky.DECKY_PLUGIN_SETTINGS_DIR
    else:
        base = os.path.join(os.path.expanduser("~"), ".config", "decky-mo2-launcher")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "settings.json")


def load_settings() -> dict[str, Any]:
    path = settings_path()
    if not os.path.isfile(path):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def save_settings(data: dict[str, Any]) -> None:
    path = settings_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_instance_override(instance_id: str) -> dict[str, Any]:
    return dict(load_settings().get("instance_overrides", {}).get(instance_id, {}))


def set_instance_override(instance_id: str, override: dict[str, Any]) -> None:
    settings = load_settings()
    overrides = settings.setdefault("instance_overrides", {})
    if override:
        current = dict(overrides.get(instance_id, {}))
        current.update(override)
        overrides[instance_id] = current
    elif instance_id in overrides:
        del overrides[instance_id]
    save_settings(settings)