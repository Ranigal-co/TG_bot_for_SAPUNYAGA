# TG_bot_for_SAPUNYAGA — бот «Почему»

[![CI](https://github.com/Ranigal-co/TG_bot_for_SAPUNYAGA/actions/workflows/ci.yml/badge.svg)](https://github.com/Ranigal-co/TG_bot_for_SAPUNYAGA/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Telegram-бот для группы: на **каждое сообщение со словом «почему»** он отвечает один и тот же кружок (video note).

## Как это работает

1. Группу, куда добавлен бот, кто-нибудь спрашивает «почему …».
2. Бот находит целое слово-триггер (без учёта регистра) и отвечает кружком.
3. Антиспам-кулдаун не даёт боту спамить в одном чате подряд (`COOLDOWN_SECONDS`, по умолчанию 30 сек).

Кружок задаётся одним из трёх способов:

| Способ | Как |
| --- | --- |
| Переслать боту | Перешлите кружок боту в личку — он запомнит его |
| Ответ на команду | В личке с ботом ответьте на кружок командой `/setnote` |
| Файл в проекте | Положите `media/video_note.mp4` — бот зальёт его при первом ответе и запомнит `file_id` |

## Быстрый старт

```bash
# 1. Клонируем
git clone https://github.com/Ranigal-co/TG_bot_for_SAPUNYAGA.git
cd TG_bot_for_SAPUNYAGA

# 2. Окружение
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Конфигурация
cp .env.example .env   # вставьте BOT_TOKEN из @BotFather и ID админов

# 4. Запуск
python -m bot
```

Добавьте бота в группу и напишите там «почему».

### Запуск в Docker

```bash
cp .env.example .env   # заполните BOT_TOKEN
docker compose up --build -d
docker compose logs -f
```

## Конфигурация

| Переменная | По умолчанию | Описание |
| --- | --- | --- |
| `BOT_TOKEN` | — | **Обязательна.** Токен от [@BotFather](https://t.me/BotFather) |
| `TRIGGER_WORD` | `почему` | Слово-триггер, ищется целое слово без учёта регистра |
| `REQUIRE_QUESTION_MARK` | `0` | `1` — отвечать только на сообщения с `?` |
| `COOLDOWN_SECONDS` | `30` | Пауза между кружками в одном чате. `0` — выключить |
| `WORK_ONLY_IN_GROUPS` | `1` | `0` — отвечать и в личке |
| `ALLOWED_CHAT_IDS` | пусто | Список ID чатов через запятую. Пусто — все чаты |
| `ADMIN_IDS` | пусто | ID админов, которым можно менять кружок. Пусто — любой в личке (**не рекомендуется**) |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Команды бота

| Команда | Где | Что делает |
| --- | --- | --- |
| `/start`, `/help` | личка | Инструкция |
| `/setnote` | личка / группа | Сохранить кружок, на который ответили командой |
| `/note_status` | личка | Показать, задан ли кружок и его `file_id` |
| — | личка | Просто перешлите кружок — он сохранится |

## Структура проекта

```
.
├── bot/
│   ├── config.py            # настройки из окружения
│   ├── triggers.py          # чистая логика триггера (тестируется без Telegram)
│   ├── storage.py           # хранение file_id + антиспам-кулдаун
│   ├── main.py              # сборка диспетчера и запуск polling
│   └── handlers/
│       ├── why.py           # реакция на «почему»
│       └── note.py          # команды и сохранение кружка
├── tests/                   # pytest
├── media/                   # media/video_note.mp4 — запасной кружок
├── data/                    # data/note.json — сохранённый file_id (в .gitignore)
├── .github/workflows/ci.yml # ruff + pytest на каждый push/PR
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml           # конфиг ruff и pytest
```

## Разработка

```bash
pip install -r requirements-dev.txt
ruff check .          # линт
ruff format .         # форматирование
pytest                # тесты
```

Весь код, который не ходит в Telegram (`triggers.py`, `storage.py`, `config.py`), покрыт тестами — можно менять без запуска бота.

Перед PR ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

[MIT](LICENSE)
