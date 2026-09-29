import json
from pathlib import Path

from bot.storage import Cooldown, NoteStorage


def test_empty_storage(tmp_path: Path) -> None:
    storage = NoteStorage(tmp_path / "note.json")
    assert storage.file_id is None


def test_set_and_reload(tmp_path: Path) -> None:
    path = tmp_path / "note.json"
    NoteStorage(path).set("file-id-1")

    assert json.loads(path.read_text(encoding="utf-8")) == {"file_id": "file-id-1"}
    assert NoteStorage(path).file_id == "file-id-1"


def test_clear(tmp_path: Path) -> None:
    path = tmp_path / "note.json"
    storage = NoteStorage(path)
    storage.set("file-id-1")
    storage.clear()

    assert storage.file_id is None
    assert not path.exists()


def test_corrupted_file_is_ignored(tmp_path: Path) -> None:
    path = tmp_path / "note.json"
    path.write_text("{ broken", encoding="utf-8")
    assert NoteStorage(path).file_id is None


def test_creates_parent_dirs(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "deep" / "note.json"
    NoteStorage(path).set("file-id-1")
    assert path.exists()


def test_cooldown_allows_then_blocks() -> None:
    cooldown = Cooldown(seconds=10)
    assert cooldown.ready(1, now=100.0) is True
    assert cooldown.ready(1, now=105.0) is False
    assert cooldown.ready(1, now=111.0) is True


def test_cooldown_is_per_chat() -> None:
    cooldown = Cooldown(seconds=10)
    assert cooldown.ready(1, now=100.0) is True
    assert cooldown.ready(2, now=100.0) is True


def test_cooldown_disabled() -> None:
    cooldown = Cooldown(seconds=0)
    assert cooldown.ready(1, now=100.0) is True
    assert cooldown.ready(1, now=100.0) is True
