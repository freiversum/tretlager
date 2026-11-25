"""Zwift's photos and clips after the ride (core/media.py)."""

import os
import time

import pytest

from tretlager.core import media, paths


@pytest.fixture
def prefix(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "STATE", tmp_path / "state")
    root = tmp_path / "prefix"
    pics = root / "drive_c/users/rider/Pictures/Zwift"
    vids = root / "drive_c/users/rider/Videos/Zwift"
    pics.mkdir(parents=True)
    vids.mkdir(parents=True)
    old = time.time() - 3600
    for name in ("old.jpg", "old_clean.jpg"):
        (pics / name).write_text("x")
        os.utime(pics / name, (old, old))
    (pics / "ride.jpg").write_text("x")
    (pics / "ride_clean.jpg").write_text("x")
    (vids / "ride.mp4").write_text("x")
    return root


def test_default_keeps_everything(prefix):
    assert media.mode() == "keep"
    assert media.after_ride(time.time() - 60, prefix) == {"pictures": 0, "videos": 0}
    assert len(list(prefix.glob("drive_c/users/*/*/Zwift/*"))) == 5


def test_only_files_of_the_ride(prefix):
    files = media.ride_files(time.time() - 60, prefix)
    assert [f.name for f in files["pictures"]] == ["ride.jpg", "ride_clean.jpg"]
    assert [f.name for f in files["videos"]] == ["ride.mp4"]


def test_move_to_user_folders_without_overwriting(prefix, tmp_path):
    media.set_mode("move")
    targets = {"pictures": tmp_path / "Bilder/Zwift", "videos": tmp_path / "Videos/Zwift"}
    targets["pictures"].mkdir(parents=True)
    (targets["pictures"] / "ride.jpg").write_text("earlier")
    done = media.after_ride(time.time() - 60, prefix, targets=targets)
    assert done == {"pictures": 2, "videos": 1}
    assert sorted(f.name for f in targets["pictures"].iterdir()) == ["ride-1.jpg", "ride.jpg", "ride_clean.jpg"]
    assert (targets["pictures"] / "ride.jpg").read_text() == "earlier"
    assert (targets["videos"] / "ride.mp4").exists()
    assert sorted(f.name for f in (prefix / "drive_c/users/rider/Pictures/Zwift").iterdir()) == ["old.jpg", "old_clean.jpg"]


def test_trash_counts_only_what_the_portal_took(prefix):
    media.set_mode("trash")
    taken = []
    def trash(path):
        if path.suffix == ".mp4":
            return False  # portal refused: the file stays
        taken.append(path.name)
        path.unlink()
        return True
    assert media.after_ride(time.time() - 60, prefix, trash=trash) == {"pictures": 2, "videos": 0}
    assert sorted(taken) == ["ride.jpg", "ride_clean.jpg"]
    assert (prefix / "drive_c/users/rider/Videos/Zwift/ride.mp4").exists()


def test_xdg_dir_from_user_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    f = tmp_path / "user-dirs.dirs"
    f.write_text('# comment\nXDG_PICTURES_DIR="$HOME/Bilder"\nXDG_VIDEOS_DIR="$HOME"\n')
    assert media.xdg_dir("pictures", [f]) == tmp_path / "Bilder"
    assert media.xdg_dir("videos", [f]) == tmp_path / "Videos"  # $HOME = disabled, fall back


def test_unknown_mode_is_ignored(prefix):
    media.set_mode("burn")
    assert media.mode() == "keep"


def test_trash_by_spec(tmp_path):
    trash = tmp_path / "Trash"
    for content in ("first", "second"):
        f = tmp_path / "ride clip.mp4"
        f.write_text(content)
        assert media.trash_by_spec(f, trash)
        assert not f.exists()
    assert sorted(p.name for p in (trash / "files").iterdir()) == ["ride clip.1.mp4", "ride clip.mp4"]
    info = (trash / "info" / "ride clip.mp4.trashinfo").read_text()
    assert info.startswith("[Trash Info]\nPath=") and "ride%20clip.mp4" in info and "DeletionDate=" in info
