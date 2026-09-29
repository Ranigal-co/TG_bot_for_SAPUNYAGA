from pathlib import Path

import pytest
from bot.config import Settings, _ids_env, _int_env


def test_int_env_default(monkeypatch) -> None:
    monkeypatch.delenv("COOLDOWN_SECONDS", raising=False)
    assert _int_env("COOLDOWN_SECONDS", 30) == 30


def test_int_env_invalid(monkeypatch) -> None:
    monkeypatch.setenv("COOLDOWN_SECONDS", "abc")
    with pytest.raises(ValueError, match="COOLDOWN_SECONDS"):
        _int_env("COOLDOWN_SECONDS", 30)


def test_ids_env(monkeypatch) -> None:
    monkeypatch.setenv("ALLOWED_CHAT_IDS", "-1001, -1002;-1003")
    assert _ids_env("ALLOWED_CHAT_IDS") == frozenset({-1001, -1002, -1003})


def test_ids_env_empty(monkeypatch) -> None:
    monkeypatch.delenv("ALLOWED_CHAT_IDS", raising=False)
    assert _ids_env("ALLOWED_CHAT_IDS") == frozenset()


def test_settings_helpers(tmp_path: Path) -> None:
    settings = Settings(
        bot_token="123:abc",
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
    )
    assert settings.note_file == tmp_path / "data" / "note.json"
    assert settings.fallback_note_path == tmp_path / "media" / "video_note.mp4"


def test_load_settings_requires_token(monkeypatch) -> None:
    from bot.config import load_settings

    monkeypatch.delenv("BOT_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="BOT_TOKEN"):
        load_settings()


def test_load_settings_ok(monkeypatch) -> None:
    from bot.config import load_settings

    monkeypatch.setenv("BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TRIGGER_WORD", "Почему")
    monkeypatch.setenv("COOLDOWN_SECONDS", "5")

    settings = load_settings()
    assert settings.bot_token == "123:abc"
    assert settings.trigger_word == "почему"
    assert settings.cooldown_seconds == 5
