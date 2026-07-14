import unittest
from pathlib import Path

from configevaluater.parser import parse_env_file
from configevaluater.rules import scan


FIXTURES = Path(__file__).parent / "fixtures"


class RuleTests(unittest.TestCase):
    def test_detects_all_primary_insecure_patterns(self):
        settings = parse_env_file(FIXTURES / "all-insecure.env")

        self.assertEqual({finding.rule_id for finding in scan(settings)}, {
            "CFG001", "CFG002", "CFG003", "CFG004", "CFG005", "CFG006", "CFG007", "CFG008"
        })

    def test_secure_settings_have_no_findings(self):
        settings = parse_env_file(FIXTURES / "secure.env")

        self.assertEqual(scan(settings), [])

    def test_local_http_url_is_allowed(self):
        self.assertEqual(scan(parse_env_file(FIXTURES / "local-http.env")), [])

    def test_duplicate_key_reports_later_occurrence(self):
        findings = scan(parse_env_file(FIXTURES / "duplicate.env"))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "CFG009")
        self.assertEqual(findings[0].line, 3)


if __name__ == "__main__":
    unittest.main()
