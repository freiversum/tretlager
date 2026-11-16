"""Sensors through the Zwift Companion app instead of the bridge: the bridge must stay off."""
import importlib
import subprocess
from pathlib import Path

import pytest

from tretlager.core import bridgectl, launch, systemcheck


@pytest.fixture
def fresh_state(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    from tretlager.core import paths, state
    importlib.reload(paths); importlib.reload(state)
    monkeypatch.setattr(bridgectl, "state", state)
    monkeypatch.setattr(bridgectl, "IN_FLATPAK", False)
    return state


def gdbus_run(responses, seen):
    def run(cmd, **_kw):
        seen.append(cmd)
        method = cmd[cmd.index("--method") + 1].rsplit(".", 1)[-1]
        out, rc = responses.get(method, ("", 1))
        return subprocess.CompletedProcess(cmd, rc, out, "" if rc == 0 else "error")
    return run


def test_bridge_is_the_default(fresh_state):
    assert bridgectl.companion() is False and bridgectl.wanted() is True


def test_companion_stops_bridge_and_autostart(fresh_state):
    bridgectl.set_autostart(True)
    seen = []
    bridgectl.set_source("companion", run=gdbus_run({"NameHasOwner": ("(true,)", 0), "Quit": ("(true,)", 0)}, seen))
    assert bridgectl.companion() is True and bridgectl.wanted() is False
    assert bridgectl.autostart() is False
    assert any("de.linuxundich.Tretlager.Bridge.Quit" in c for c in seen)


def test_back_to_bridge(fresh_state):
    seen = []
    bridgectl.set_source("companion", run=gdbus_run({"NameHasOwner": ("(false,)", 0)}, seen))
    bridgectl.set_source("bridge", run=gdbus_run({}, seen))
    assert bridgectl.wanted() is True
    assert fresh_state.load()["sensors"]["source"] == "bridge"


def test_unknown_source_is_rejected(fresh_state):
    with pytest.raises(ValueError):
        bridgectl.set_source("ant")
    assert bridgectl.companion() is False


def test_launch_never_starts_bridge_with_companion(fresh_state, monkeypatch):
    fresh_state.update("sensors", source="companion")
    calls, log = [], []
    monkeypatch.setattr(bridgectl, "is_running", lambda *a, **k: True)
    monkeypatch.setattr(bridgectl, "set_running", lambda on, *a, **k: calls.append(on))
    launch.Launcher(lambda *a, **k: None, log.append).ensure_bridge()
    assert calls == [False]  # a bridge left running is stopped, never started
    assert "Companion" in log[0]


def test_launch_starts_bridge_by_default(fresh_state, monkeypatch):
    calls = []
    monkeypatch.setattr(bridgectl, "is_running", lambda *a, **k: False)
    monkeypatch.setattr(bridgectl, "set_running", lambda on, *a, **k: calls.append(on))
    launch.Launcher(lambda *a, **k: None, lambda _t: None).ensure_bridge()
    assert calls == [True]


def test_system_check_skips_bluetooth_and_avahi(monkeypatch):
    for name in ("check_system", "check_bluetooth", "check_avahi", "check_disk", "check_network",
                 "check_wine", "check_existing"):
        monkeypatch.setattr(systemcheck, name,
                            lambda name=name: systemcheck.Check(name, name, systemcheck.OK, ""))
    monkeypatch.setattr(systemcheck, "check_graphics", lambda: [])
    with_bridge = [c.id for c in systemcheck.run_all(companion=False)]
    with_companion = [c.id for c in systemcheck.run_all(companion=True)]
    assert "check_bluetooth" in with_bridge and "check_avahi" in with_bridge
    assert set(with_bridge) - set(with_companion) == {"check_bluetooth", "check_avahi"}


def test_warnings_name_the_companion_route():
    qml = Path(bridgectl.__file__).parent.parent / "kde" / "qml"
    for page in ("WarningDialog.qml", "WelcomePage.qml", "AboutPage.qml"):
        text = (qml / page).read_text()
        assert "Companion app instead of the bridge" in text, page
        assert "Sensor bridge: at your own risk" in text, page


# --- Zwift's own switch: without it Zwift never asks the phone for sensors ---

PREFS = """<ZWIFT>
    <CONFIG>
        <PREFER_NATIVE_BLE>1</PREFER_NATIVE_BLE>
        <LANGUAGE>en</LANGUAGE>
    </CONFIG>
</ZWIFT>
"""


def zwift_folder(prefix, user="rider"):
    folder = prefix / "drive_c" / "users" / user / "AppData" / "Local" / "Zwift"
    folder.mkdir(parents=True)
    return folder


def test_prefs_switch_to_companion_and_back(tmp_path):
    from tretlager.core import zwiftprefs
    file = zwift_folder(tmp_path) / "prefs.xml"
    file.write_text(PREFS)
    assert zwiftprefs.set_prefer_native_ble(False, tmp_path) is True
    assert "<PREFER_NATIVE_BLE>0</PREFER_NATIVE_BLE>" in file.read_text()
    assert "<LANGUAGE>en</LANGUAGE>" in file.read_text()
    assert zwiftprefs.set_prefer_native_ble(False, tmp_path) is False  # already set: file untouched
    assert zwiftprefs.set_prefer_native_ble(True, tmp_path) is True
    assert file.read_text() == PREFS


def test_prefs_key_or_file_missing(tmp_path):
    from tretlager.core import zwiftprefs
    folder = zwift_folder(tmp_path)
    (tmp_path / "drive_c" / "users" / "Public").mkdir()
    assert zwiftprefs.set_prefer_native_ble(True, tmp_path) is False  # default: create nothing
    assert not (folder / "prefs.xml").exists()
    assert zwiftprefs.set_prefer_native_ble(False, tmp_path) is True  # before Zwift's first start
    assert "<PREFER_NATIVE_BLE>0</PREFER_NATIVE_BLE>" in (folder / "prefs.xml").read_text()
    assert not (tmp_path / "drive_c" / "users" / "Public" / "AppData").exists()
    (folder / "prefs.xml").write_text("<ZWIFT>\n    <CONFIG>\n        <METRIC>1</METRIC>\n    </CONFIG>\n</ZWIFT>\n")
    assert zwiftprefs.set_prefer_native_ble(False, tmp_path) is True
    text = (folder / "prefs.xml").read_text()
    assert "<PREFER_NATIVE_BLE>0</PREFER_NATIVE_BLE>" in text and "<METRIC>1</METRIC>" in text


def test_launch_sets_zwift_switch(fresh_state, monkeypatch, tmp_path):
    from tretlager.core import zwiftprefs
    file = zwift_folder(tmp_path) / "prefs.xml"
    file.write_text(PREFS)
    monkeypatch.setattr(zwiftprefs.paths, "PREFIX", tmp_path)
    log = []
    launcher = launch.Launcher(lambda *a, **k: None, log.append)
    launcher.ensure_sensor_route()
    assert log == [] and file.read_text() == PREFS  # bridge: Zwift's default stays
    fresh_state.update("sensors", source="companion")
    launcher.ensure_sensor_route()
    assert "<PREFER_NATIVE_BLE>0</PREFER_NATIVE_BLE>" in file.read_text() and "Companion" in log[0]
