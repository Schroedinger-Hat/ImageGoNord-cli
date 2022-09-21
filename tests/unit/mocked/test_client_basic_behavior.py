from image_go_nord_client.main import main
from .unit_test_base_class import UnitTestBaseClass

from unittest.mock import ANY


class ClientShould(UnitTestBaseClass):
    def test_return_docs_when_nothing_is_given(self):
        with self.assertRaises(SystemExit):
            main(argv=["image-go-nord-client"])

        self.mock_gn_instance.open_image.assert_not_called()
        self.mock_gn_instance.convert_image.assert_not_called()
        self.assertIn(
            "image-go-nord-client: error: the following arguments are required: -i/--img",
            self.mocked_stderr.getvalue(),
        )

    def test_return_docs_when_given_help_parameter(self):
        with self.assertRaises(SystemExit):
            main(argv=["image-go-nord-client", "--help"])

        self.mock_gn_instance.open_image.assert_not_called()
        self.mock_gn_instance.convert_image.assert_not_called()
        self.assertIn(
            "ImageGoNord, a converter for a rgb images to norththeme palette",
            self.mocked_stdout.getvalue(),
        )

        with self.assertRaises(SystemExit) as cm:
            main(argv=["image-go-nord-client", "-h"])
            self.assertEqual(0, cm.exception.code)

        self.mock_gn_instance.open_image.assert_not_called()
        self.mock_gn_instance.convert_image.assert_not_called()
        self.assertIn(
            "ImageGoNord, a converter for a rgb images to norththeme palette",
            self.mocked_stdout.getvalue(),
        )

    def test_return_version_docs_when_given_version_parameter(self):
        with self.assertRaises(SystemExit) as cm:
            main(argv=["image-go-nord-client", "--version"])
            self.assertEqual(0, cm.exception.code)

        self.assertEqual("0.2.0", self.mocked_stdout.getvalue().strip())
        self.mock_gn_instance.open_image.assert_not_called()
        self.mock_gn_instance.convert_image.assert_not_called()

        with self.assertRaises(SystemExit) as cm:
            main(argv=["image-go-nord-client", "-v"])
            self.assertEqual(0, cm.exception.code)

        self.assertIn("0.2.0", self.mocked_stdout.getvalue().strip())
        self.mock_gn_instance.open_image.assert_not_called()
        self.mock_gn_instance.convert_image.assert_not_called()

    def test_no_output_when_convert_to_nord_palette_and_quiet_parameter_provided(self):
        main(argv=["image-go-nord-client", "-i=input0.png", "-q"])
        self.assertEqual("", self.mocked_stdout.getvalue())
        self.mock_gn_instance.open_image.assert_called_with("input0.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_PATH.name
        )
        self.mock_gn_instance.reset_mock()

        main(argv=["image-go-nord-client", "--img=input1.png", "--quiet"])
        self.assertEqual("", self.mocked_stdout.getvalue())
        self.mock_gn_instance.open_image.assert_called_with("input1.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_PATH.name
        )

    def test_convert_to_nord_palette_when_given_only_short_img_parameter(self):
        main(argv=["image-go-nord-client", "-i=input2.png"])
        self.mock_gn_instance.open_image.assert_called_with("input2.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_PATH.name
        )

    def test_convert_to_nord_palette_when_given_only_long_img_parameter(self):
        main(argv=["image-go-nord-client", "--img=input3.png"])
        self.mock_gn_instance.open_image.assert_called_with("input3.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path=self.DEFAULT_OUTPUT_FILE_PATH.name
        )

    def test_convert_to_nord_palette_when_given_only_short_img_and_out_parameters(self):
        main(argv=["image-go-nord-client", "-i=input4.png", "-o=output1.png"])
        self.mock_gn_instance.open_image.assert_called_with("input4.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path="output1.png"
        )

    def test_convert_to_nord_palette_when_given_only_long_img_and_out_parameters(self):
        main(argv=["image-go-nord-client", "--img=input4.png", "--out=output1.png"])
        self.mock_gn_instance.open_image.assert_called_with("input4.png")
        self.mock_gn_instance.convert_image.assert_called_with(
            ANY, save_path="output1.png"
        )
