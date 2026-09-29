"""Конфигурация бота: читается из переменных окружения / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Переменная {name} должна быть числом, получено: {raw!r}") from exc


def _ids_env(name: str) -> frozenset[int]:
    raw = os.getenv(name, "")
    ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError as exc:
            raise ValueError(
                f"Переменная {name} должна содержать числа, получено: {part!r}"
            ) from exc
    return frozenset(ids)


@dataclass(frozen=True)
class Settings:
    """Настройки приложения."""

    bot_token: str
    trigger_word: str = "почему"
    require_question_mark: bool = False
    cooldown_seconds: int = 30
    allowed_chat_ids: frozenset[int] = field(default_factory=frozenset)
    admin_ids: frozenset[int] = field(default_factory=frozenset)
    work_only_in_groups: bool = True
    data_dir: Path = BASE_DIR / "data"
    media_dir: Path = BASE_DIR / "media"
    log_level: str = "INFO"

    @property
    def note_file(self) -> Path:
        return self.data_dir / "note.json"

    @property
    def fallback_note_path(self) -> Path:
        return self.media_dir / "video_note.mp4"


def load_settings() -> Settings:
    """Собрать настройки из окружения."""
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "BOT_TOKEN не задан. Скопируйте .env.example в .env и заполните BOT_TOKEN."
        )

    return Settings(
        bot_token=token,
        trigger_word=os.getenv("TRIGGER_WORD", "почему").strip().lower() or "почему",
        require_question_mark=_int_env("REQUIRE_QUESTION_MARK", 0) == 1,
        cooldown_seconds=max(_int_env("COOLDOWN_SECONDS", 30), 0),
        allowed_chat_ids=_ids_env("ALLOWED_CHAT_IDS"),
        admin_ids=_ids_env("ADMIN_IDS"),
        work_only_in_groups=os.getenv("WORK_ONLY_IN_GROUPS", "1").strip() != "0",
        data_dir=Path(os.getenv("DATA_DIR", str(BASE_DIR / "data"))),
        media_dir=Path(os.getenv("MEDIA_DIR", str(BASE_DIR / "media"))),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
