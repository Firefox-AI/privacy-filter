from privacy_filter.core.classes import Span
from privacy_filter.core.masking import mask_text


def test_mask_text_replaces_spans_from_right_to_left() -> None:
    text = "Email jane@example.com or call 555-0100."
    spans = [
        Span(
            category="email",
            text="jane@example.com",
            start=6,
            end=22,
            score=0.99,
        ),
        Span(
            category="phone_number",
            text="555-0100",
            start=31,
            end=39,
            score=0.98,
        ),
    ]

    assert mask_text(text, spans) == "Email [EMAIL] or call [PHONE]."


def test_mask_text_uses_category_fallback() -> None:
    text = "Token abc123"
    spans = [
        Span(
            category="unknown",
            text="abc123",
            start=6,
            end=12,
            score=0.9,
        ),
    ]

    assert mask_text(text, spans) == "Token [UNKNOWN]"


def test_mask_text_combines_adjacent_duplicate_placeholders() -> None:
    text = "Jim Bob is a man"
    spans = [
        Span(
            category="private_person",
            text="Jim",
            start=0,
            end=3,
            score=0.9999982714653015,
        ),
        Span(
            category="private_person",
            text="Bob",
            start=3,
            end=7,
            score=0.9999939203262329,
        ),
    ]

    assert mask_text(text, spans) == "[PRIVATE_PERSON] is a man"
