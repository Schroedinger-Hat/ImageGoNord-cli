from unittest.mock import patch

from image_go_nord_client.ign import run

from .unit_test_base_class import UnitTestBaseClass


class ModernCliFrameworkShould(UnitTestBaseClass):
    def test_fallback_to_legacy_main_when_typer_is_missing(self):
        with patch("image_go_nord_client.ign._is_typer_available", return_value=False):
            with patch("image_go_nord_client.ign.legacy_main", return_value=7) as mocked:
                result = run(["--img=input.png", "--palette=nord"])

        self.assertEqual(7, result)
        mocked.assert_called_once_with(
            ["image-go-nord-client", "--img=input.png", "--palette=nord"]
        )

    def test_use_legacy_route_for_existing_flag_style_even_if_typer_is_available(self):
        with patch("image_go_nord_client.ign._is_typer_available", return_value=True):
            with patch("image_go_nord_client.ign.legacy_main", return_value=0) as mocked:
                result = run(["--img=input.png"])

        self.assertEqual(0, result)
        mocked.assert_called_once_with(["image-go-nord-client", "--img=input.png"])

    def test_use_legacy_route_for_convert_with_legacy_img_option(self):
        with patch("image_go_nord_client.ign._is_typer_available", return_value=True):
            with patch("image_go_nord_client.ign.legacy_main", return_value=0) as mocked:
                result = run(["convert", "--img=input.png"])

        self.assertEqual(0, result)
        mocked.assert_called_once_with(
            ["image-go-nord-client", "convert", "--img=input.png"]
        )
