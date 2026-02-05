"""Входната точка за CLI.
Тук са parse_args(), main() и настройка за UTF-8 изход.
"""
from __future__ import annotations

import argparse
import io
import sys

from cpuinfo_app.formatters import format_json, format_table
from cpuinfo_app.providers import get_cpu_info, get_system_info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Показва информация за CPU и системата.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Извежда резултата като чист JSON обект.",
    )
    parser.add_argument(
        "--full",
        "--verbose",
        action="store_true",
        dest="full",
        help="Детайлен режим с всички налични атрибути.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Изключва оцветяването на изхода.",
    )
    wait_group = parser.add_mutually_exclusive_group()
    wait_group.add_argument(
        "--wait-exit",
        action="store_true",
        help="Изчаква клавиш преди изход (удобно при стартиране с двоен клик).",
    )
    wait_group.add_argument(
        "--no-wait-exit",
        action="store_true",
        help="Прескача автоматичното изчакване преди изход.",
    )
    return parser.parse_args()


def main() -> int:
    _ensure_utf8_stdout()
    args = parse_args()

    data = {
        "cpu": get_cpu_info(),
        "system": get_system_info(),
    }

    use_color = sys.stdout.isatty() and not args.no_color and not args.json

    if args.json:
        print(format_json(data))
    else:
        print(format_table(data, verbose=args.full, use_color=use_color))

    if _should_wait_before_exit(args):
        _wait_before_exit()

    return 0


def _should_wait_before_exit(args: argparse.Namespace) -> bool:
    if args.no_wait_exit:
        return False
    if args.wait_exit:
        return True
    return (
        sys.platform == "win32"
        and getattr(sys, "frozen", False)
        and len(sys.argv) == 1
        and sys.stdout.isatty()
    )


def _wait_before_exit() -> None:
    try:
        if sys.platform == "win32":
            import msvcrt

            print("\nPress any key to exit...", file=sys.stderr, end="", flush=True)
            msvcrt.getch()
            print(file=sys.stderr)
            return

        input("\nPress Enter to exit...")
    except (EOFError, KeyboardInterrupt):
        return


def _ensure_utf8_stdout() -> None:
    """Опит за UTF-8 на stdout, иначе се използва ASCII-safe вариант."""
    stdout = sys.stdout
    try:
        if hasattr(stdout, "reconfigure"):
            stdout.reconfigure(encoding="utf-8", errors="replace")
            return
    except Exception:
        pass

    try:
        buffer = stdout.buffer
    except Exception:
        return

    sys.stdout = io.TextIOWrapper(buffer, encoding="ascii", errors="backslashreplace", line_buffering=True)


if __name__ == "__main__":
    raise SystemExit(main())
