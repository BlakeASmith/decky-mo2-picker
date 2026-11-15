"""Discover and parse MO2 instances."""

from __future__ import annotations

import configparser
import hashlib
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .path_utils import drive_c_path, get_storage_roots, win_to_linux_path
from .prefix_indexer import PrefixEntry, PrefixIndexer, SCRIPT_EXTENDER_TITLES

GLOBAL_MO2 = Path("users/steamuser/AppData/Local/ModOrganizer")

MO2_EXE_CANDIDATES = (
    "Modding/MO2/ModOrganizer.exe",
    "Program Files/Mod Organizer 2/ModOrganizer.exe",
    "Program Files (x86)/Mod Organizer 2/ModOrganizer.exe",
)


@dataclass
class MO2Executable:
    title: str
    binary: str
    arguments: str


@dataclass
class MO2Instance:
    id: str
    displayName: str
    instanceType: str
    instanceName: str
    gameName: str
    gamePathLinux: str
    mo2ExeLinux: str
    mo2IniLinux: str
    selectedProfile: str
    executables: list[dict[str, str]] = field(default_factory=list)
    defaultExecutable: str = ""
    launcherSource: str = "custom"
    prefixPath: str = ""
    protonBinaryPath: str = ""
    envOverrides: dict[str, str] = field(default_factory=dict)
    isValid: bool = False
    validationError: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def instance_id(ini_path: str, instance_name: str) -> str:
    digest = hashlib.sha256(f"{ini_path}:{instance_name}".encode()).hexdigest()
    return digest[:16]


def pick_default_executable(executables: list[MO2Executable]) -> str:
    for exe in executables:
        upper = exe.title.upper()
        for token in SCRIPT_EXTENDER_TITLES:
            if token.upper() in upper:
                return exe.title
    return executables[0].title if executables else ""


def parse_modorganizer_ini(
    ini_path: str, prefix_path: str
) -> tuple[dict[str, str], list[MO2Executable]]:
    parser = configparser.ConfigParser(strict=False)
    parser.optionxform = str  # type: ignore[method-assign]
    parser.read(ini_path, encoding="utf-8")
    general = parser["General"] if parser.has_section("General") else {}
    game_name = general.get("gameName", "")
    game_path_raw = general.get("gamePath", "")
    selected = general.get("selected_profile", general.get("selectedProfile", ""))
    game_path_linux = win_to_linux_path(game_path_raw, prefix_path)

    executables: list[MO2Executable] = []
    if parser.has_section("customExecutables"):
        section = parser["customExecutables"]
        try:
            size = int(section.get("size", "0"))
        except ValueError:
            size = 0
        for i in range(1, size + 1):
            title = section.get(f"{i}\\title", "")
            binary = section.get(f"{i}\\binary", "")
            arguments = section.get(f"{i}\\arguments", "")
            if title:
                executables.append(
                    MO2Executable(
                        title=title,
                        binary=win_to_linux_path(binary, prefix_path),
                        arguments=arguments,
                    )
                )

    meta = {
        "gameName": game_name,
        "gamePathLinux": game_path_linux,
        "selectedProfile": selected,
    }
    return meta, executables


def find_mo2_exe_near_ini(ini_dir: str, prefix_path: str) -> str:
    local = os.path.join(ini_dir, "ModOrganizer.exe")
    if os.path.isfile(local):
        return local
    dc = drive_c_path(prefix_path) if prefix_path else ""
    for rel in MO2_EXE_CANDIDATES:
        if dc:
            candidate = os.path.join(dc, rel.replace("/", os.sep))
            if os.path.isfile(candidate):
                return candidate
    return local


def scan_instances(
    indexer: PrefixIndexer | None = None,
    custom_paths: list[str] | None = None,
) -> list[MO2Instance]:
    indexer = indexer or PrefixIndexer()
    if not indexer.entries:
        indexer.build()

    found: dict[str, MO2Instance] = {}
    roots = get_storage_roots()
    portable_dirs = [
        os.path.join(r, sub) for r in roots for sub in ("Games", "Downloads", "Desktop")
    ]
    if custom_paths:
        portable_dirs.extend(custom_paths)

    for base in portable_dirs:
        if not os.path.isdir(base):
            continue
        _walk_portable(base, max_depth=4, found=found, indexer=indexer)

    for entry in indexer.entries:
        if not entry.prefix_path:
            continue
        dc = drive_c_path(entry.prefix_path)
        if os.path.isdir(dc):
            _walk_portable(dc, max_depth=3, found=found, indexer=indexer, host_entry=entry)
        global_root = os.path.join(dc, str(GLOBAL_MO2))
        if os.path.isdir(global_root):
            for name in os.listdir(global_root):
                ini = os.path.join(global_root, name, "ModOrganizer.ini")
                if os.path.isfile(ini):
                    _ingest_ini(
                        ini,
                        instance_type="global",
                        instance_name=name,
                        host_entry=entry,
                        found=found,
                        indexer=indexer,
                    )

    return sorted(found.values(), key=lambda x: x.displayName.lower())


