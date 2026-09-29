"""Чистая логика определения «почему»-вопроса (удобно тестировать)."""

from __future__ import annotations

import re


def build_pattern(word: str) -> re.Pattern[str]:
    """Скомпилировать паттерн «слово целиком, без учёта регистра»."""
    escaped = re.escape(word.strip())
    return re.compile(rf"(?<![\w-]){escaped}(?![\w-])", re.IGNORECASE)


def is_trigger(
    text: str | None,
    word: str = "почему",
    require_question_mark: bool = False,
) -> bool:
    """True, если сообщение содержит слово-триггер.

    Проверяется целое слово, поэтому «непочему» или «почемуЖе» не считаются.
    """
    if not text:
        return False
    normalized = text.strip()
    if not normalized:
        return False
    if not build_pattern(word).search(normalized):
        return False
    if require_question_mark and "?" not in normalized:
        return False
    return True
