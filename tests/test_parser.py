import unittest
from pathlib import Path

from configevaluater.parser import EnvParseError, parse_env_file, parse_env_text


FIXTURES = Path(__file__).parent / "fixtures"


class ParserTests(unittest.TestCase):
    def test_parses_comments_quotes_and_equals_in_values(self):
        settings = parse_env_file(FIXTURES / "parser-cases.env")

        self.assertEqual([(item.key, item.value, item.line) for item in settings], [
            ("NAME", "hello world", 2),
            ("URL", "https://example.test/?a=b", 3),
        ])

    def test_retains_empty_values_and_duplicate_keys(self):
        settings = parse_env_text("TOKEN=\nDEBUG=false\nDEBUG=true\n")

        self.assertEqual(len(settings), 3)
        self.assertEqual(settings[0].value, "")

    def test_rejects_malformed_line_with_line_number(self):
        with self.assertRaisesRegex(EnvParseError, "line 2"):
            parse_env_file(FIXTURES / "malformed.env")

    def test_rejects_unmatched_quote(self):
        with self.assertRaisesRegex(EnvParseError, "unmatched quote"):
            parse_env_text('NAME="unfinished\n')


if __name__ == "__main__":
    unittest.main()
