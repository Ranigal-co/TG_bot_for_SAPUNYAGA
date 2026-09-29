"""Точка входа: настройка логирования, DI и запуск polling."""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings, load_settings
from bot.handlers import note, why
from bot.storage import Cooldown, NoteStorage

logger = logging.getLogger(__name__)


def build_dispatcher(settings: Settings) -> tuple[Bot, Dispatcher]:
    """Собрать бота и диспетчер (выделено для тестов)."""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp["settings"] = settings
    dp["storage"] = NoteStorage(settings.note_file)
    dp["cooldown"] = Cooldown(settings.cooldown_seconds)

    dp.include_router(note.router)
    dp.include_router(why.router)
    return bot, dp


async def run(settings: Settings | None = None) -> None:
    settings = settings or load_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    bot, dp = build_dispatcher(settings)
    me = await bot.get_me()
    logger.info("Бот запущен: @%s (триггер %r)", me.username, settings.trigger_word)
    if not settings.admin_ids:
        logger.warning("ADMIN_IDS пуст — установить кружок сможет любой в личке с ботом")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def main() -> None:
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановлено")


if __name__ == "__main__":
    main()
