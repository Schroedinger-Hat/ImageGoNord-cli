import unittest
from pathlib import Path

from tests.utils import run_image_go_nord_client, is_image_empty, are_images_the_same


class UnitTestBaseClass(unittest.TestCase):
    input_image_path = None
    expected_image_path = None

    def tearDown(self) -> None:
        # Delete the output image if exists
        std_output_path = Path('nord.png')
        if std_output_path.exists():
            std_output_path.unlink()

    def run_test(self, output_image_path, *args):
        assert self.input_image_path is not None, "The input_image_path is not set"
        assert self.expected_image_path is not None, "The expected_image_path is not set"

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
