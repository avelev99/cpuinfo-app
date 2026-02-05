"""Тук са функциите за събиране на данни.
get_cpu_info() и get_system_info() са основните, а _cpu_* са вътрешните помощни функции.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import platform
import re
import socket
import time

import psutil

from .utils import UNKNOWN, format_bytes, format_duration, safe_call

CPUINFO_PATH = Path("/proc/cpuinfo")
CACHE_DIR = Path("/sys/devices/system/cpu/cpu0/cache")
GENERIC_CPU_NAMES = {"x86_64", "amd64", "arm64", "aarch64", "i386", "i686"}


def get_cpu_info() -> Dict[str, Any]:
    """Събира CPU данни от psutil и (ако има) от системни файлове."""
    return {
        "brand": _cpu_brand(),
        "architecture": _cpu_architecture(),
        "physical_cores": _cpu_count(logical=False),
        "logical_processors": _cpu_count(logical=True),
        "frequency_mhz": _cpu_frequency(),
        "usage_percent": _cpu_usage(),
        "features": _cpu_features(),
        "cache": _cpu_cache_sizes(),
    }


def get_system_info() -> Dict[str, Any]:
    """Събира OS, hostname, uptime и RAM в един речник."""
    uname = platform.uname()

    os_name = uname.system or platform.system() or UNKNOWN
    os_release = uname.release or platform.release() or UNKNOWN
    os_version = uname.version or platform.version() or UNKNOWN
    hostname = safe_call(socket.gethostname, UNKNOWN)

    boot_time = safe_call(psutil.boot_time, None)
    uptime_seconds: Any
    uptime_human: Any
    if isinstance(boot_time, (int, float)):
        uptime_seconds = max(0, int(time.time() - boot_time))
        uptime_human = format_duration(uptime_seconds)
    else:
        uptime_seconds = UNKNOWN
        uptime_human = UNKNOWN

    mem_info = safe_call(psutil.virtual_memory, None)
    if mem_info and hasattr(mem_info, "total"):
        total_bytes = mem_info.total
        available_bytes = mem_info.available
        total_human = format_bytes(total_bytes)
        available_human = format_bytes(available_bytes)
    else:
        total_bytes = UNKNOWN
        available_bytes = UNKNOWN
        total_human = UNKNOWN
        available_human = UNKNOWN

    return {
        "os": {
            "name": os_name,
            "release": os_release,
            "version": os_version,
        },
        "hostname": hostname,
        "uptime_seconds": uptime_seconds,
        "uptime_human": uptime_human,
        "memory": {
            "total_bytes": total_bytes,
            "available_bytes": available_bytes,
            "total_human": total_human,
            "available_human": available_human,
        },
    }


def _cpu_brand() -> str:
    try:
        name = platform.processor() or platform.uname().processor
    except Exception:
        name = ""

    if name:
        normalized = name.strip().lower()
        if normalized not in GENERIC_CPU_NAMES:
            return name

    if CPUINFO_PATH.exists():
        try:
            content = CPUINFO_PATH.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"^model name\s*:\s*(.+)$", content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        except Exception:
            return UNKNOWN

    return UNKNOWN


def _cpu_architecture() -> str:
    return safe_call(lambda: platform.machine() or UNKNOWN, UNKNOWN)


def _cpu_count(logical: bool) -> Any:
    value = safe_call(lambda: psutil.cpu_count(logical=logical), None)
    if isinstance(value, int):
        return value
    return UNKNOWN


def _cpu_frequency() -> Dict[str, Any]:
    freq = safe_call(psutil.cpu_freq, None)
    if not freq:
        return {"current": UNKNOWN, "min": UNKNOWN, "max": UNKNOWN}
    return {
        "current": round(freq.current, 2) if freq.current is not None else UNKNOWN,
        "min": round(freq.min, 2) if freq.min is not None else UNKNOWN,
        "max": round(freq.max, 2) if freq.max is not None else UNKNOWN,
    }


def _cpu_usage() -> Any:
    value = safe_call(lambda: psutil.cpu_percent(interval=0.1), None)
    if isinstance(value, (int, float)):
        return round(value, 1)
    return UNKNOWN


def _cpu_features() -> Any:
    if not CPUINFO_PATH.exists():
        return UNKNOWN

    try:
        content = CPUINFO_PATH.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return UNKNOWN

    match = re.search(r"^flags\s*:\s*(.+)$", content, re.MULTILINE)
    if not match:
        match = re.search(r"^Features\s*:\s*(.+)$", content, re.MULTILINE)
    if not match:
        return UNKNOWN

    features = [item.strip() for item in match.group(1).split() if item.strip()]
    return features if features else UNKNOWN


def _cpu_cache_sizes() -> Dict[str, Any]:
    if not CACHE_DIR.exists():
        return {"L1": UNKNOWN, "L2": UNKNOWN, "L3": UNKNOWN}

    best_sizes: Dict[str, int] = {}
    best_labels: Dict[str, str] = {}

    for idx in CACHE_DIR.glob("index*"):
        level_path = idx / "level"
        size_path = idx / "size"
        if not level_path.exists() or not size_path.exists():
            continue
        try:
            level = level_path.read_text().strip()
            size_text = size_path.read_text().strip()
        except Exception:
            continue

        level_key = f"L{level}"
        size_bytes = _parse_cache_size(size_text)
        if size_bytes is None:
            continue
        if level_key not in best_sizes or size_bytes > best_sizes[level_key]:
            best_sizes[level_key] = size_bytes
            best_labels[level_key] = size_text

    return {
        "L1": best_labels.get("L1", UNKNOWN),
        "L2": best_labels.get("L2", UNKNOWN),
        "L3": best_labels.get("L3", UNKNOWN),
    }


def _parse_cache_size(text: str) -> Optional[int]:
    match = re.match(r"^(\d+(?:\.\d+)?)([KMG])$", text.strip(), re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).upper()
    multiplier = {"K": 1024, "M": 1024**2, "G": 1024**3}.get(unit, 1)
    return int(value * multiplier)
