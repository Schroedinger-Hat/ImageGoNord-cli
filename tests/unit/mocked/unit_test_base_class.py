from unittest import TestCase

import io
from pathlib import Path
from unittest.mock import patch


class UnitTestBaseClass(TestCase):
    DATA_PATH = Path(__file__).parent / "data"
    DEFAULT_OUTPUT_FILE_NAME = "nord.png"
    DEFAULT_OUTPUT_FILE_PATH = Path(DEFAULT_OUTPUT_FILE_NAME)
    DEFAULT_INPUT_FILE_PATH = DATA_PATH / "blue_square.png"

    def tearDown(self) -> None:
        self.stdout_patch.stop()
        self.stderr_patch.stop()
        self.mocked_go_nord.stop()

    def setUp(self) -> None:
        self.maxDiff = None
        self.stdout_patch = patch("sys.stdout", io.StringIO())
        self.mocked_stdout = self.stdout_patch.start()

        self.stderr_patch = patch("sys.stderr", io.StringIO())
        self.mocked_stderr = self.stderr_patch.start()

        self.go_nord_patch = patch("image_go_nord_client.main.GoNord")
        self.mocked_go_nord = self.go_nord_patch.start()
        self.mock_gn_instance = self.mocked_go_nord.return_value
