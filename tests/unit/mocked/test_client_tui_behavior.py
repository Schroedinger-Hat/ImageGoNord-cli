import json
from unittest.mock import patch

from image_go_nord_client.main import main

from .unit_test_base_class import UnitTestBaseClass


class ClientShould(UnitTestBaseClass):
    def test_run_tui_action_browse_palettes_in_json_mode(self):
        result = main(
            argv=[
                "image-go-nord-client",
                "tui",
                "--action=browse-palettes",
                "--format=json",
            ]
        )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual("tui-action", payload["result"]["mode"])
        self.assertEqual("browse-palettes", payload["result"]["action"])
        self.assertIn("nord", payload["result"]["palettes"])
        self.mocked_go_nord.assert_not_called()

    def test_run_tui_action_convert_image_in_text_mode(self):
        result = main(
            argv=["image-go-nord-client", "tui", "--action=convert-image"]
        )

        self.assertEqual(0, result)
        self.assertIn("Convert flow is available in CLI mode", self.mocked_stdout.getvalue())
        self.mocked_go_nord.assert_not_called()

    def test_fail_tui_action_with_validation_error_payload(self):
        with patch(
            "image_go_nord_client.main._run_tui_action_helper",
            return_value=(2, {"message": "Unknown action: invalid-action"}),
        ):
            result = main(
                argv=[
                    "image-go-nord-client",
                    "tui",
                    "--action=convert-image",
                    "--format=json",
                ]
            )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(2, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_VALIDATION", payload["error"]["code"])
        self.mocked_go_nord.assert_not_called()

    def test_return_0_when_tui_exits_successfully(self):
        with patch("image_go_nord_client.main._launch_tui", return_value=(0, "done")):
            result = main(argv=["image-go-nord-client", "tui"])

        self.assertEqual(0, result)
        self.assertIn("done", self.mocked_stdout.getvalue())
        self.mocked_go_nord.assert_not_called()

    def test_return_json_payload_when_tui_exits_successfully(self):
        with patch("image_go_nord_client.main._launch_tui", return_value=(0, "done")):
            result = main(argv=["image-go-nord-client", "tui", "--format=json"])

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual("3.0", payload["contract_version"])
        self.assertRegex(payload["request_id"], r"^[0-9a-f-]{36}$")
        self.assertEqual("tui", payload["result"]["mode"])
        self.mocked_go_nord.assert_not_called()

    def test_return_4_when_tui_dependency_is_missing(self):
        with patch(
            "image_go_nord_client.main._launch_tui",
            return_value=(4, "Textual is not installed"),
        ):
            result = main(argv=["image-go-nord-client", "tui"])

        self.assertEqual(4, result)
        self.mocked_go_nord.assert_not_called()

    def test_return_json_error_when_tui_dependency_is_missing(self):
        with patch(
            "image_go_nord_client.main._launch_tui",
            return_value=(4, "Textual is not installed"),
        ):
            result = main(argv=["image-go-nord-client", "tui", "--format=json"])

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(4, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_DEPENDENCY", payload["error"]["code"])
        self.mocked_go_nord.assert_not_called()
