"""Отправка кружка в ответ на «почему»."""

from __future__ import annotations

import logging
import time

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, Message

from bot.config import Settings
from bot.storage import Cooldown, NoteStorage
from bot.triggers import is_trigger

logger = logging.getLogger(__name__)

router = Router(name="why")


def _scope_ok(message: Message, settings: Settings) -> bool:
    chat = message.chat
    if settings.work_only_in_groups and chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return False
    if settings.allowed_chat_ids and chat.id not in settings.allowed_chat_ids:
        return False
    return True


async def _resolve_file_id(
    message: Message, settings: Settings, storage: NoteStorage
) -> str | None:
    """Вернуть рабочий file_id: из хранилища, иначе залить файл из media/."""
    file_id = storage.file_id
    if file_id:
        return file_id

    fallback = settings.fallback_note_path
    if not fallback.is_file():
        logger.warning("Кружок не задан: нет ни file_id, ни файла %s", fallback)
        return None

    sent = await message.answer_video_note(video_note=FSInputFile(fallback))
    if sent.video_note:
        storage.set(sent.video_note.file_id)
        logger.info("Кружок залит из %s, file_id сохранён", fallback)
        return sent.video_note.file_id
    return None


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def on_message(
    message: Message, settings: Settings, storage: NoteStorage, cooldown: Cooldown
) -> None:
    """Ответить кружком на сообщение со словом «почему»."""
    if not _scope_ok(message, settings):
        return
    if not is_trigger(message.text, settings.trigger_word, settings.require_question_mark):
        return
    if not cooldown.ready(message.chat.id, time.monotonic()):
        return

    try:
        file_id = await _resolve_file_id(message, settings, storage)
        if not file_id:
            await message.reply(
                "Кружок пока не задан. Админ может переслать его боту "
                "или ответить им на команду /setnote"
            )
            return
        await message.reply_video_note(video_note=file_id)
    except TelegramBadRequest as exc:
        logger.warning("Не удалось отправить кружок (%s), пробуем залить заново", exc)
        storage.clear()
        new_file_id = await _resolve_file_id(message, settings, storage)
        if new_file_id:
            await message.reply_video_note(video_note=new_file_id)
