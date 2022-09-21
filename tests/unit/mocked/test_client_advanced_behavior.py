from unittest.mock import ANY
from image_go_nord_client.main import main


from .unit_test_base_class import UnitTestBaseClass


class ClientShould(UnitTestBaseClass):
    def test_convert_to_nord_palette_using_short_no_avg_pixels_parameter(self):
        main(argv=["image-go-nord-client", "-na", "-i=file1.png"])
        self.mock_gn_instance.set_avg_box_data.assert_not_called()
        self.mock_gn_instance.open_image.assert_called_with("file1.png")
        self.mock_gn_instance.disable_avg_algorithm.assert_called_once()
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_NAME
        )

    def test_convert_to_nord_palette_using_long_no_avg_pixels_parameter(self):
        main(
            argv=[
                "image-go-nord-client",
                "--no-avg",
                "--img=file2.png",
                "--out=output.jpg",
            ]
        )
        self.mock_gn_instance.enable_gaussian_blur.assert_not_called()
        self.mock_gn_instance.set_avg_box_data.assert_not_called()
        self.mock_gn_instance.open_image.assert_called_with("file2.png")
        self.mock_gn_instance.disable_avg_algorithm.assert_called_once()
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path="output.jpg"
        )

    def test_convert_to_nord_palette_using_short_blur_parameter(self):
        main(argv=["image-go-nord-client", "-b", "-i=file3.png"])
        self.mock_gn_instance.disable_avg_algorithm.assert_not_called()
        self.mock_gn_instance.enable_gaussian_blur.assert_called_once()
        self.mock_gn_instance.open_image.assert_called_with("file3.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_NAME
        )

    def test_convert_to_nord_palette_using_short_pixel_data_parameter(self):
        main(argv=["image-go-nord-client", "-i=file4.png", "-pa=20,15"])
        self.mock_gn_instance.enable_gaussian_blur.assert_not_called()
        self.mock_gn_instance.set_avg_box_data.assert_called_with(w="20", h="15")
        self.mock_gn_instance.open_image.assert_called_with("file4.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_NAME
        )

    def test_convert_to_nord_palette_using_long_pixel_data_parameter(self):
        main(argv=["image-go-nord-client", "-i=file4.png", "--pixels-area=20,15"])
        self.mock_gn_instance.set_avg_box_data.assert_called_with(w="20", h="15")
        self.mock_gn_instance.open_image.assert_called_with("file4.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_NAME
        )

    def test_convert_to_nord_palette_using_long_single_pixel_data_parameter(self):
        main(argv=["image-go-nord-client", "-i=file4.png", "--pixels-area=20"])
        self.mock_gn_instance.set_avg_box_data.assert_called_with(w="20", h="20")
        self.mock_gn_instance.open_image.assert_called_with("file4.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_NAME
        )

    def test_raise_error_using_wrong_single_pixel_data_parameter(self):
        with self.assertRaises(SystemExit) as cm:
            main(
                argv=[
                    "image-go-nord-client",
                    "-i=file4.png",
                    "--pixels-area=20,10,30",
                ]
            )
            self.assertEqual(2, cm.exception.code)

        with self.assertRaises(SystemExit) as cm:
            main(argv=["image-go-nord-client", "-i=file4.png", "--pixels-area"])
            self.assertEqual(2, cm.exception.code)

        with self.assertRaises(SystemExit) as cm:
            main(argv=["image-go-nord-client", "-i=file4.png", "--pixels-area=xxx,10"])
            self.assertEqual(2, cm.exception.code)
