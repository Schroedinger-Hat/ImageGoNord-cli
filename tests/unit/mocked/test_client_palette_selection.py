from pathlib import Path
from .unit_test_base_class import UnitTestBaseClass

from unittest.mock import ANY
from image_go_nord_client.main import main


class ClientShould(UnitTestBaseClass):
    def test_convert_to_nord_palette_when_given_only_img_and_out_parameters_in_short_version(
        self,
    ):
        main(["image-go-nort", "-i=file_1.png", "-o=file_output.png", "--monokai"])

        self.mock_gn_instance.open_image.assert_called_with("file_1.png")

        call_args = self.mock_gn_instance.set_palette_lookup_path.call_args
        file_path = call_args[0][0].lower()
        self.assertIn("monokai", file_path)
        self.assertTrue(Path(file_path).exists())

        self.mock_gn_instance.add_file_to_palette.assert_called_with("Colors.txt")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path="file_output.png"
        )

    def test_convert_to_nord_palette_with_aurora_theme_when_given_specific_palette(
        self,
    ):
        main(["image-go-nort", "-i=file_1.png", "-o=file_output.png", "--nord=Aurora"])

        self.mock_gn_instance.open_image.assert_called_with("file_1.png")

        call_args = self.mock_gn_instance.set_palette_lookup_path.call_args
        file_path = call_args[0][0].lower()
        self.assertIn("nord", file_path)
        self.assertTrue(Path(file_path).exists())

        self.mock_gn_instance.add_file_to_palette.assert_called_with("Aurora.txt")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path="file_output.png"
        )
