import json
import re
from pathlib import Path
from unittest import TestCase


class ReadmeCliContractShould(TestCase):
    def setUp(self):
        self.readme_path = Path(__file__).resolve().parents[2] / "README.md"
        self.readme_content = self.readme_path.read_text(encoding="utf-8")

    def test_include_cli_contract_section(self):
        self.assertIn("## CLI Contract", self.readme_content)

    def test_keep_json_examples_in_contract_shape(self):
        json_blocks = re.findall(r"```json\n(.*?)\n```", self.readme_content, flags=re.DOTALL)
        self.assertGreaterEqual(len(json_blocks), 2)

        for block in json_blocks:
            payload = json.loads(block)
            self.assertIn("contract_version", payload)
            self.assertIn("ok", payload)
            self.assertIn("request_id", payload)
            self.assertRegex(payload["request_id"], r"^[0-9a-f-]{36}$")
            self.assertEqual("3.0", payload["contract_version"])

            if payload["ok"]:
                self.assertIn("result", payload)
                self.assertIsInstance(payload["result"], dict)
            else:
                self.assertIn("error", payload)
                self.assertIsInstance(payload["error"], dict)
                self.assertIn("code", payload["error"])
                self.assertIn("message", payload["error"])

    def test_document_expected_exit_codes(self):
        documented_codes = {
            int(code)
            for code in re.findall(r"- `([0-9]+)`:", self.readme_content)
        }
        self.assertTrue({0, 2, 3, 4, 5}.issubset(documented_codes))
