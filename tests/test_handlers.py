import asyncio
from pathlib import Path
from unittest.mock import AsyncMock

from bot.config import Settings
from bot.handlers.why import on_message
from bot.storage import Cooldown, NoteStorage


def make_settings(**kwargs) -> Settings:
    return Settings(bot_token="123456789:AAFakeTokenForTests", **kwargs)


def make_message(text: str, chat_type: str = "supergroup", chat_id: int = -100):
    message = AsyncMock()
    message.text = text
    message.chat.type = chat_type
    message.chat.id = chat_id
    return message


def test_ignores_non_trigger(tmp_path: Path) -> None:
    settings = make_settings(data_dir=tmp_path, media_dir=tmp_path)
    storage = NoteStorage(tmp_path / "note.json")
    message = make_message("обычное сообщение")

    asyncio.run(on_message(message, settings, storage, Cooldown(0)))

    message.reply_video_note.assert_not_awaited()


def test_ignores_private_chat(tmp_path: Path) -> None:
    settings = make_settings(data_dir=tmp_path, media_dir=tmp_path)
    storage = NoteStorage(tmp_path / "note.json")
    message = make_message("почему", chat_type="private")

    asyncio.run(on_message(message, settings, storage, Cooldown(0)))

    message.reply_video_note.assert_not_awaited()


def test_answers_with_stored_note(tmp_path: Path) -> None:
    settings = make_settings(data_dir=tmp_path, media_dir=tmp_path)
    storage = NoteStorage(tmp_path / "note.json")
    storage.set("file-id-42")
    message = make_message("Почему так происходит?")

    asyncio.run(on_message(message, settings, storage, Cooldown(0)))

    message.reply_video_note.assert_awaited_once_with(video_note="file-id-42")


def test_asks_to_set_note_when_missing(tmp_path: Path) -> None:
    settings = make_settings(data_dir=tmp_path, media_dir=tmp_path / "empty-media")
    storage = NoteStorage(tmp_path / "note.json")
    message = make_message("почему")

    asyncio.run(on_message(message, settings, storage, Cooldown(0)))

    message.reply_video_note.assert_not_awaited()
    assert "Кружок пока не задан" in message.reply.call_args.args[0]


def test_cooldown_blocks_second_answer(tmp_path: Path) -> None:
    settings = make_settings(data_dir=tmp_path, media_dir=tmp_path)
    storage = NoteStorage(tmp_path / "note.json")
    storage.set("file-id-42")
    cooldown = Cooldown(60)

    first = make_message("почему")
    second = make_message("почему снова")

    asyncio.run(on_message(first, settings, storage, cooldown))
    asyncio.run(on_message(second, settings, storage, cooldown))

    first.reply_video_note.assert_awaited_once()
    second.reply_video_note.assert_not_awaited()


def test_allowed_chat_filter(tmp_path: Path) -> None:
    settings = make_settings(
        data_dir=tmp_path,
        media_dir=tmp_path,
        allowed_chat_ids=frozenset({-123}),
    )
    storage = NoteStorage(tmp_path / "note.json")
    storage.set("file-id-42")
    message = make_message("почему", chat_id=-456)

    asyncio.run(on_message(message, settings, storage, Cooldown(0)))

    message.reply_video_note.assert_not_awaited()
