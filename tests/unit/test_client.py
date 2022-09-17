import tempfile
import unittest
from pathlib import Path

from tests.utils import run_image_go_nord_client, is_image_empty, are_images_the_same


class ClientShould(unittest.TestCase):
    # Get blue_suqare.png path from data folder
    data = Path(__file__).parent.parent / 'data'
    blue_square_path = data / 'blue_square.png'
    blue_nord_square_path = data / 'blue_nord_square.png'

    def run_test(self, output_image_path, *args):
        command, output = run_image_go_nord_client(*args)
        self.assertFalse(is_image_empty(output_image_path))
        self.assertTrue(
            are_images_the_same(self.blue_nord_square_path, output_image_path),
            f"FAIL: The output image is NOT the same as the expected image \n{command}",
        )
        self.assertFalse(
            are_images_the_same(self.blue_square_path, output_image_path),
            f"FAIL: The output image IS the same as the expected image \n{command}",
        )

    def test_convert_to_nord_palette_when_given_only_img_and_out_parameters_in_extended_version(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / 'output.png'

            self.run_test(
                output_image_path,
                f'--img={self.blue_square_path}',
                f'--out={output_image_path}'
            )

    def test_convert_to_nord_palette_when_given_only_img_and_out_parameters_in_short_version(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / 'output.png'

            self.run_test(
                output_image_path,
                f'-i={self.blue_square_path}',
                f'-o={output_image_path}'
            )

    def test_return_version_when_given_version_extended_parameter(self):
        command, output = run_image_go_nord_client('--version')
        self.assertEqual('0.1.0', output.strip())

    def test_return_version_when_given_version_short_parameter(self):
        command, output = run_image_go_nord_client('-v')
        self.assertEqual('0.1.0', output.strip())

    def test_return_docs_when_given_help_extended_parameter(self):
        command, output = run_image_go_nord_client('--help')
        self.assertTrue('ImageGoNord, a converter for a rgb images to norththeme palette' in output)

    def test_return_docs_when_given_help_short_parameter(self):
        command, output = run_image_go_nord_client('-h')
        self.assertTrue('ImageGoNord, a converter for a rgb images to norththeme palette' in output)
