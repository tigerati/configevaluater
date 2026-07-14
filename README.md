# ConfigEvaluater

ConfigEvaluater is an offline command-line security linter that scans `.env` files
for common insecure configuration choices and explains how to address them.

It is intended for students, developers, and security learners reviewing local
configuration examples. It does not connect to systems, test credentials,
modify files, or guarantee that a configuration is secure.

## Requirements

- Python 3.9 or newer

## Installation

From a fresh clone, create an isolated environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

## Quick start

```bash
configevaluater examples/insecure.env
```

During development, the tool can also run without installation:

```bash
PYTHONPATH=src python3 -m configevaluater examples/insecure.env
```

Example output:

```text
HIGH   CFG002  line 4  SECRET_KEY
       A placeholder secret value was detected.
       Recommendation: Replace it with a securely generated secret.

Summary: 4 high, 4 medium, 0 low
```

ConfigEvaluater never includes configuration values in its reports.

## Options

```text
--format text|json          Select the output format
--severity low|medium|high  Show this severity or higher
--fail-on low|medium|high   Exit with status 1 at this severity or higher
--version                   Show the installed version
```

Input and command errors return exit status `2`. A completed scan normally
returns `0`; `--fail-on` can change it to `1` for automation.

## Current rules

| ID | Check | Severity |
|---|---|---|
| CFG001 | Debug mode enabled | Medium |
| CFG002 | Placeholder secret | High |
| CFG003 | Empty sensitive value | High |
| CFG004 | Non-local service URL uses HTTP | Medium |
| CFG005 | Wildcard CORS origin | Medium |
| CFG006 | Secure cookies disabled | Medium |
| CFG007 | TLS verification disabled | High |
| CFG008 | Debug mode bound to a public interface | High |
| CFG009 | Duplicate configuration key | Low |

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -v
```

The suite covers normal input, malformed input, edge cases, every security rule,
JSON output, severity filtering, missing files, exit statuses, and secret-safe
reporting.

## Limitations

- Only the documented subset of `.env` syntax is supported.
- Inline comments, variable expansion, and `export KEY=value` are not parsed.
- Rule matching uses common configuration names and may produce false positives
  or miss framework-specific settings.
- A clean report is not proof that a configuration is secure.

## Safety and ethical use

Only scan files you are authorized to access. Example files in this repository
contain fictional data. ConfigEvaluater performs local, read-only analysis and
does not transmit input contents.

## License

Released under the MIT License. See `LICENSE`.
