import tempfile
from pathlib import Path

from tests.unit.unit_test_base_class import UnitTestBaseClass
from tests.utils import run_image_go_nord_client


class ClientShould(UnitTestBaseClass):
    # Get blue_suqare.png path from data folder
    data = Path(__file__).parent.parent / 'data'
    input_image_path = data / 'blue_square.png'
    expected_image_path = data / 'blue_nord_square.png'

    def test_return_docs_when_given_help_extended_parameter(self):
        _, output = run_image_go_nord_client('--help')
        self.assertTrue('ImageGoNord, a converter for a rgb images to norththeme palette' in output)

    def test_return_docs_when_given_help_short_parameter(self):
        _, output = run_image_go_nord_client('-h')
        self.assertTrue('ImageGoNord, a converter for a rgb images to norththeme palette' in output)

    def test_return_version_when_given_version_extended_parameter(self):
        _, output = run_image_go_nord_client('--version')
        self.assertEqual('0.1.0', output.strip())

    def test_return_version_when_given_version_short_parameter(self):
        _, output = run_image_go_nord_client('-v')
        self.assertEqual('0.1.0', output.strip())

    def test_no_output_when_convert_to_nord_palette_and_quiet_short_parameter_provided(self):
        _, output = run_image_go_nord_client(f'-i={self.input_image_path}', '-q')
        self.assertEqual('', output)

    def test_no_output_when_convert_to_nord_palette_and_quiet_extended_parameter_provided(self):
        _, output = run_image_go_nord_client(f'--img={self.input_image_path}', '--quiet')
        self.assertEqual('', output)

    def test_convert_to_nord_palette_when_given_only_img_in_short_version(self):
        # Check if default file nord.png is created in the current directory
        run_image_go_nord_client(f'-i={self.input_image_path}')
        default_file_path = Path('nord.png')
        self.assertTrue(default_file_path.exists())

    def test_convert_to_nord_palette_when_given_only_img_in_extended_version(self):
        # Check if default file nord.png is created in the current directory
        run_image_go_nord_client(f'--img={self.input_image_path}')
        default_file_path = Path('nord.png')
        self.assertTrue(default_file_path.exists())

    def test_convert_to_nord_palette_when_given_only_img_and_out_parameters_in_extended_version(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / 'blue_monokai_square.png'

            self.run_test(
                output_image_path,
                f'--img={self.input_image_path}',
                f'--out={output_image_path}'
            )

    def test_convert_to_nord_palette_when_given_only_img_and_out_parameters_in_short_version(self):
        # Create a temporary folder to store the output image
        # Run the script with the image path input and output and check result
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_image_path = Path(tmpdirname) / 'blue_monokai_square.png'

            self.run_test(
                output_image_path,
                f'-i={self.input_image_path}',
                f'-o={output_image_path}'
            )
