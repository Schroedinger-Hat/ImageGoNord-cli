import json
from unittest.mock import patch

from image_go_nord_client.main import main

from .unit_test_base_class import UnitTestBaseClass


class ClientShould(UnitTestBaseClass):
    def test_return_0_and_text_output_when_doctor_passes(self):
        with patch("image_go_nord_client.main._is_textual_available", return_value=True):
            result = main(argv=["image-go-nord-client", "doctor"])

        self.assertEqual(0, result)
        self.assertIn("doctor checks passed", self.mocked_stdout.getvalue())
        self.assertIn("image_go_nord: pass", self.mocked_stdout.getvalue())
        self.mocked_go_nord.assert_not_called()

    def test_return_json_output_when_doctor_passes(self):
        with patch("image_go_nord_client.main._is_textual_available", return_value=False):
            result = main(argv=["image-go-nord-client", "doctor", "--format=json"])

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual("3.0", payload["contract_version"])
        self.assertRegex(payload["request_id"], r"^[0-9a-f-]{36}$")
        checks = {check["name"]: check for check in payload["result"]["checks"]}
        self.assertEqual("pass", checks["image_go_nord"]["status"])
        self.assertEqual("warn", checks["textual"]["status"])
        self.mocked_go_nord.assert_not_called()

    def test_return_4_and_dependency_error_when_imagegonord_missing(self):
        with patch("image_go_nord_client.main.GoNord", None):
            result = main(argv=["image-go-nord-client", "doctor", "--format=json"])

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(4, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_DEPENDENCY", payload["error"]["code"])
        self.mocked_go_nord.assert_not_called()
