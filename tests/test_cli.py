import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from configevaluater.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, content: str, *arguments: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.env"
            path.write_text(content, encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main([str(path), *arguments])
            return code, stdout.getvalue(), stderr.getvalue()

    def test_json_output_is_valid_and_does_not_expose_secret(self):
        secret = "changeme"
        code, output, error = self.run_cli(
            f"SECRET_KEY={secret}\n", "--format", "json"
        )
        payload = json.loads(output)

        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertEqual(payload["summary"]["high"], 1)
        self.assertNotIn(secret, output)

    def test_fail_on_threshold_returns_one(self):
        code, _, _ = self.run_cli("VERIFY_TLS=false\n", "--fail-on", "high")
        self.assertEqual(code, 1)

    def test_missing_file_returns_two(self):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["definitely-missing.env"])

        self.assertEqual(code, 2)
        self.assertIn("configevaluater: cannot read", stderr.getvalue())
        self.assertIn("file does not exist", stderr.getvalue())

    def test_severity_filter_hides_lower_findings(self):
        _, output, _ = self.run_cli(
            "DEBUG=false\nDEBUG=false\n", "--severity", "high"
        )
        self.assertNotIn("CFG009", output)


if __name__ == "__main__":
    unittest.main()

