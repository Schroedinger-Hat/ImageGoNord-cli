import subprocess
from pathlib import Path


def run_image_go_nord_client(*args):
    """Run the image-go-nord script with the given arguments.

    :param args: The arguments to pass directly to the script.
    """

    command = ["python", (str(Path.cwd() / 'src' / 'cli.py')), *args]
    return " ".join(command), subprocess.check_output(command, universal_newlines=True)


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
