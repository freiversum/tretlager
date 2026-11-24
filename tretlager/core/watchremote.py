"""Watch remote: a Garmin watch running the ZWindoor app steers Zwift (turns, Ride On, power-up …).

The watch can only act as a Bluetooth LE central, so Tretlager offers a small GATT service on the
same adapter the sensor bridge uses and types the matching Zwift keyboard shortcuts into the Wine
window via XTest. The core comes from the ZWindoor project (tretlager/zwindoor, vendored).

Runs inside the interface process (not in the sensor bridge): it needs the X11 display Wine uses,
and it also works when the sensors come through the Zwift Companion app. Off by default; the
switch is kept in state.json ("watch_remote").
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from ..i18n import LANGUAGE
from . import applog, bridgectl, login, paths, state

CONFIG_FILE = paths.STATE / "watch-remote.json"
HISTORY = 5

# Buttons on the page "Watch remote" -> (action, value) of the ZWindoor protocol
TEST_ACTIONS = {
    "left": (0x18, 1), "right": (0x19, 1), "straight": (0x10, 1), "uturn": (0x37, 1),
    "rideon": (0x20, 0x01), "powerup": (0x50, 1),
}


def wanted() -> bool:
    return bool(state.load().get("watch_remote", {}).get("enabled", False))


def set_wanted(on: bool) -> None:
    state.update("watch_remote", enabled=on)


def companion_allowed() -> bool:
    """The Companion link replaces the phone registered with Zwift. With sensors through the real
    Zwift Companion app that would cut the sensors off, so the link is not offered then."""
    return not bridgectl.companion()


def zwift_token() -> str | None:
    """Access token for the Companion link from Tretlager's sign-in (keyring); None = sign in first.
    Blocking (may refresh over the network); the core calls it from a worker thread."""
    if not companion_allowed():
        return None
    try:
        token = login.valid_token()
    except login.LoginError as e:
        applog.warning("Watch remote: Zwift token: %s", e)
        return None
    return (token or {}).get("access_token")


def _route_logs() -> None:
    """Send the core's log lines to tretlager.log."""
    core = logging.getLogger("tretlager.zwindoor")
    if not core.handlers:
        for h in logging.getLogger("tretlager.app").handlers:
            core.addHandler(h)
        core.setLevel(logging.INFO)
        core.propagate = False


class WatchRemote:
    """Owns the bridge runner; `on_change` is called from the runner thread on every change."""

    def __init__(self, on_change: Callable[[], None]) -> None:
        self.on_change = on_change
        self.runner = None
        self.events: list[dict] = []
        self.sink_error = ""

    def _make_runner(self):
        from ..zwindoor.config import Config
        from ..zwindoor.runner import BridgeRunner
        from ..zwindoor.sinks import KeySink, SinkError
        try:
            from ..zwindoor.sinks.xtest import XTestSink
            sink = XTestSink()
            self.sink_error = ""
        except SinkError as e:
            applog.warning("Watch remote: no keyboard output (%s)", e)
            sink, self.sink_error = KeySink(), str(e)
        runner = BridgeRunner(Config.load(CONFIG_FILE), config_path=CONFIG_FILE, sink=sink, token_provider=zwift_token)
        runner.on_event.append(self._event)
        runner.on_state.append(lambda _s: self.on_change())
        runner.on_status.append(self.on_change)
        return runner

    @property
    def running(self) -> bool:
        return bool(self.runner and self.runner.thread and self.runner.thread.is_alive())

    def start(self) -> None:
        if self.running:
            return
        _route_logs()
        self.runner = self._make_runner()
        self.runner.start_thread()
        applog.info("Watch remote started")
        self.on_change()

    def stop(self) -> None:
        if self.runner:
            self.runner.stop()
            applog.info("Watch remote stopped")
        self.runner = None
        self.on_change()

    def _event(self, ev) -> None:
        self.events = [{"time": time.strftime("%H:%M:%S", time.localtime(ev.when)), "action": ev.action_de if LANGUAGE == "de" else ev.action,
                        "result": ev.result.name.lower(), "ms": round(ev.ms)}] + self.events[:HISTORY - 1]
        self.on_change()

    def set_option(self, name: str, value: bool) -> None:
        if self.runner:
            self.runner.update_config(**{name: value})
        else:
            from ..zwindoor.config import Config
            c = Config.load(CONFIG_FILE)
            setattr(c, name, value)
            c.save(CONFIG_FILE)
        self.on_change()

    def test(self, name: str) -> bool:
        if not self.runner or name not in TEST_ACTIONS:
            return False
        return self.runner.test_action(*TEST_ACTIONS[name]) is not None

    def snapshot(self) -> dict:
        from ..zwindoor.config import Config
        from ..zwindoor.protocol import State
        r = self.runner
        cfg = r.config if r else Config.load(CONFIG_FILE)
        s = r.zwift_state if r else State(0)
        return {
            "enabled": wanted(), "running": bool(r and r.running), "error": (r.error if r else "") or "",
            "keyboardError": self.sink_error, "watch": bool(r and r.watch_connected),
            "keyboardBlocked": bool(r and r.engine and r.engine.blocked),
            "zwiftRunning": bool(s & State.ZWIFT_RUNNING), "zwiftFocused": bool(s & State.ZWIFT_FOCUSED),
            "obcConnected": bool(s & State.OBC_CONNECTED),
            "obc": cfg.obc, "bringToFront": cfg.bring_to_front, "events": list(self.events),
            "companion": cfg.companion, "companionAllowed": companion_allowed(),
            "companionLinked": bool(s & State.COMPANION),
            "companionRegistered": bool(r and r.companion and r.companion.registered),
            "companionError": (r.companion.error if r and r.companion else "") or "",
            "companionNoLogin": bool(r and r.companion and r.companion.error == "no Zwift sign-in"),
        }
