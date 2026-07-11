"""Security checks for parsed environment settings."""

from collections import Counter
from collections.abc import Iterable

from src.configevaluater.models import Finding, Setting

TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}
FALSE_VALUES = {"0", "false", "no", "off", "disabled"}
PLACEHOLDERS = {
    "changeme",
    "change-me",
    "password",
    "secret",
    "default",
    "your-secret-here",
    "replace-me",
    "todo",
}
SENSITIVE_WORDS = ("PASSWORD", "PASSWD", "SECRET", "TOKEN", "API_KEY", "PRIVATE_KEY")
DEBUG_KEYS = {"DEBUG", "APP_DEBUG", "FLASK_DEBUG", "DJANGO_DEBUG"}
PUBLIC_HOST_KEYS = {"HOST", "BIND", "LISTEN_HOST"}
TLS_VERIFY_KEYS = {"VERIFY_TLS", "TLS_VERIFY", "SSL_VERIFY", "VERIFY_SSL"}
COOKIE_SECURE_KEYS = {"SESSION_COOKIE_SECURE", "COOKIE_SECURE", "SECURE_COOKIE"}
CORS_KEYS = {"CORS_ALLOW_ORIGINS", "CORS_ALLOWED_ORIGINS", "ALLOWED_ORIGINS"}
SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def scan(settings: Iterable[Setting]) -> list[Finding]:
    """Apply all rules and return findings ordered by severity and line."""
    items = list(settings)
    findings: list[Finding] = []
    findings.extend(_check_individual_settings(items))
    findings.extend(_check_duplicates(items))
    findings.extend(_check_public_debug(items))
    return sorted(
        findings,
        key=lambda finding: (-SEVERITY_ORDER[finding.severity], finding.line, finding.rule_id),
    )


def _check_individual_settings(settings: list[Setting]) -> list[Finding]:
    findings: list[Finding] = []

    for setting in settings:
        key = setting.key.upper()
        normalized = setting.value.strip().lower()

        if key in DEBUG_KEYS and normalized in TRUE_VALUES:
            findings.append(_finding("CFG001", "medium", setting, "Debug mode is enabled.", "Disable debug mode in production."))

        if _is_sensitive(key) and normalized in PLACEHOLDERS:
            findings.append(_finding("CFG002", "high", setting, "A placeholder secret value was detected.", "Replace it with a securely generated secret."))

        if _is_sensitive(key) and not setting.value.strip():
            findings.append(_finding("CFG003", "high", setting, "A sensitive setting has an empty value.", "Provide the value securely at deployment time."))

        if _looks_like_url_key(key) and normalized.startswith("http://") and not _is_local_url(normalized):
            findings.append(_finding("CFG004", "medium", setting, "A service URL uses unencrypted HTTP.", "Use HTTPS when communicating beyond the local machine."))

        if key in CORS_KEYS and normalized == "*":
            findings.append(_finding("CFG005", "medium", setting, "Cross-origin access is allowed from every origin.", "List only the trusted origins that require access."))

        if key in COOKIE_SECURE_KEYS and normalized in FALSE_VALUES:
            findings.append(_finding("CFG006", "medium", setting, "Secure cookies are disabled.", "Enable secure cookies when the application uses HTTPS."))

        if key in TLS_VERIFY_KEYS and normalized in FALSE_VALUES:
            findings.append(_finding("CFG007", "high", setting, "TLS certificate verification is disabled.", "Enable certificate verification and use a trusted CA."))

    return findings


def _check_duplicates(settings: list[Setting]) -> list[Finding]:
    counts = Counter(setting.key.upper() for setting in settings)
    seen: set[str] = set()
    findings: list[Finding] = []

    for setting in settings:
        key = setting.key.upper()
        if counts[key] > 1 and key in seen:
            findings.append(_finding("CFG009", "low", setting, "This key is defined more than once.", "Remove the duplicate and keep one intentional value."))
        seen.add(key)

    return findings


def _check_public_debug(settings: list[Setting]) -> list[Finding]:
    debug = next((item for item in settings if item.key.upper() in DEBUG_KEYS and item.value.lower() in TRUE_VALUES), None)
    public_host = next((item for item in settings if item.key.upper() in PUBLIC_HOST_KEYS and item.value.strip() in {"0.0.0.0", "::"}), None)

    if debug and public_host:
        return [_finding("CFG008", "high", public_host, "Debug mode may be exposed on a public network interface.", "Disable debug mode or bind the application to a local interface.")]
    return []


def _finding(rule_id: str, severity: str, setting: Setting, message: str, remediation: str) -> Finding:
    return Finding(rule_id, severity, setting.line, setting.key, message, remediation)


def _is_sensitive(key: str) -> bool:
    return any(word in key for word in SENSITIVE_WORDS)


def _looks_like_url_key(key: str) -> bool:
    return key.endswith("_URL") or key.endswith("_URI") or key in {"URL", "URI"}


def _is_local_url(value: str) -> bool:
    return value.startswith(("http://localhost", "http://127.0.0.1", "http://[::1]"))

