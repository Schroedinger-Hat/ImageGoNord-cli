import argparse
from argparse import RawDescriptionHelpFormatter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VERSION = (Path(__file__).parent / "VERSION").read_text().strip()
DEFAULT_EXTENSION = ".png"
OUTPUT_IMAGE_NAME = "nord" + DEFAULT_EXTENSION

__doc__ = """ImageGoNord, a converter for a rgb images to norththeme palette.
Usage: gonord [OPTION]...

Mandatory arguments to long options are mandatory for short options too.

Startup:


Theme options:
  --PALETTE[=LIST_COLOR_SET]        the palettes can be found in the
                                    src/palettes/ directory (actually there is
                                    only nord), by replacing 'PALETTE' with a
                                    theme name it is possible to select it. If
                                    necessary you can specify the set of colors
                                    you want to use.
                                    Ex: python src/cli.py --nord=Aurora,PolarNight,SnowStorm
                                    Ex: python src/cli.py --monokai

Email bug reports, questions, discussions to <dev@schroedinger-hat.org>
and/or open issues at https://github.com/Schroedinger-Hat/ImageGoNord/issues/new
"""


def parse_pixels_area(value: str):
    if not value:
        raise TypeError("Invalid value for pixels area: {}".format(value))

    values = value.split(",")
    if len(values) > 2:
        raise ValueError(
            "Invalid number of parameters for pixels area: {}".format(value)
        )

    if not all(map(lambda x: x.isdigit(), values)):
        raise ValueError(
            "Invalid value for pixels area, all should be integer: {}".format(value)
        )

    return values


@dataclass
class Color:
    name: str
    path: Path


@dataclass
class Palette:
    name: str
    path: Path
    colors: list[Color]


def get_palette_dict() -> dict[str, Palette]:
    return {
        folder.name.lower(): Palette(
            name=folder.name.lower(),
            path=folder,
            colors=[
                Color(name=file.name.replace(".txt", ""), path=file)
                for file in folder.iterdir()
            ],
        )
        for folder in (Path(__file__).parent / "palettes").iterdir()
    }


def get_palette_list() -> list[Palette]:
    return [
        Palette(
            name=folder.name.lower(),
            path=folder,
            colors=[
                Color(name=file.name.replace(".txt", ""), path=file)
                for file in folder.iterdir()
            ],
        )
        for folder in (Path(__file__).parent / "palettes").iterdir()
    ]


def search_palette_by_name(name: str) -> Optional[Palette]:
    for palette in get_palette_list():
        if name.lower() == palette.name.lower():
            return palette

    return None


def get_default_palette() -> Palette:
    default_path = Path(__file__).parent / "palettes" / "nord"
    return Palette(
        name="nord",
        path=default_path,
        colors=[
            Color(name=file.name.replace(".txt", ""), path=file)
            for file in default_path.iterdir()
        ],
    )


def normalize_argv(argv: list[str]) -> list[str]:
    normalized_argv = argv.copy()

    if normalized_argv and not normalized_argv[0].startswith("-"):
        normalized_argv = normalized_argv[1:]

    if normalized_argv and normalized_argv[0] == "convert":
        normalized_argv = normalized_argv[1:]

    return normalized_argv


def parse_arguments(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = get_argument_parser()
    return parser.parse_known_args(normalize_argv(argv))


def parse_palette_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Palette management commands",
        add_help=True,
        prog="image-go-nord-client palette",
    )

    parser.add_argument(
        "--format",
        type=str,
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="specify output format",
    )

    subparsers = parser.add_subparsers(dest="palette_action", required=True)

    list_parser = subparsers.add_parser("list", help="list available palettes")
    list_parser.add_argument(
        "--format",
        type=str,
        dest="sub_output_format",
        choices=["text", "json"],
        default=None,
        help="specify output format",
    )

    info_parser = subparsers.add_parser("info", help="show palette details")
    info_parser.add_argument(
        "--format",
        type=str,
        dest="sub_output_format",
        choices=["text", "json"],
        default=None,
        help="specify output format",
    )
    info_parser.add_argument("name", type=str, help="palette name")

    arguments = parser.parse_args(normalize_argv(argv)[1:])
    if arguments.sub_output_format is not None:
        arguments.output_format = arguments.sub_output_format

    return arguments


