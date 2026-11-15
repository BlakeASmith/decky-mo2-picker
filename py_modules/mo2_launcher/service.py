"""Orchestrate scanning, overrides, and launch."""

from __future__ import annotations

from typing import Any

from .launcher import launch_instance
from .mo2_scanner import MO2Instance, scan_instances
from .prefix_indexer import PrefixIndexer, list_all_prefixes, list_installed_protons
from .settings_store import load_settings, set_instance_override


class MO2Service:
    def __init__(self, logger: Any | None = None):
        self.logger = logger
        self.indexer = PrefixIndexer()
        self._cache: list[dict[str, Any]] | None = None

    def get_instances(self, force_rescan: bool = False) -> list[dict[str, Any]]:
        if self._cache is not None and not force_rescan:
            return self._cache
        settings = load_settings()
        self.indexer.build()
        instances = scan_instances(
            self.indexer, custom_paths=settings.get("custom_search_paths", [])
        )
        result = [
            self._apply_overrides(inst.to_dict(), settings) for inst in instances
        ]
        self._cache = result
        return result

    def _apply_overrides(
        self, inst: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        override = settings.get("instance_overrides", {}).get(inst["id"], {})
        if not override:
            return inst
        merged = dict(inst)
        for key, val in override.items():
            if key == "envOverrides" and isinstance(val, dict):
                env = dict(merged.get("envOverrides") or {})
                env.update(val)
                merged["envOverrides"] = env
            elif val not in (None, ""):
                merged[key] = val
        return merged

    def save_instance_override(self, instance_id: str, data: dict[str, Any]) -> None:
        set_instance_override(instance_id, data)
        self._cache = None

    def launch_mo2(self, instance_id: str) -> dict[str, Any]:
        inst = self._find(instance_id)
        if not inst:
            return {"success": False, "error": "Instance not found"}
        if not inst.get("isValid"):
            return {"success": False, "error": inst.get("validationError", "Invalid")}
        try:
            launch_instance(inst, logger=self.logger)
            return {"success": True}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def launch_game(self, instance_id: str, executable_title: str | None = None) -> dict[str, Any]:
        inst = self._find(instance_id)
        if not inst:
            return {"success": False, "error": "Instance not found"}
        title = executable_title or inst.get("defaultExecutable")
        if not title:
            return {"success": False, "error": "No executable configured"}
        try:
            launch_instance(inst, executable_title=title, logger=self.logger)
            return {"success": True}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def get_available_protons(self) -> list[dict[str, str]]:
        return list_installed_protons()

    def get_available_prefixes(self) -> list[dict[str, str]]:
        self.indexer.build()
        return list_all_prefixes(self.indexer)

    def _find(self, instance_id: str) -> dict[str, Any] | None:
        for inst in self.get_instances():
            if inst["id"] == instance_id:
                return inst
        return None