"""Zwift's photos and clips after the ride (Overview → Zwift, state.json "media.after_ride").

Zwift saves photos (with and without the HUD, `…_clean.jpg`) to `Pictures/Zwift` and video clips
(F9) to `Videos/Zwift` in the Windows profile of the Wine environment, where nobody finds them.
Once Zwift has ended, Tretlager handles the files of that ride as chosen:

  keep   leave them where Zwift put them (default, as before)
  move   move them to the user's Pictures and Videos folders, subfolder Zwift
  trash  move them to the trash: Zwift has already uploaded the photos to Zwift or Strava, and
         many riders do not want to archive them on the computer

Only files written since the start of Zwift are touched, older ones stay. The trash goes through
the Trash portal (org.freedesktop.portal.Trash) first. On tinytin (TUXEDO OS, Plasma,
xdg-desktop-portal 1.22.1) the portal answered 0 for every file, also outside the Flatpak, while
`gio trash` worked; so Tretlager then follows the freedesktop.org trash specification itself
(`~/.local/share/Trash/files` plus a `.trashinfo`, Flatpak permission `xdg-data/Trash`), like file
managers do. If that fails too, the file stays.
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import time
import urllib.parse
from pathlib import Path

from . import applog, paths, state

MODES = ("keep", "move", "trash")
KINDS = {"pictures": ("Pictures", "XDG_PICTURES_DIR"), "videos": ("Videos", "XDG_VIDEOS_DIR")}
SUBFOLDER = "Zwift"
PORTAL = "org.freedesktop.portal.Desktop"
PORTAL_PATH = "/org/freedesktop/portal/desktop"


def mode() -> str:
    value = state.load().get("media", {}).get("after_ride", "keep")
    return value if value in MODES else "keep"


def set_mode(value: str) -> None:
    if value in MODES:
        state.update("media", after_ride=value)


def _user_dirs_files() -> list[Path]:
    # In the Flatpak XDG_CONFIG_HOME is the app's own; Flatpak puts the host's user-dirs.dirs there.
    config = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return [Path(config) / "user-dirs.dirs", Path.home() / ".config" / "user-dirs.dirs"]


def xdg_dir(kind: str, files: list[Path] | None = None) -> Path:
    """The user's Pictures or Videos folder (xdg-user-dirs), e.g. ~/Bilder on a German desktop."""
    english, key = KINDS[kind]
    for f in files if files is not None else _user_dirs_files():
        try:
            text = f.read_text()
        except OSError:
            continue
        m = re.search(rf'^{key}="(.*)"\s*$', text, re.M)
        if m:
            value = m.group(1).replace("$HOME", str(Path.home()))
            if value and Path(value) != Path.home():  # $HOME means "disabled"
                return Path(value)
    return Path.home() / english


def target(kind: str) -> Path:
    return xdg_dir(kind) / SUBFOLDER


def zwift_folders(prefix: Path | None = None) -> dict[str, list[Path]]:
    """Zwift's own folders per kind (one per Windows user in the environment)."""
    root = prefix or paths.PREFIX
    return {kind: sorted(p for p in root.glob(f"drive_c/users/*/{english}/{SUBFOLDER}") if p.is_dir())
            for kind, (english, _key) in KINDS.items()}


def ride_files(since: float, prefix: Path | None = None) -> dict[str, list[Path]]:
    """Files Zwift wrote since `since` (time.time() at the start), per kind."""
    out: dict[str, list[Path]] = {}
    for kind, folders in zwift_folders(prefix).items():
        files = []
        for folder in folders:
            for f in folder.iterdir():
                try:
                    if f.is_file() and f.stat().st_mtime >= since - 2:
                        files.append(f)
                except OSError:
                    pass
        out[kind] = sorted(files)
    return out


def _free_name(folder: Path, name: str) -> Path:
    dest = folder / name
    stem, suffix, n = dest.stem, dest.suffix, 1
    while dest.exists():
        dest = folder / f"{stem}-{n}{suffix}"
        n += 1
    return dest


async def _trash_async(path: Path) -> bool:
    from dbus_fast import Message, MessageType
    from dbus_fast.aio import MessageBus

    bus = await MessageBus(negotiate_unix_fd=True).connect()
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
        try:
            reply = await bus.call(Message(destination=PORTAL, path=PORTAL_PATH,
                                           interface="org.freedesktop.portal.Trash", member="TrashFile",
                                           signature="h", body=[0], unix_fds=[fd]))
        finally:
            os.close(fd)
        if reply.message_type == MessageType.ERROR:
            applog.warning("Trash portal refused (%s)", reply.error_name)
            return False
        return reply.body[0] == 1
    finally:
        bus.disconnect()


def home_trash() -> Path:
    # Not XDG_DATA_HOME: in the Flatpak that is the app's own folder.
    return Path.home() / ".local" / "share" / "Trash"


def trash_by_spec(path: Path, trash: Path | None = None) -> bool:
    """Move a file to the home trash following the freedesktop.org trash specification."""
    trash = trash or home_trash()
    files, info = trash / "files", trash / "info"
    try:
        files.mkdir(parents=True, exist_ok=True)
        info.mkdir(parents=True, exist_ok=True)
        stem, suffix, n = path.stem, path.suffix, 0
        while True:  # claim a name by creating its .trashinfo exclusively
            name = path.name if n == 0 else f"{stem}.{n}{suffix}"
            try:
                fd = os.open(info / f"{name}.trashinfo", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                break
            except FileExistsError:
                n += 1
        with os.fdopen(fd, "w") as f:
            f.write("[Trash Info]\nPath={}\nDeletionDate={}\n".format(
                urllib.parse.quote(str(path.absolute())), time.strftime("%Y-%m-%dT%H:%M:%S")))
        try:
            shutil.move(str(path), str(files / name))
        except OSError:
            (info / f"{name}.trashinfo").unlink(missing_ok=True)
            raise
        return True
    except OSError as e:
        applog.warning("Trash: %s", type(e).__name__)
        return False


def trash_file(path: Path) -> bool:
    """Move a file to the trash, through the portal or else by the specification; True on success."""
    try:
        if asyncio.run(_trash_async(path)):
            return True
    except Exception as e:  # no session bus, no portal
        applog.warning("Trash portal: %s", type(e).__name__)
    return trash_by_spec(path)


def after_ride(since: float, prefix: Path | None = None, trash=trash_file,
               targets: dict[str, Path] | None = None) -> dict[str, int]:
    """Handle the ride's photos and clips as set; returns how many files per kind were handled."""
    current = mode()
    done = {kind: 0 for kind in KINDS}
    if current == "keep":
        return done
    for kind, files in ride_files(since, prefix).items():
        for f in files:
            if current == "move":
                folder = (targets or {}).get(kind) or target(kind)
                folder.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), str(_free_name(folder, f.name)))
                done[kind] += 1
            elif trash(f):
                done[kind] += 1
    return done
