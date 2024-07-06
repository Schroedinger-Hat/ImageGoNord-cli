import tempfile
from pathlib import Path

from .unit_test_base_class import UnitTestBaseClass


class ClientShould(UnitTestBaseClass):
    # Get blue_suqare.png path from data folder
    data = Path(__file__).parent / "data"
    input_image_path = data / "blue_square.png"

    def test_convert_to_nord_palette_with_aurora_theme_when_given_specific_palette(
        self,
    ):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / "output.png"

            self.run_test(
                self.input_image_path,
                output_image_path,
                self.data / "blue_nord_aurora_square.png",
                f"-i={self.input_image_path}",
                f"-o={output_image_path}",
                "--palette=nord",
                "--colors=Aurora",
            )

    def test_convert_to_nord_palette_with_frost_theme_when_given_specific_palette(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / "output.png"

            self.run_test(
                self.input_image_path,
                output_image_path,
                self.data / "blue_nord_frost_square.png",
                f"-i={self.input_image_path}",
                f"-o={output_image_path}",
                "--palette=nord",
                "--colors=Frost",
            )

    def test_convert_to_nord_palette_with_polarnight_and_aurora_theme_when_given_specific_palette(
        self,
    ):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / "output.png"

            self.run_test(
                self.input_image_path,
                output_image_path,
                self.data / "blue_nord_polarnight_aurora_square.png",
                f"-i={self.input_image_path}",
                f"-o={output_image_path}",
                "--palette=nord",
                "--colors=PolarNight,Aurora",
            )
