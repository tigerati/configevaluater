"""Small, deliberately conservative parser for .env files."""

import re
from pathlib import Path

from src.configevaluater.models import Setting

KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class EnvParseError(ValueError):
    """Raised when an input file contains unsupported .env syntax."""

    def __init__(self, line: int, message: str) -> None:
        self.line = line
        self.message = message
        super().__init__(f"line {line}: {message}")


def parse_env_text(text: str) -> list[Setting]:
    """Parse supported .env syntax while retaining order and duplicates."""
    settings: list[Setting] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise EnvParseError(line_number, "expected KEY=value")

        raw_key, raw_value = line.split("=", 1)
        key = raw_key.strip()
        value = raw_value.strip()

        if not KEY_PATTERN.fullmatch(key):
            raise EnvParseError(line_number, f"invalid key {key!r}")

        value = _remove_matching_quotes(value, line_number)
        settings.append(Setting(key=key, value=value, line=line_number))

    return settings


def parse_env_file(path: Path) -> list[Setting]:
    """Read and parse a UTF-8 .env file."""
    return parse_env_text(path.read_text(encoding="utf-8"))


def _remove_matching_quotes(value: str, line: int) -> str:
    if not value:
        return value

    starts_quoted = value[0] in {'"', "'"}
    ends_quoted = value[-1] in {'"', "'"}

    if starts_quoted or ends_quoted:
        if len(value) < 2 or value[0] != value[-1]:
            raise EnvParseError(line, "unmatched quote in value")
        return value[1:-1]

    return value

