"""Команды админа: установка и статус кружка, служебные сообщения."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import Settings
from bot.storage import NoteStorage

logger = logging.getLogger(__name__)

router = Router(name="note")


def _is_admin(message: Message, settings: Settings) -> bool:
    """Пустой ADMIN_IDS = установить кружок может любой в личке с ботом."""
    if not settings.admin_ids:
        return True
    if message.from_user and message.from_user.id in settings.admin_ids:
        return True
    return False


async def _save_from_message(message: Message, storage: NoteStorage) -> bool:
    note = message.video_note
    if not note:
        return False
    storage.set(note.file_id)
    logger.info("Кружок сохранён: file_id=%s", note.file_id)
    return True


@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я отвечаю кружком на слово «почему» в группе.\n\n"
        "Как задать кружок:\n"
        "1. Перешлите его мне в личку — я запомню.\n"
        "2. Или ответьте на кружок командой /setnote в чате с ботом.\n\n"
        "Команды: /setnote, /note_status, /help"
    )


@router.message(Command("help"), F.chat.type == ChatType.PRIVATE)
async def cmd_help(message: Message) -> None:
    await message.answer(
        "/setnote — ответьте этой командой на кружок, чтобы бот запомнил его\n"
        "/note_status — показать, задан ли кружок\n"
        "Пересланный в личку кружок тоже сохраняется автоматически"
    )


@router.message(Command("setnote"), F.chat.type == ChatType.PRIVATE)
async def cmd_setnote_reply(message: Message, storage: NoteStorage, settings: Settings) -> None:
    """Сохранить кружок, на который ответили командой."""
    if not _is_admin(message, settings):
        return
    replied = message.reply_to_message
    if replied and await _save_from_message(replied, storage):
        await message.answer("Кружок сохранён.")
        return
    if await _save_from_message(message, storage):
        await message.answer("Кружок сохранён.")
        return
    await message.answer(
        "Перешлите кружок (video note) мне в личку или ответьте командой /setnote на кружок."
    )


@router.message(Command("setnote"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_setnote_group(message: Message, storage: NoteStorage, settings: Settings) -> None:
    if not _is_admin(message, settings):
        return
    replied = message.reply_to_message
    if replied and replied.video_note:
        storage.set(replied.video_note.file_id)
        await message.reply("Кружок сохранён.")
        return
    await message.reply("Ответьте этой командой на кружок, чтобы я его запомнил.")


@router.message(F.chat.type == ChatType.PRIVATE, F.video_note)
async def on_forwarded_note(message: Message, storage: NoteStorage, settings: Settings) -> None:
    """Пересланный/отправленный кружок в личку — сохраняем."""
    if not _is_admin(message, settings):
        return
    if await _save_from_message(message, storage):
        await message.answer("Кружок сохранён, буду отвечать им на «почему».")


@router.message(Command("note_status"), F.chat.type == ChatType.PRIVATE)
async def cmd_note_status(message: Message, storage: NoteStorage) -> None:
    file_id = storage.file_id
    if file_id:
        await message.answer(f"Кружок задан.\nfile_id: <code>{file_id}</code>")
    else:
        await message.answer("Кружок не задан — бот ответит файлом из media/, если он есть.")
