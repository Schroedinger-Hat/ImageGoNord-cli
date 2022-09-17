import tempfile
import unittest
from pathlib import Path

from tests.utils import run_image_go_nord_client, is_image_empty, are_images_the_same


class ClientShould(unittest.TestCase):
    # Get blue_suqare.png path from data folder
    data = Path(__file__).parent.parent / 'data'
    input_image_path = data / 'blue_square.png'
    expected_image_path = data / 'blue_monokai_square.png'

    def tearDown(self) -> None:
        # Delete the output image if exists
        std_output_path = Path('nord.png')
        if std_output_path.exists():
            std_output_path.unlink()

    def run_test(self, output_image_path, *args):
        command, output = run_image_go_nord_client(*args)
        self.assertFalse(is_image_empty(output_image_path))
        self.assertTrue(
            are_images_the_same(self.expected_image_path, output_image_path),
            f"FAIL: The output image is NOT the same as the expected image \n{command}",
        )
        self.assertFalse(
            are_images_the_same(self.input_image_path, output_image_path),
            f"FAIL: The output image IS the same as the expected image \n{command}",
        )

        return output

    def test_convert_to_nord_palette_when_given_only_img_and_out_parameters_in_short_version(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / 'blue_monokai_square.png'

            self.run_test(
                output_image_path,
                f'-i={self.input_image_path}',
                f'-o={output_image_path}',
                '--monokai'
            )
