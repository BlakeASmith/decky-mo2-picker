import pytest

from mo2_launcher.path_utils import get_storage_roots, strip_bytearray, win_to_linux_path


def test_strip_bytearray():
    assert strip_bytearray('@ByteArray(Z:\\\\home\\\\deck\\\\Games)') == "Z:\\\\home\\\\deck\\\\Games"


def test_win_to_linux_z_drive():
    assert win_to_linux_path("Z:/home/deck/Games/Fallout4", "/prefix") == "/home/deck/Games/Fallout4"


def test_win_to_linux_c_drive_with_pfx(tmp_path):
    prefix = tmp_path / "compat" / "377160" / "pfx" / "drive_c"
    prefix.mkdir(parents=True)
    result = win_to_linux_path(
        "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4",
        str(tmp_path / "compat" / "377160"),
    )
    assert result.endswith("Fallout 4")
    assert "/pfx/drive_c/" in result


def test_storage_roots_includes_home():
    roots = get_storage_roots()
    assert any("deck" in r or r.startswith("/home") for r in roots)