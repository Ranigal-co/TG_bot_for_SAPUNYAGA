import asyncio

from bot.config import Settings
from bot.main import build_dispatcher


def test_dispatcher_wired(tmp_path) -> None:
    settings = Settings(
        bot_token="123456789:AAFakeTokenForTests",
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
        cooldown_seconds=0,
    )

    async def scenario() -> None:
        bot, dp = build_dispatcher(settings)
        try:
            assert dp["settings"] is settings
            assert dp["storage"].file_id is None
            assert {r.name for r in dp.sub_routers} == {"note", "why"}
        finally:
            await bot.session.close()

    asyncio.run(scenario())
