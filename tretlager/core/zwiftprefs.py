"""Zwift's own settings file (prefs.xml in the Wine prefix), as far as Tretlager has to touch it.

Only one key: `PREFER_NATIVE_BLE`. With 1 (Zwift's default on Windows) Zwift insists on the
computer's own Bluetooth, which does not exist under Wine, and never asks the Companion app for
sensors: the pairing screen then searches forever. On Windows the pairing screen offers a switch
for this; under Wine it does not appear. With 0 Zwift scans through the phone ("Starting ZC scan"
in Zwift's Log.txt). Zwift writes the file when it exits, so only change it while Zwift is closed.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import paths

KEY = "PREFER_NATIVE_BLE"
_TAG = re.compile(rf"<{KEY}>\s*([01])\s*</{KEY}>")


def user_dirs(prefix: Path | None = None) -> list[Path]:
    """Zwift's settings folders of the Windows users in the prefix (normally exactly one)."""
    users = (prefix or paths.PREFIX) / "drive_c" / "users"
    return [u / "AppData" / "Local" / "Zwift" for u in sorted(users.glob("*"))
            if u.is_dir() and u.name.lower() != "public"]


def set_prefer_native_ble(native: bool, prefix: Path | None = None) -> bool:
    """Tell Zwift where to look for Bluetooth sensors: on this computer (True, Zwift's default)
    or through the Companion app (False). Returns True if a file was changed.

    For the Companion app a missing file or key is created (Zwift adds everything else itself);
    back to the default only an existing key is reset, nothing is created.
    """
    value = "1" if native else "0"
    changed = False
    for folder in user_dirs(prefix):
        file = folder / "prefs.xml"
        try:
            text = file.read_text(encoding="utf-8", errors="surrogateescape")
        except FileNotFoundError:
            if native:
                continue
            folder.mkdir(parents=True, exist_ok=True)
            file.write_text(f"<ZWIFT><CONFIG><{KEY}>0</{KEY}></CONFIG></ZWIFT>\n")
            changed = True
            continue
        found = _TAG.search(text)
        if found:
            if found.group(1) == value:
                continue
            new = _TAG.sub(f"<{KEY}>{value}</{KEY}>", text)
        elif native or "</CONFIG>" not in text:
            continue
        else:
            new = text.replace("</CONFIG>", f"    <{KEY}>0</{KEY}>\n    </CONFIG>", 1)
        tmp = file.with_suffix(".tmp")
        tmp.write_text(new, encoding="utf-8", errors="surrogateescape")
        tmp.replace(file)
        changed = True
    return changed
