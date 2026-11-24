"""Watch remote: Tretlager glue around the vendored Zwindoor core."""

import asyncio
import time

import pytest

from tretlager.core import paths, state, watchremote
from tretlager.zwindoor import actions
from tretlager.zwindoor.ble import Peripheral
from tretlager.zwindoor.config import Config
from tretlager.zwindoor.protocol import Command, Result, encode_command
from tretlager.zwindoor.runner import BridgeRunner
from tretlager.zwindoor.sinks import RecordingSink


@pytest.fixture(autouse=True)
def tmp_state(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "STATE", tmp_path)
    monkeypatch.setattr(watchremote, "CONFIG_FILE", tmp_path / "watch-remote.json")


class FakePeripheral(Peripheral):
    """Stands in for BlueZ: lets the test write commands like the watch."""
    instances = []

    def __init__(self, on_write, info, adapter=""):
        super().__init__(on_write, info)
        self.notified = []
        FakePeripheral.instances.append(self)

    async def start(self):
        pass

    async def notify(self, data):
        self.notified.append(data)

    async def stop(self):
        pass


def test_off_by_default_and_switch_is_persistent():
    assert not watchremote.wanted()
    watchremote.set_wanted(True)
    assert watchremote.wanted()
    assert state.load()["watch_remote"]["enabled"] is True


def test_snapshot_without_runner():
    snap = watchremote.WatchRemote(lambda: None).snapshot()
    assert snap["running"] is False and snap["watch"] is False and snap["events"] == []
    assert snap["bringToFront"] is True and snap["obc"] is False


def test_option_without_runner_is_saved():
    wr = watchremote.WatchRemote(lambda: None)
    wr.set_option("obc", True)
    assert Config.load(watchremote.CONFIG_FILE).obc is True


def test_test_actions_are_known():
    for action, value in watchremote.TEST_ACTIONS.values():
        assert actions.find(action, value), (action, value)


def test_runner_end_to_end_with_fake_radio():
    FakePeripheral.instances.clear()
    changes = []
    wr = watchremote.WatchRemote(lambda: changes.append(1))
    sink = RecordingSink()
    wr._make_runner = lambda: _runner(wr, sink)
    wr.start()
    try:
        for _ in range(100):
            if wr.runner.running:
                break
            time.sleep(0.02)
        assert wr.runner.running
        periph = FakePeripheral.instances[0]
        fut = asyncio.run_coroutine_threadsafe(
            periph.on_write(encode_command(Command(9, actions.STEER_RIGHT, 1))), wr.runner.loop)
        assert fut.result(2) == bytes((0x01, 9, Result.OK))
        assert [k.keysym for kind, k in sink.events if kind == "press"] == [0xFF53]
        snap = wr.snapshot()
        assert snap["watch"] and snap["events"][0]["action"] == "Turn right" and snap["events"][0]["result"] == "ok"
        assert wr.test("rideon")
    finally:
        wr.stop()
    assert changes and not wr.running


def _runner(wr, sink):
    r = BridgeRunner(Config(hold_ms=1), config_path=watchremote.CONFIG_FILE, sink=sink,
                     peripheral_factory=FakePeripheral)
    r.on_event.append(wr._event)
    r.on_status.append(wr.on_change)
    return r


def test_companion_link_blocked_with_companion_sensors(monkeypatch):
    from tretlager.core import bridgectl, login
    monkeypatch.setattr(login, "valid_token", lambda: {"access_token": "abc"})
    monkeypatch.setattr(bridgectl, "companion", lambda: False)
    assert watchremote.companion_allowed() and watchremote.zwift_token() == "abc"
    monkeypatch.setattr(bridgectl, "companion", lambda: True)
    assert not watchremote.companion_allowed() and watchremote.zwift_token() is None


def test_zwift_token_without_sign_in(monkeypatch):
    from tretlager.core import bridgectl, login
    monkeypatch.setattr(bridgectl, "companion", lambda: False)
    monkeypatch.setattr(login, "valid_token", lambda: None)
    assert watchremote.zwift_token() is None

    def offline():
        raise login.LoginUnavailable("offline")
    monkeypatch.setattr(login, "valid_token", offline)
    assert watchremote.zwift_token() is None


def test_snapshot_has_companion_fields(monkeypatch):
    from tretlager.core import bridgectl
    monkeypatch.setattr(bridgectl, "companion", lambda: False)
    snap = watchremote.WatchRemote(lambda: None).snapshot()
    assert snap["companion"] is False and snap["companionAllowed"] is True
    assert snap["companionLinked"] is False and snap["companionNoLogin"] is False
