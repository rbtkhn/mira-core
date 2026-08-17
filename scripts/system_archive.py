"""Compatibility wrapper for the former System Archive Python entry point."""

from archive import *  # noqa: F401,F403
from archive import main as _archive_main


def main(arguments: list[str] | None = None) -> int:
    return _archive_main(arguments)


if __name__ == "__main__":
    import sys

    print("system-archive is deprecated; use archive", file=sys.stderr)
    raise SystemExit(main())
