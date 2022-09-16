import os
import os.path
import subprocess
import tempfile
import unittest
from pathlib import Path


def run_image_go_nord_script(*args):
    """Run the image-go-nord script with the given arguments.

    :param args: The arguments to pass directly to the script.
    """

    script_path = str(Path.cwd() / 'src' / 'cli.py')
    os.path.join(os.path.dirname(__file__), "../src/image-go-nord")
    return subprocess.check_output(
        ["python", script_path, *args], universal_newlines=True
    )


def is_image_empty(image_path):
    """Check if an image is empty.

    :param image_path: The path to the image.
    """
    return Path(image_path).stat().st_size == 0


def are_images_the_same(image1_path, image2_path):
    """Compare two images and return True if they are the same.

    :param image1_path: The path to the first image.
    :param image2_path: The path to the second image.
    """
    return Path(image1_path).read_bytes() == Path(image2_path).read_bytes()


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
            output_path = Path(tmpdirname) / 'output.png'
            script = run_image_go_nord_script(f'--img={self.blue_square_path}', f'--out={output_path}')

            self.assertFalse(is_image_empty(output_path))

            self.assertTrue(
                are_images_the_same(self.blue_nord_square_path, output_path),
                "FAIL: The output image is NOT the same as the expected image {}".format(script),
            )

            self.assertFalse(
                are_images_the_same(self.blue_square_path, output_path),
                "FAIL: The output image IS the same as the expected image {}".format(script),
            )
