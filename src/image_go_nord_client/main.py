#! /usr/bin/env python3

import logging
import sys

from typing import Union
from ImageGoNord import GoNord

from image_go_nord_client import (
    get_argument_parser,
    get_palette_list,
    get_default_palette,
)

__ALL__ = ["main"]
print(sys.warnoptions)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def main(argv: Union[list[str], None] = None):
    is_palette_selected = False

    if argv is None:
        argv = sys.argv.copy()

    parser = get_argument_parser()
    arguments, uknown_args = parser.parse_known_args(argv.copy())
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

    palettes = get_palette_list()

    is_palette_selected = False
    for arg in uknown_args:
        arg = arg.replace("-", "")
        selected_palette, args_colors = arg.split("=") if "=" in arg else (arg, None)
        selected_colors = args_colors.split(",") if args_colors else []
        for palette in palettes:
            if selected_palette.lower() == palette.name.lower():
                is_palette_selected = True
                go_nord.reset_palette()
                go_nord.set_palette_lookup_path(str(palette.path) + "/")

                if not selected_colors:
                    logging.info("Use all color set: %s", palette.name.capitalize())
                    go_nord.reset_palette()
                    go_nord.set_palette_lookup_path(str(palette.path) + "/")
                    for color in palette.colors:
                        go_nord.add_file_to_palette(str(color.name) + ".txt")

                logging.info("Use palette set: %s", palette.name.capitalize())
                for selected_color in selected_colors:
                    color = next(
                        filter(
                            lambda c: selected_color.lower() in c.name.lower(),
                            palette.colors,
                        )
                    )
                    go_nord.add_file_to_palette(color.name + ".txt")

                    for color in palette.colors:
                        frm_string = (
                            "\t %s \u2713"
                            if color.name.lower() == selected_color.lower()
                            else "\t %s \u2718"
                        )
                        logging.info(frm_string, color.name)

    if not is_palette_selected:
        palette = get_default_palette()
        go_nord.reset_palette()
        logging.warning("No theme specified, use default Nord theme")
        go_nord.set_palette_lookup_path(str(palette.path) + "/")
        for color in palette.colors:
            go_nord.add_file_to_palette(str(color.name) + ".txt")

    go_nord.convert_image(image, save_path=output_image_path)

    return 0
