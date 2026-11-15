import textwrap
from pathlib import Path

import pytest

from mo2_launcher.mo2_scanner import parse_modorganizer_ini, pick_default_executable, instance_id
from mo2_launcher.mo2_scanner import MO2Executable


def test_instance_id_stable():
    assert instance_id("/a/ModOrganizer.ini", "Portable") == instance_id(
        "/a/ModOrganizer.ini", "Portable"
    )


def test_pick_default_executable_prefers_f4se():
    exes = [
        MO2Executable("Fallout 4", "", ""),
        MO2Executable("F4SE", "", ""),
    ]
    assert pick_default_executable(exes) == "F4SE"


def test_parse_modorganizer_ini(tmp_path: Path):
    ini = tmp_path / "ModOrganizer.ini"
    ini.write_text(
        textwrap.dedent(
            """
            [General]
            gameName=Fallout 4
            gamePath=Z:/home/deck/Games/Fallout4
            selected_profile=Default
            [customExecutables]
            size=1
            1\\title=F4SE
            1\\binary=Z:/home/deck/Games/Fallout4/f4se_loader.exe
            1\\arguments=
            """
        ).strip(),
        encoding="utf-8",
    )
    meta, exes = parse_modorganizer_ini(str(ini), "/prefix")
    assert meta["gameName"] == "Fallout 4"
    assert meta["gamePathLinux"] == "/home/deck/Games/Fallout4"
    assert len(exes) == 1
    assert exes[0].title == "F4SE"