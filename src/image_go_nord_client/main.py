#! /usr/bin/env python3

import logging
import sys
from typing import Union

from ImageGoNord import GoNord

from image_go_nord_client import get_argument_parser, get_palette_dict

__ALL__ = ["main"]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def main(argv: Union[list[str], None] = None):

    if argv is None:
        argv = sys.argv.copy()

    parser = get_argument_parser()
    arguments, _ = parser.parse_known_args(argv.copy())
    if arguments.quiet_mode:
        logging.basicConfig(level=logging.CRITICAL)

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
        return 1

    selected_colors = arguments.colors if arguments.colors else all_colors_names
    for color in selected_colors:
        go_nord.add_file_to_palette(str(color) + ".txt")

    go_nord.convert_image(image, save_path=output_image_path)

    return 0
