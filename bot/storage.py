"""Хранение file_id кружка (video note) в JSON-файле."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)


class NoteStorage:
    """Потокобезопасное хранилище одного кружка."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = Lock()
        self._file_id: str | None = None
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.exception("Не удалось прочитать %s, кружок будет сброшен", self._path)
            return
        file_id = payload.get("file_id")
        if isinstance(file_id, str) and file_id:
            self._file_id = file_id

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"file_id": self._file_id}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(self._path)

    @property
    def file_id(self) -> str | None:
        return self._file_id

    def set(self, file_id: str) -> None:
        """Сохранить новый file_id."""
        with self._lock:
            self._file_id = file_id
            self._save()

    def clear(self) -> None:
        """Забыть сохранённый кружок."""
        with self._lock:
            self._file_id = None
            if self._path.exists():
                self._path.unlink()


class Cooldown:
    """Антиспам: не отвечать в одном чате чаще, чем раз в N секунд."""

    def __init__(self, seconds: int) -> None:
        self._seconds = seconds
        self._last: dict[int, float] = {}

    def ready(self, key: int, now: float) -> bool:
        if self._seconds <= 0:
            return True
        last = self._last.get(key)
        if last is not None and now - last < self._seconds:
            return False
        self._last[key] = now
        return True
