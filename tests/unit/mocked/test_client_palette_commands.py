import json
from unittest.mock import patch

from image_go_nord_client.main import main

from .unit_test_base_class import UnitTestBaseClass


class ClientShould(UnitTestBaseClass):
    def test_use_palette_renderer_helper_in_text_mode(self):
        with patch("image_go_nord_client.main._print_palette_names") as mocked_renderer:
            result = main(argv=["image-go-nord-client", "palette", "list"])

        self.assertEqual(0, result)
        mocked_renderer.assert_called_once()
        self.mocked_go_nord.assert_not_called()

    def test_list_available_palettes_in_text_mode(self):
        result = main(argv=["image-go-nord-client", "palette", "list"])

        output = self.mocked_stdout.getvalue()
        self.assertEqual(0, result)
        self.assertIn("nord", output)
        self.assertIn("monokai", output)
        self.mocked_go_nord.assert_not_called()

    def test_list_available_palettes_in_json_mode(self):
        result = main(argv=["image-go-nord-client", "palette", "--format=json", "list"])

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual("3.0", payload["contract_version"])
        self.assertRegex(payload["request_id"], r"^[0-9a-f-]{36}$")
        self.assertIn("nord", payload["result"]["palettes"])
        self.mocked_go_nord.assert_not_called()

    def test_show_palette_info_in_json_mode(self):
        result = main(
            argv=["image-go-nord-client", "palette", "info", "nord", "--format=json"]
        )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual("nord", payload["result"]["name"])
        self.assertIn("Aurora", payload["result"]["colors"])
        self.mocked_go_nord.assert_not_called()

    def test_return_2_when_palette_info_target_is_missing(self):
        result = main(
            argv=[
                "image-go-nord-client",
                "palette",
                "info",
                "missing-palette",
                "--format=json",
            ]
        )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(2, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_PALETTE_NOT_FOUND", payload["error"]["code"])
        self.mocked_go_nord.assert_not_called()
