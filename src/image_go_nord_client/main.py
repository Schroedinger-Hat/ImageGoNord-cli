#! /usr/bin/env python3

import json
import logging
import sys
from typing import Union

try:
    from ImageGoNord import GoNord
except ModuleNotFoundError:
    GoNord = None

from image_go_nord_client import get_palette_dict, parse_arguments

__ALL__ = ["main"]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def _write_json(arguments, payload: dict) -> None:
    if arguments.output_format == "json":
        print(json.dumps(payload, sort_keys=True))


def main(argv: Union[list[str], None] = None):

    if argv is None:
        argv = sys.argv.copy()

    arguments, _ = parse_arguments(argv)
    if arguments.quiet_mode:
        logging.basicConfig(level=logging.CRITICAL)

    if GoNord is None:
        raise RuntimeError(
            "ImageGoNord package is required to run this command. "
            "Install dependencies from requirements.txt."
        )

    go_nord = GoNord()

    image = go_nord.open_image(arguments.input_path)
    logging.info("Loading input image: %s", arguments.input_path)

    output_image_path = arguments.output_path
    logging.info("Set output image name: %s", output_image_path)

    if arguments.enable_blur:
        go_nord.enable_gaussian_blur()
        logging.info("Blur enabled")

    if arguments.disable_avg_pixels:
        go_nord.disable_avg_algorithm()
        logging.info("No average pixels selected for algorithm optimization")

    if arguments.pixels_area:
        w = arguments.pixels_area[0]
        h = arguments.pixels_area[1] if len(arguments.pixels_area) > 1 else w
        go_nord.set_avg_box_data(w=w, h=h)
        logging.info("Set up pixels width area: %s", w)
        logging.info("Set up pixels height area: %s", h)

    if not (selected_palette := get_palette_dict().get(arguments.palette)):
        logging.warning("No palette found with the name %s", arguments.palette)
        _write_json(
            arguments,
            {
                "error": {
                    "code": "E_PALETTE_NOT_FOUND",
                    "message": f"No palette found with the name {arguments.palette}",
                },
                "ok": False,
            },
        )
        return 1

    logging.info("Use palette set: %s", selected_palette.name.capitalize())
    go_nord.reset_palette()
    go_nord.set_palette_lookup_path(str(selected_palette.path) + "/")

    all_colors_names = sorted([color.name for color in selected_palette.colors])
    if not set(arguments.colors).issubset(set(all_colors_names)):
        logging.warning(
            "Color %s not found, possible colors are %s",
            arguments.colors,
            all_colors_names,
        )
        _write_json(
            arguments,
            {
                "error": {
                    "code": "E_VALIDATION",
                    "message": (
                        f"Color {arguments.colors} not found, "
                        f"possible colors are {all_colors_names}"
                    ),
                },
                "ok": False,
            },
        )
        return 1

    selected_colors = arguments.colors if arguments.colors else all_colors_names
    for color in selected_colors:
        go_nord.add_file_to_palette(str(color) + ".txt")

    go_nord.convert_image(image, save_path=output_image_path)

    _write_json(
        arguments,
        {
            "ok": True,
            "result": {
                "colors": selected_colors,
                "input_path": arguments.input_path,
                "output_path": output_image_path,
                "palette": selected_palette.name,
            },
        },
    )

    return 0
