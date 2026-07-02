"""Comment text normalization and validation."""


def normalize_comment_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Comment text cannot be empty")
    return cleaned
