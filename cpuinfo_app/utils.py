"""Малки помощни функции.
safe_call() е за безопасни извиквания, format_bytes() и format_duration()
дават четим текст за памет и време.
"""
from __future__ import annotations

from typing import Any, Callable

UNKNOWN = "N/A"


def safe_call(func: Callable[[], Any], default: Any = UNKNOWN) -> Any:
    """Изпълнява функцията и при грешка връща default."""
    try:
        return func()
    except Exception:
        return default


def format_bytes(num_bytes: Any) -> str:
    """Байтове -> човешки формат (KB/MB/GB/TB)."""
    if not isinstance(num_bytes, (int, float)) or num_bytes < 0:
        return UNKNOWN

    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def format_duration(seconds: Any) -> str:
    """Секунди -> hh:mm:ss, с дни когато има."""
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return UNKNOWN

    total = int(seconds)
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    if days > 0:
        return f"{days}д {hours:02}:{minutes:02}:{secs:02}"
    return f"{hours:02}:{minutes:02}:{secs:02}"
