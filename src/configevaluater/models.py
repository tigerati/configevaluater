"""Data objects shared by the parser, rules, and reporters."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Setting:
    """One parsed key/value setting from an environment file."""

    key: str
    value: str
    line: int


@dataclass(frozen=True)
class Finding:
    """One actionable security warning."""

    rule_id: str
    severity: str
    line: int
    key: str
    message: str
    remediation: str