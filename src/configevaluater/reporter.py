"""Human-readable and JSON output for ConfigEvaluater findings."""

import json
from collections import Counter
from pathlib import Path

from configevaluater.models import Finding


def render_text(path: Path, findings: list[Finding]) -> str:
    lines = ["ConfigEvaluater scan", f"File: {path}", ""]

    if not findings:
        lines.extend([
            "No known insecure settings detected.",
            "Note: this result does not guarantee that the configuration is secure.",
        ])
        return "\n".join(lines)

    for finding in findings:
        lines.extend([
            f"{finding.severity.upper():<6} {finding.rule_id}  line {finding.line}  {finding.key}",
            f"       {finding.message}",
            f"       Recommendation: {finding.remediation}",
            "",
        ])

    counts = Counter(finding.severity for finding in findings)
    lines.append(f"Summary: {counts['high']} high, {counts['medium']} medium, {counts['low']} low")
    return "\n".join(lines)


def render_json(path: Path, findings: list[Finding]) -> str:
    counts = Counter(finding.severity for finding in findings)
    payload = {
        "file": str(path),
        "findings": [
            {
                "rule_id": finding.rule_id,
                "severity": finding.severity,
                "line": finding.line,
                "key": finding.key,
                "message": finding.message,
                "remediation": finding.remediation,
            }
            for finding in findings
        ],
        "summary": {level: counts[level] for level in ("high", "medium", "low")},
    }
    return json.dumps(payload, indent=2)
