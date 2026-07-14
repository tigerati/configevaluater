# ConfigEvaluater User Manual

## Supported environment

ConfigEvaluater requires Python 3.9 or newer and supports operating systems where
Python runs. It has no third-party runtime dependencies.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

## Input format

The input is a UTF-8 text file containing one `KEY=value` setting per line:

```dotenv
# Full-line comments are allowed.
DEBUG=false
APP_NAME="Example application"
CALLBACK_URL=https://example.test/callback?mode=test
EMPTY_VALUE=
```

Keys may contain letters, numbers, and underscores, but cannot begin with a
number. Values can be unquoted, single-quoted, or double-quoted. Blank lines and
full-line comments are ignored. Values may contain `=` characters.

Inline comments, variable expansion, multiline values, and the `export` prefix
are not supported in version 0.1.0.

## Commands

Scan a file and display every finding:

```bash
configevaluater examples/insecure.env
```

Display only high-severity findings:

```bash
configevaluater examples/insecure.env --severity high
```

Produce machine-readable output:

```bash
configevaluater examples/insecure.env --format json
```

Return status `1` when a high-severity or more serious finding exists:

```bash
configevaluater examples/insecure.env --fail-on high
```

`--severity` affects displayed findings. `--fail-on` evaluates all findings,
including findings hidden by the display filter.

## Output fields

- **Severity:** `HIGH`, `MEDIUM`, or `LOW`.
- **Rule ID:** Stable identifier for the check, such as `CFG002`.
- **Line:** Input line associated with the finding.
- **Key:** Configuration key involved in the finding.
- **Message:** Reason the setting may be unsafe.
- **Recommendation:** A practical remediation step.

Configuration values are deliberately omitted from output.

## Exit status

| Status | Meaning |
|---:|---|
| 0 | Scan completed and did not meet the `--fail-on` threshold |
| 1 | A finding met the selected `--fail-on` threshold |
| 2 | Invalid input, unreadable file, or command error |

## Complete example

The repository includes `examples/insecure.env`. Its first three settings are:

```dotenv
DEBUG=true
HOST=0.0.0.0
SECRET_KEY=changeme
```

From the project directory, run:

```bash
configevaluater examples/insecure.env
```

ConfigEvaluater reports debug mode, the placeholder secret, and the combined risk
of exposing debug mode on a public interface. Replace the placeholder, disable
debug mode, and bind development services to a local address.

## Troubleshooting

### `configevaluater: command not found`

Activate the virtual environment and install the package. Alternatively, run:

```bash
PYTHONPATH=src python3 -m configevaluater path/to/file.env
```

### `expected KEY=value`

The reported line does not contain an equals sign. Rewrite it as one setting per
line, for example `DEBUG=false`.

### `unmatched quote in value`

The value begins or ends with a quote but does not have a matching quote.

### Unexpected or missing warning

ConfigEvaluater recognizes common key names and is not framework-aware. Check the
rule catalogue in `README.md` and record any false positive as a known
limitation.

## Test and demonstration files

- `examples/insecure.env` demonstrates multiple high- and medium-severity findings.
- `examples/secure.env` demonstrates a clean scan.
- `examples/malformed.env` demonstrates a useful format error.
- `examples/edge-cases.env` demonstrates quoted values, embedded equals signs, and
  a duplicate key.

All example values are fictional and safe to publish.
