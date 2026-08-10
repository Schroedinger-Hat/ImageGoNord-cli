from unittest import TestCase

from image_go_nord_client import parse_arguments


class ArgparseShould(TestCase):
    def test_multiple_colors(self) -> None:
        command = [
            "image-go-nort",
            "-i=file_1.png",
            "-o=file_output.png",
            "--palette=nord",
            "--colors=Aurora,Frost",
        ]

        namespace, _ = parse_arguments(command)

        self.assertEqual(namespace.input_path, "file_1.png")
        self.assertEqual(namespace.output_path, "file_output.png")
        self.assertEqual(namespace.palette, "nord")
        self.assertEqual(namespace.colors, ["Aurora", "Frost"])

    def test_default_colors(self) -> None:
        command = ["image-go-nort", "-i=file_1.png", "-o=file_output.png"]
        namespace, _ = parse_arguments(command)
        self.assertEqual(namespace.input_path, "file_1.png")
        self.assertEqual(namespace.output_path, "file_output.png")
        self.assertEqual(namespace.palette, "nord")
        self.assertEqual(namespace.colors, [])

    def test_multiple_colors_nord(self) -> None:
        command = [
            "image-go-nort",
            "-i=file_1.png",
            "-o=file_output.png",
            "--palette=nord",
            "--colors=PolarNight,Aurora",
        ]

        namespace, _ = parse_arguments(command)

        self.assertEqual(namespace.input_path, "file_1.png")
        self.assertEqual(namespace.output_path, "file_output.png")
        self.assertEqual(namespace.palette, "nord")
        self.assertEqual(namespace.colors, ["PolarNight", "Aurora"])

    def test_convert_subcommand(self) -> None:
        command = [
            "image-go-nort",
            "convert",
            "-i=file_1.png",
            "-o=file_output.png",
            "--palette=nord",
        ]

        namespace, _ = parse_arguments(command)

        self.assertEqual(namespace.input_path, "file_1.png")
        self.assertEqual(namespace.output_path, "file_output.png")
        self.assertEqual(namespace.palette, "nord")
