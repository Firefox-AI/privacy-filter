from privacy_filter.core.classes import Span

MASK_TOKENS = {
    "account_number": "[ACCOUNT]",
    "address": "[ADDRESS]",
    "email": "[EMAIL]",
    "person": "[NAME]",
    "phone_number": "[PHONE]",
    "url": "[URL]",
    "date": "[DATE]",
    "secret": "[SECRET]",
}


def mask_text(text: str, spans: list[Span]) -> str:
    replacements: list[tuple[int, int, str]] = []
    for span in sorted(spans, key=lambda item: item.start):
        placeholder = MASK_TOKENS.get(span.category, f"[{span.category.upper()}]")
        if (
            replacements
            and span.start <= replacements[-1][1]
            and placeholder == replacements[-1][2]
        ):
            start, end, _ = replacements[-1]
            replacements[-1] = (start, max(end, span.end), placeholder)
        else:
            replacements.append((span.start, span.end, placeholder))

    # Walk right-to-left so earlier offsets stay valid as we splice.
    out = text
    for start, end, placeholder in reversed(replacements):
        out = out[:start] + placeholder + out[end:]
    return out
