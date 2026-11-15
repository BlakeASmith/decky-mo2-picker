"""Launch MO2 GUI or headless moshortcut inside the correct prefix."""

from __future__ import annotations

import os
import pwd
import subprocess
import glob
from typing import Any

from .path_utils import prefix_has_pfx

DECK_USER = "deck"


def demote_to_deck() -> None:
    pw = pwd.getpwnam(DECK_USER)
    os.setgid(pw.pw_gid)
    os.setuid(pw.pw_uid)


def build_session_env() -> dict[str, str]:
    uid = pwd.getpwnam(DECK_USER).pw_uid
    runtime = f"/run/user/{uid}"
    env: dict[str, str] = {
        "HOME": f"/home/{DECK_USER}",
        "USER": DECK_USER,
        "LOGNAME": DECK_USER,
        "XDG_RUNTIME_DIR": runtime,
        "DISPLAY": ":0",
        "WAYLAND_DISPLAY": "gamescope-0",
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path={runtime}/bus",
    }
    for pattern in (f"{runtime}/gamescope-*", "/tmp/.X11-unix/X*"):
        matches = sorted(glob.glob(pattern))
        if matches and "gamescope" in pattern:
            env["WAYLAND_DISPLAY"] = os.path.basename(matches[-1])
        elif matches and "X11" in pattern:
            env["DISPLAY"] = ":" + os.path.basename(matches[-1]).lstrip("X")
    env_path = os.path.join(runtime, "environment")
    if os.path.isfile(env_path):
        try:
            with open(env_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "=" in line:
                        key, val = line.strip().split("=", 1)
                        if key in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR"):
                            env[key] = val
        except OSError:
            pass
    return env


def build_proton_command(
    instance: dict[str, Any],
    *,
    executable_title: str | None = None,
) -> tuple[list[str], dict[str, str]]:
    proton = instance["protonBinaryPath"]
    mo2_exe = instance["mo2ExeLinux"]
    prefix = instance["prefixPath"]
    env = build_session_env()
    env.update(instance.get("envOverrides") or {})

    steam_root = os.path.expanduser("~/.local/share/Steam")
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = steam_root

    use_wine64 = os.path.isdir(os.path.join(prefix, "drive_c")) and not prefix_has_pfx(
        prefix
    )
    argv: list[str]

    if use_wine64:
        proton_dir = os.path.dirname(proton)
        wine64 = os.path.join(proton_dir, "files", "bin", "wine64")
        if not os.path.isfile(wine64):
            wine64 = os.path.join(proton_dir, "dist", "bin", "wine64")
        env["WINEPREFIX"] = prefix
        argv = [wine64, mo2_exe]
        if instance["instanceType"] == "global":
            argv.extend(["-i", instance["instanceName"]])
        if executable_title:
            argv.append(f"moshortcut://:{executable_title}")
    else:
        env["STEAM_COMPAT_DATA_PATH"] = prefix
        argv = [proton, "run", mo2_exe]
        if instance["instanceType"] == "global":
            argv.extend(["-i", instance["instanceName"]])
        if executable_title:
            argv.append(f"moshortcut://:{executable_title}")

    return argv, env


def launch_instance(
    instance: dict[str, Any],
    *,
    executable_title: str | None = None,
    logger: Any | None = None,
) -> None:
    argv, env = build_proton_command(instance, executable_title=executable_title)
    if logger:
        logger.info("MO2 launch argv=%s", argv)
        logger.info("MO2 launch env=%s", {k: env[k] for k in sorted(env) if k.startswith(("STEAM", "WINE", "PROTON", "WAYLAND", "DISPLAY"))})
    subprocess.Popen(
        argv,
        env={**os.environ, **env},
        preexec_fn=demote_to_deck,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )