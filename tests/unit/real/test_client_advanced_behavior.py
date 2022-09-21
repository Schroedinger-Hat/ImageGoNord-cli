import tempfile
from pathlib import Path
import unittest

from .unit_test_base_class import UnitTestBaseClass
from tests.utils import are_images_the_same


class ClientShould(UnitTestBaseClass):
    # Get blue_suqare.png path from data folder
    data = Path(__file__).parent / "data"
    input_image_path = data / "blue_square.png"
    expected_image_path = data / "blue_nord_square.png"

    def test_convert_to_nord_palette_using_no_avg_pixels_parameter(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / "output.png"
            input_image_path = self.data / "rainbow_square.png"

            self.run_test(
                input_image_path,
                output_image_path,
                self.data / "rainbow_nord_na_square.png",
                f"-i={input_image_path}",
                f"-o={output_image_path}",
                "--no-avg",
            )

    def test_convert_to_nord_palette_using_no_avg_pixels_short_parameter(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / "output.png"
            input_image_path = self.data / "rainbow_square.png"

            self.run_test(
                self.data / "rainbow_square.png",
                output_image_path,
                self.data / "rainbow_nord_na_square.png",
                f"-i={input_image_path}",
                f"-o={output_image_path}",
                "-na",
            )

    @unittest.skip("This test is not working")
    def test_make_image_difference_avg_pixel_and_no_avg_pixel_parameter(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / "output.png"
            output_image_na_path = Path(tmpdirname) / "output_na.png"
            input_image_path = self.data / "rainbow_square.png"

            self.run_test(
                input_image_path,
                output_image_path,
                self.data / "rainbow_nord_square.png",
                f"-i={input_image_path}",
                f"-o={output_image_path}",
            )

            self.run_test(
                input_image_path,
                output_image_na_path,
                self.data / "rainbow_nord_na_square.png",
                f"-i={input_image_path}",
                f"-o={output_image_na_path}",
                "--no-avg-pixels",
            )

            self.assertFalse(
                are_images_the_same(output_image_path, output_image_na_path)
            )
