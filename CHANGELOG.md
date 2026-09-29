# Changelog

Формат ведётся по [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версионирование — [Semantic Versioning](https://semver.org/lang/ru/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-09-29

### Added

- Бот отвечает кружком (video note) на целое слово «почему» в группах.
- Сохранение кружка тремя способами: пересылка в личку, `/setnote` в ответ на
  кружок, файл `media/video_note.mp4` как запасной вариант.
- Антиспам-кулдаун на чат (`COOLDOWN_SECONDS`).
- Фильтры: `TRIGGER_WORD`, `REQUIRE_QUESTION_MARK`, `ALLOWED_CHAT_IDS`,
  `WORK_ONLY_IN_GROUPS`, `ADMIN_IDS`.
- Автовосстановление: при невалидном `file_id` бот забывает его и заливает
  кружок заново из `media/`.
- Тесты (pytest) и линт (ruff), CI в GitHub Actions.
- Docker-образ и docker-compose.
- README, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, шаблоны issue/PR.
