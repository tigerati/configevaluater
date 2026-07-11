"""Allow python -m configevaluater to run the tool."""

from configevaluater.cli import main


if __name__ == "__main__":
    raise SystemExit(main())