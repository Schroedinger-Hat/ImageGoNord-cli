from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from image_go_nord_client import Color, Palette
from image_go_nord_client.tui import convert_image_from_tui


class TuiConversionHelperShould(TestCase):
    def test_return_2_when_input_path_is_missing(self):
        with patch("image_go_nord_client.tui.GoNord", object()):
            result, payload = convert_image_from_tui(
                colors=[],
                disable_avg_pixels=False,
                enable_blur=False,
                input_path="",
                output_path="nord.png",
                palette="nord",
            )

        self.assertEqual(2, result)
        self.assertIn("Input image path is required", payload["message"])

    def test_return_2_when_palette_is_unknown(self):
        with patch("image_go_nord_client.tui.GoNord", object()), patch(
            "image_go_nord_client.tui.search_palette_by_name", return_value=None
        ):
            result, payload = convert_image_from_tui(
                colors=[],
                disable_avg_pixels=False,
                enable_blur=False,
                input_path="/tmp/in.png",
                output_path="nord.png",
                palette="missing",
            )

        self.assertEqual(2, result)
        self.assertIn("No palette found with the name missing", payload["message"])

    def test_return_0_when_conversion_succeeds(self):
        palette = Palette(
            name="nord",
            path=Path("/tmp/nord"),
            colors=[
                Color(name="Aurora", path=Path("/tmp/nord/Aurora.txt")),
                Color(name="Frost", path=Path("/tmp/nord/Frost.txt")),
            ],
        )

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "in.png"
            output_path = Path(tmpdir) / "out" / "nord.png"
            input_path.write_bytes(b"fake-image")

            with patch(
                "image_go_nord_client.tui.search_palette_by_name",
                return_value=palette,
            ), patch("image_go_nord_client.tui.GoNord") as mocked_go_nord:
                result, payload = convert_image_from_tui(
                    colors=["Aurora"],
                    disable_avg_pixels=True,
                    enable_blur=True,
                    input_path=str(input_path),
                    output_path=str(output_path),
                    palette="nord",
                )

        self.assertEqual(0, result)
        self.assertEqual("nord", payload["palette"])
        self.assertEqual(["Aurora"], payload["colors"])
        self.assertIn("Converted image saved", payload["message"])

        gn_instance = mocked_go_nord.return_value
        gn_instance.enable_gaussian_blur.assert_called_once()
        gn_instance.disable_avg_algorithm.assert_called_once()
        gn_instance.reset_palette.assert_called_once()
        gn_instance.set_palette_lookup_path.assert_called_once_with("/tmp/nord/")
        gn_instance.add_file_to_palette.assert_called_once_with("Aurora.txt")
        gn_instance.open_image.assert_called_once_with(str(input_path))
        gn_instance.convert_image.assert_called_once()
