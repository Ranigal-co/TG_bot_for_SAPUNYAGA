import pytest
from bot.triggers import is_trigger


@pytest.mark.parametrize(
    "text",
    [
        "почему",
        "Почему так?",
        "А почему бы и нет",
        "почему\tи ещё текст",
        "ПОЧЕМУ!!!",
        "почему?",
        "слово почему внутри предложения",
    ],
)
def test_trigger_detected(text: str) -> None:
    assert is_trigger(text) is True


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        "   ",
        "непочему",
        "почемуже",
        "Почему-то",
        "обычное сообщение",
        "за?",
    ],
)
def test_not_trigger(text: str | None) -> None:
    assert is_trigger(text) is False


def test_require_question_mark() -> None:
    assert is_trigger("почему", require_question_mark=True) is False
    assert is_trigger("почему так?", require_question_mark=True) is True


def test_custom_word() -> None:
    assert is_trigger("зачем ты это сделал", word="зачем") is True
    assert is_trigger("почему", word="зачем") is False


def test_pattern_reused_without_recompiling_error() -> None:
    assert is_trigger("Почему") is True
    assert is_trigger("почему") is True
