import os
import sys

import asyncio

import decky

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "py_modules"))

from mo2_launcher.service import MO2Service  # noqa: E402


class Plugin:
    def __init__(self) -> None:
        self.service = MO2Service(logger=decky.logger)

    async def get_instances(self, force_rescan: bool = False):
        return await asyncio.to_thread(self.service.get_instances, force_rescan)

    async def launch_mo2(self, instance_id: str):
        return await asyncio.to_thread(self.service.launch_mo2, instance_id)

    async def launch_game(self, instance_id: str, executable_title: str | None = None):
        return await asyncio.to_thread(
            self.service.launch_game, instance_id, executable_title
        )

    async def save_instance_override(self, instance_id: str, override_data: dict):
        return await asyncio.to_thread(
            self.service.save_instance_override, instance_id, override_data
        )

    async def get_available_protons(self):
        return await asyncio.to_thread(self.service.get_available_protons)

    async def get_available_prefixes(self):
        return await asyncio.to_thread(self.service.get_available_prefixes)

    async def _main(self):
        decky.logger.info("MO2 Universal Launcher loaded")

    async def _unload(self):
        decky.logger.info("MO2 Universal Launcher unloading")

    async def _uninstall(self):
        decky.logger.info("MO2 Universal Launcher uninstalling")

    async def _migration(self):
        decky.migrate_settings(
            os.path.join(decky.DECKY_HOME, "settings", "decky-mo2-launcher.json"),
            os.path.join(decky.DECKY_USER_HOME, ".config", "decky-mo2-launcher"),
        )