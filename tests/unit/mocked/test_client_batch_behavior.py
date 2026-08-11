import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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
        planned_output = payload["result"]["plan"][0]["output"]
        self.assertTrue(planned_output.endswith("nested/deep-nord.webp"))
        self.mocked_go_nord.assert_not_called()

    def test_preserve_relative_structure_when_out_dir_is_used(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            nested = base_path / "a" / "b"
            nested.mkdir(parents=True, exist_ok=True)
            (nested / "wall.png").write_text("x", encoding="utf-8")
            output_dir = base_path / "out"

            result = main(
                argv=[
                    "image-go-nord-client",
                    "batch",
                    str(base_path),
                    "--recursive",
                    f"--out-dir={output_dir}",
                    "--format=json",
                ]
            )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["result"]["plan"][0]["output"].endswith("a/b/wall-nord.png"))
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

    def test_run_batch_apply_successfully_in_json_mode(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            (base_path / "one.png").write_text("x", encoding="utf-8")
            (base_path / "two.jpg").write_text("x", encoding="utf-8")

            result = main(
                argv=[
                    "image-go-nord-client",
                    "batch",
                    str(base_path),
                    "--apply",
                    "--format=json",
                ]
            )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(0, result)
        self.assertTrue(payload["ok"])
        self.assertEqual(False, payload["result"]["dry_run"])
        self.assertEqual(2, payload["result"]["summary"]["converted"])
        self.assertEqual(0, payload["result"]["summary"]["failed"])
        self.assertEqual(2, len(payload["result"]["files"]))

    def test_create_nested_output_parent_directories_during_apply(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            nested = base_path / "a" / "b"
            nested.mkdir(parents=True, exist_ok=True)
            (nested / "wall.png").write_text("x", encoding="utf-8")
            output_dir = base_path / "converted"

            result = main(
                argv=[
                    "image-go-nord-client",
                    "batch",
                    str(base_path),
                    "--recursive",
                    f"--out-dir={output_dir}",
                    "--apply",
                    "--format=json",
                ]
            )

            payload = json.loads(self.mocked_stdout.getvalue().strip())
            self.assertEqual(0, result)
            self.assertTrue(payload["ok"])
            expected_dir = output_dir / "a" / "b"
            self.assertTrue(expected_dir.is_dir())

    def test_return_5_when_one_or_more_batch_apply_conversions_fail(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            (base_path / "one.png").write_text("x", encoding="utf-8")
            (base_path / "two.jpg").write_text("x", encoding="utf-8")

            self.mock_gn_instance.convert_image.side_effect = [
                RuntimeError("boom"),
                None,
            ]

            result = main(
                argv=[
                    "image-go-nord-client",
                    "batch",
                    str(base_path),
                    "--apply",
                    "--format=json",
                ]
            )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(5, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_CONVERSION_FAILED", payload["error"]["code"])
        self.assertEqual(1, payload["result"]["summary"]["converted"])
        self.assertEqual(1, payload["result"]["summary"]["failed"])

    def test_return_4_when_batch_apply_dependency_is_missing(self):
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            (base_path / "one.png").write_text("x", encoding="utf-8")

            with patch("image_go_nord_client.main.GoNord", None):
                result = main(
                    argv=[
                        "image-go-nord-client",
                        "batch",
                        str(base_path),
                        "--apply",
                        "--format=json",
                    ]
                )

        payload = json.loads(self.mocked_stdout.getvalue().strip())
        self.assertEqual(4, result)
        self.assertFalse(payload["ok"])
        self.assertEqual("E_DEPENDENCY", payload["error"]["code"])
