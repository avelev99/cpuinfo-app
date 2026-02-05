"""Този файл съдържа логиката за форматиране.
Има format_json() за JSON и format_table() за табличен CLI изход,
а останалото са помощни функции за редове, проценти и кеш.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple
import json
import textwrap

from .utils import UNKNOWN


def format_json(data: Dict[str, Any]) -> str:
    """JSON за хора и скриптове, с нормално отстояние."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_table(data: Dict[str, Any], verbose: bool = False, use_color: bool = True) -> str:
    """Табличен изход за конзолата, кратък или подробен според verbose."""
    cpu = data.get("cpu", {})
    system = data.get("system", {})

    cpu_rows = _build_cpu_rows(cpu, verbose)
    system_rows = _build_system_rows(system, verbose)

    sections = [
        _format_section("CPU", cpu_rows, use_color),
        _format_section("СИСТЕМА", system_rows, use_color),
    ]
    return "\n\n".join(sections)


def _build_cpu_rows(cpu: Dict[str, Any], verbose: bool) -> List[Tuple[str, str]]:
    freq = cpu.get("frequency_mhz", {})
    rows = [
        ("Модел/Бранд", _value(cpu.get("brand"))),
        ("Архитектура", _value(cpu.get("architecture"))),
        ("Физически ядра", _value(cpu.get("physical_cores"))),
        ("Логически нишки", _value(cpu.get("logical_processors"))),
        ("Честота (MHz)", _format_freq_summary(freq)),
        ("Натоварване", _format_percent(cpu.get("usage_percent"))),
    ]

    if verbose:
        rows.extend(
            [
                ("Честота мин (MHz)", _value(freq.get("min"))),
                ("Честота макс (MHz)", _value(freq.get("max"))),
                ("Функции/Флагове", _format_list(cpu.get("features"), verbose=True)),
                ("CPU Cache", _format_cache(cpu.get("cache"))),
            ]
        )
    return rows


def _build_system_rows(system: Dict[str, Any], verbose: bool) -> List[Tuple[str, str]]:
    os_info = system.get("os", {})
    memory = system.get("memory", {})

    os_label = f"{os_info.get('name', UNKNOWN)} {os_info.get('release', UNKNOWN)}"
    os_version = os_info.get("version", UNKNOWN)

    rows = [
        ("ОС", _value(os_label)),
        ("OS версия", _value(os_version)),
        ("Hostname", _value(system.get("hostname"))),
        ("Uptime", _value(system.get("uptime_human"))),
        ("RAM общо", _value(memory.get("total_human"))),
        ("RAM свободно", _value(memory.get("available_human"))),
    ]

    if verbose:
        rows.extend(
            [
                ("Uptime (сек)", _value(system.get("uptime_seconds"))),
                ("RAM общо (байтове)", _value(memory.get("total_bytes"))),
                ("RAM свободно (байтове)", _value(memory.get("available_bytes"))),
            ]
        )
    return rows


def _format_section(title: str, rows: List[Tuple[str, str]], use_color: bool) -> str:
    table = _format_table(rows)
    header = _color(title, "1;36") if use_color else title
    return f"{header}\n{table}"


def _format_table(rows: List[Tuple[str, str]]) -> str:
    label_header = "Параметър"
    value_header = "Стойност"

    normalized_rows = [(label, _value(value)) for label, value in rows]
    max_label = max(len(label_header), *(len(label) for label, _ in normalized_rows))

    max_value = max(len(value_header), *(len(value) for _, value in normalized_rows))
    max_value = min(max_value, 70)

    border = f"+{'-' * (max_label + 2)}+{'-' * (max_value + 2)}+"
    header = f"| {label_header.ljust(max_label)} | {value_header.ljust(max_value)} |"

    lines = [border, header, border]
    for label, value in normalized_rows:
        wrapped = textwrap.wrap(value, width=max_value) or [""]
        for idx, chunk in enumerate(wrapped):
            label_text = label if idx == 0 else ""
            line = f"| {label_text.ljust(max_label)} | {chunk.ljust(max_value)} |"
            lines.append(line)
    lines.append(border)
    return "\n".join(lines)


def _format_freq_summary(freq: Any) -> str:
    if not isinstance(freq, dict):
        return _value(freq)

    current = _value(freq.get("current"))
    min_value = _value(freq.get("min"))
    max_value = _value(freq.get("max"))

    if min_value == UNKNOWN and max_value == UNKNOWN:
        return current
    return f"{current} (мин: {min_value}, макс: {max_value})"


def _format_percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.1f}%"
    return _value(value)


def _format_list(value: Any, verbose: bool) -> str:
    if not isinstance(value, list):
        return _value(value)

    if verbose:
        return ", ".join(value) if value else UNKNOWN

    limit = 10
    if len(value) <= limit:
        return ", ".join(value)
    remaining = len(value) - limit
    return f"{', '.join(value[:limit])} ... (+{remaining})"


def _format_cache(cache: Any) -> str:
    if not isinstance(cache, dict):
        return _value(cache)

    parts = []
    for level in ["L1", "L2", "L3"]:
        parts.append(f"{level}: {cache.get(level, UNKNOWN)}")
    return ", ".join(parts)


def _value(value: Any) -> str:
    if value is None:
        return UNKNOWN
    if isinstance(value, bool):
        return "Да" if value else "Не"
    return str(value)


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"
