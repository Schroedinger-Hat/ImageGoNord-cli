import json
from pathlib import Path
from tempfile import TemporaryDirectory

from image_go_nord_client.main import main

from .unit_test_base_class import UnitTestBaseClass


class ClientShould(UnitTestBaseClass):
    def test_run_batch_dry_run_in_json_mode(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            (base_path / "one.png").write_text("x", encoding="utf-8")
            (base_path / "two.jpg").write_text("x", encoding="utf-8")
            (base_path / "ignore.txt").write_text("x", encoding="utf-8")

            result = main(
                argv=[
                    "image-go-nord-client",
                    "batch",
                    str(base_path),
                    "--format=json",
                ]
            )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual("3.0", payload["contract_version"])
        self.assertEqual(2, payload["result"]["summary"]["images_detected"])
        self.assertEqual(2, payload["result"]["summary"]["planned_conversions"])
        self.assertEqual(False, payload["result"]["recursive"])
        self.assertEqual(True, payload["result"]["dry_run"])
        self.mocked_go_nord.assert_not_called()

    def test_include_nested_images_when_recursive_is_enabled(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            nested = base_path / "nested"
            nested.mkdir(parents=True, exist_ok=True)
            (nested / "deep.webp").write_text("x", encoding="utf-8")

            result = main(
                argv=[
                    "image-go-nord-client",
                    "batch",
                    str(base_path),
                    "--recursive",
                    "--format=json",
                ]
            )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual(1, payload["result"]["summary"]["images_detected"])
        self.assertEqual(True, payload["result"]["recursive"])
        self.mocked_go_nord.assert_not_called()

    def test_return_2_when_input_dir_is_missing(self):
        result = main(
            argv=[
                "image-go-nord-client",
                "batch",
                "/path/that/does/not/exist",
                "--format=json",
            ]
        )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(2, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_VALIDATION", payload["error"]["code"])
        self.assertIn("Input directory does not exist", payload["error"]["message"])
        self.mocked_go_nord.assert_not_called()

    def test_print_text_summary_and_commands(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            (base_path / "one.png").write_text("x", encoding="utf-8")

            result = main(argv=["image-go-nord-client", "batch", str(base_path)])

        output = self.mocked_stdout.getvalue()
        self.assertEqual(0, result)
        self.assertIn("batch dry-run summary", output)
        self.assertIn("images_detected: 1", output)
        self.assertIn("image-go-nord-client --img=", output)
        self.assertIn("--palette=nord", output)
        self.mocked_go_nord.assert_not_called()
