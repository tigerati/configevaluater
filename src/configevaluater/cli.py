"""Command-line interface for ConfigEvaluater."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from configevaluater import __version__
from configevaluater.parser import EnvParseError, parse_env_file
from configevaluater.reporter import render_json, render_text
from configevaluater.rules import SEVERITY_ORDER, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="configevaluater",
        description="Scan a .env file for common insecure settings.",
    )
    parser.add_argument("file", type=Path, help="path to the .env file to scan")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format (default: text)")
    parser.add_argument("--severity", choices=("low", "medium", "high"), default="low", help="minimum severity to display")
    parser.add_argument("--fail-on", choices=("low", "medium", "high"), help="return exit code 1 when this severity or higher is found")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if not args.file.exists():
            raise OSError("file does not exist")
        if not args.file.is_file():
            raise OSError("path is not a regular file")
        settings = parse_env_file(args.file)
    except EnvParseError as error:
        print(f"configevaluater: invalid input: {error}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as error:
        print(f"configevaluater: cannot read {args.file}: {error}", file=sys.stderr)
        return 2

    all_findings = scan(settings)
    minimum = SEVERITY_ORDER[args.severity]
    displayed = [item for item in all_findings if SEVERITY_ORDER[item.severity] >= minimum]
    output = render_json(args.file, displayed) if args.format == "json" else render_text(args.file, displayed)
    print(output)

    if args.fail_on:
        threshold = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER[item.severity] >= threshold for item in all_findings):
            return 1
    return 0
