import tempfile
import unittest
from pathlib import Path

from tests.utils import run_image_go_nord_client, is_image_empty, are_images_the_same


class TestClient(unittest.TestCase):
    # Get blue_suqare.png path from data folder
    data = Path(__file__).parent.parent / 'data'
    blue_square_path = data / 'blue_square.png'
    blue_nord_square_path = data / 'blue_nord_square.png'

    def test_client_basic_conversion(self):
        """Run image-go-nord script with only the image path input and output and check result"""

        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / 'output.png'
            command, output = run_image_go_nord_client(f'--img={self.blue_square_path}', f'--out={output_image_path}')

            self.assertFalse(is_image_empty(output_image_path))

            self.assertTrue(
                are_images_the_same(self.blue_nord_square_path, output_image_path),
                f"FAIL: The output image is NOT the same as the expected image \n{command}",
            )

            self.assertFalse(
                are_images_the_same(self.blue_square_path, output_image_path),
                f"FAIL: The output image IS the same as the expected image \n{command}",
            )