def parse_tui_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interactive terminal UI",
        add_help=True,
        prog="image-go-nord-client tui",
    )

    parser.add_argument(
        "--format",
        type=str,
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="specify output format",
    )

    parser.add_argument(
        "--action",
        type=str,
        dest="action",
        choices=["convert-image", "browse-palettes", "batch-conversion"],
        default=None,
        help="run a TUI action without launching the interactive app",
    )

    parser.add_argument(
        "--img",
        type=str,
        dest="input_path",
        default=None,
        help="input image path for convert-image action",
    )

    parser.add_argument(
        "--out",
        type=str,
        dest="output_path",
        default=OUTPUT_IMAGE_NAME,
        help="output image path for convert-image action",
    )

    parser.add_argument(
        "--palette",
        type=str,
        dest="palette",
        default="nord",
        help="palette for convert-image action",
    )

    parser.add_argument(
        "--colors",
        type=lambda value: list(value.split(",")),
        dest="colors",
        default=[],
        help="comma-separated colors for convert-image action",
    )

    parser.add_argument(
        "--blur",
        action="store_true",
        dest="enable_blur",
        default=False,
        help="enable blur for convert-image action",
    )

    parser.add_argument(
        "--no-avg",
        action="store_true",
        dest="disable_avg_pixels",
        default=False,
        help="disable avg optimization for convert-image action",
    )

    return parser.parse_args(normalize_argv(argv)[1:])


def parse_doctor_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Environment diagnostics",
        add_help=True,
        prog="image-go-nord-client doctor",
    )

    parser.add_argument(
        "--format",
        type=str,
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="specify output format",
    )

    return parser.parse_args(normalize_argv(argv)[1:])


def parse_batch_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch conversion (dry-run)",
        add_help=True,
        prog="image-go-nord-client batch",
    )

    parser.add_argument(
        "input_dir",
        type=str,
        help="input directory with images to convert",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        dest="recursive",
        default=False,
        help="scan input directory recursively",
    )

    parser.add_argument(
        "--palette",
        type=str,
        dest="palette",
        default="nord",
        help="palette to use in generated convert commands",
    )

    parser.add_argument(
        "--out-dir",
        type=str,
        dest="output_dir",
        default=None,
        help="output directory for generated convert commands",
    )

    parser.add_argument(
        "--format",
        type=str,
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="specify output format",
    )

    return parser.parse_args(normalize_argv(argv)[1:])


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        add_help=True,
        prog="image-go-nord-client",
        formatter_class=RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=VERSION,
        help="show version number and exit",
    )

    parser.add_argument(
        "-i",
        "--img",
        type=str,
        dest="input_path",
        metavar="PATH",
        required=True,
        help="specify input image path",
    )

    parser.add_argument(
        "-b",
        "--blur",
        action="store_true",
        dest="enable_blur",
        default=False,
        help="use blur on the final result",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet_mode",
        default=False,
        help="quiet (no output)",
    )

    parser.add_argument(
        "--format",
        type=str,
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="specify output format",
    )

    parser.add_argument(
        "-o",
        "--out",
        type=str,
        dest="output_path",
        metavar="PATH",
        default=OUTPUT_IMAGE_NAME,
        help="specify output image path",
    )

    parser.add_argument(
        "-na",
        "--no-avg",
        action="store_true",
        dest="disable_avg_pixels",
        default=False,
        help="do not use the average pixels optimization algorithm on conversion",
    )

    parser.add_argument(
        "-pa",
        "--pixels-area",
        type=parse_pixels_area,
        dest="pixels_area",
        metavar="WEIGHT[,HEIGHT]",
        default=[],
        help="specify pixels of the area for average color calculation",
    )

    parser.add_argument(
        "-p",
        "--palette",
        type=str,
        dest="palette",
        metavar="PALETTE",
        default="nord",
        help="specify the palette to use",
    )

    parser.add_argument(
        "-c",
        "--colors",
        type=lambda value: list(value.split(",")),
        dest="colors",
        metavar="COLORS",
        default=[],
        help="specify the colors to use",
    )

    return parser