def _walk_portable(
    base: str,
    max_depth: int,
    found: dict[str, MO2Instance],
    indexer: PrefixIndexer,
    host_entry: PrefixEntry | None = None,
    depth: int = 0,
) -> None:
    if depth > max_depth:
        return
    try:
        for entry in os.scandir(base):
            if entry.is_dir(follow_symlinks=False):
                _walk_portable(
                    entry.path, max_depth, found, indexer, host_entry, depth + 1
                )
            elif entry.name.lower() == "modorganizer.ini":
                _ingest_ini(
                    entry.path,
                    instance_type="portable",
                    instance_name="Portable",
                    host_entry=host_entry,
                    found=found,
                    indexer=indexer,
                )
    except OSError:
        return


def _ingest_ini(
    ini_path: str,
    instance_type: str,
    instance_name: str,
    host_entry: PrefixEntry | None,
    found: dict[str, MO2Instance],
    indexer: PrefixIndexer,
) -> None:
    ini_dir = os.path.dirname(ini_path)
    prefix_guess = ""
    if host_entry:
        prefix_guess = host_entry.prefix_path
    elif "pfx" in ini_path or "drive_c" in ini_path:
        parts = Path(ini_path).parts
        for i, part in enumerate(parts):
            if part == "pfx" and i > 0:
                prefix_guess = os.path.join(*parts[:i])
                break
            if part == "drive_c" and i > 0:
                prefix_guess = os.path.join(*parts[:i])
                break

    meta, executables = parse_modorganizer_ini(ini_path, prefix_guess)
    mo2_exe = find_mo2_exe_near_ini(ini_dir, prefix_guess)
    matched = indexer.match_install_path(meta.get("gamePathLinux", ""))
    entry = host_entry or matched

    launcher = entry.launcher_source if entry else "custom"
    prefix = entry.prefix_path if entry else prefix_guess
    proton = entry.proton_binary_path if entry else ""
    env = dict(entry.env_overrides) if entry else {}

    if instance_type == "global" and host_entry and not matched:
        launcher = host_entry.launcher_source
        prefix = host_entry.prefix_path
        proton = host_entry.proton_binary_path
        env = dict(host_entry.env_overrides)

    game_name = meta.get("gameName") or "Unknown Game"
    badge = launcher.title() if launcher != "custom" else instance_type.title()
    display = f"{game_name} ({badge})"

    inst = MO2Instance(
        id=instance_id(ini_path, instance_name),
        displayName=display,
        instanceType=instance_type,
        instanceName=instance_name,
        gameName=game_name,
        gamePathLinux=meta.get("gamePathLinux", ""),
        mo2ExeLinux=mo2_exe,
        mo2IniLinux=ini_path,
        selectedProfile=meta.get("selectedProfile", ""),
        executables=[
            {"title": e.title, "binary": e.binary, "arguments": e.arguments}
            for e in executables
        ],
        defaultExecutable=pick_default_executable(executables),
        launcherSource=launcher,
        prefixPath=prefix,
        protonBinaryPath=proton,
        envOverrides=env,
    )
    _validate_instance(inst)
    found[inst.id] = inst


def _validate_instance(inst: MO2Instance) -> None:
    errors: list[str] = []
    if not inst.mo2ExeLinux or not os.path.isfile(inst.mo2ExeLinux):
        errors.append("ModOrganizer.exe not found")
    if not inst.prefixPath or not os.path.isdir(inst.prefixPath):
        errors.append("Wine/Proton prefix not resolved")
    if not inst.protonBinaryPath or not os.path.isfile(inst.protonBinaryPath):
        errors.append("Proton binary not resolved")
    if errors:
        inst.isValid = False
        inst.validationError = "; ".join(errors)
    else:
        inst.isValid = True
        inst.validationError = None