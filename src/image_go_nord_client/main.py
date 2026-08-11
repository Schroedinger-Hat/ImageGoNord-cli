#! /usr/bin/env python3

import json
import logging
import sys
import uuid
from typing import Union

try:
    from ImageGoNord import GoNord
except ModuleNotFoundError:
    GoNord = None

from image_go_nord_client import get_palette_dict, parse_arguments

__ALL__ = ["main"]
CONTRACT_VERSION = "3.0"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def _write_json(arguments, payload: dict) -> None:
    if arguments.output_format == "json":
        print(json.dumps(payload, sort_keys=True))


def _json_response(
    *,
    request_id: str,
    ok: bool,
    result: Union[dict, None] = None,
    error: Union[dict, None] = None,
) -> dict:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "ok": ok,
        "request_id": request_id,
    }

    if ok:
        payload["result"] = result or {}
    else:
        payload["error"] = error or {}

    return payload


def main(argv: Union[list[str], None] = None):

    if argv is None:
        argv = sys.argv.copy()

    arguments, _ = parse_arguments(argv)
    request_id = str(uuid.uuid4())
    if arguments.quiet_mode:
        logging.basicConfig(level=logging.CRITICAL)

    if GoNord is None:
        message = (
            "ImageGoNord package is required to run this command. "
            "Install dependencies from requirements.txt."
        )
        logging.error(message)
        _write_json(
            arguments,
            _json_response(
                request_id=request_id,
                ok=False,
                error={
                    "code": "E_INTERNAL",
                    "message": message,
                },
            ),
        )
        return 4

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
            _json_response(
                request_id=request_id,
                ok=False,
                error={
                    "code": "E_PALETTE_NOT_FOUND",
                    "message": f"No palette found with the name {arguments.palette}",
                },
            ),
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
            _json_response(
                request_id=request_id,
                ok=False,
                error={
                    "code": "E_VALIDATION",
                    "message": (
                        f"Color {arguments.colors} not found, "
                        f"possible colors are {all_colors_names}"
                    ),
                },
            ),
        )
        return 1

    selected_colors = arguments.colors if arguments.colors else all_colors_names
    for color in selected_colors:
        go_nord.add_file_to_palette(str(color) + ".txt")

    try:
        go_nord.convert_image(image, save_path=output_image_path)
    except Exception:
        message = "Failed to convert image"
        logging.exception(message)
        _write_json(
            arguments,
            _json_response(
                request_id=request_id,
                ok=False,
                error={
                    "code": "E_CONVERSION_FAILED",
                    "message": message,
                },
            ),
        )
        return 3

    _write_json(
        arguments,
        _json_response(
            request_id=request_id,
            ok=True,
            result={
                "colors": selected_colors,
                "input_path": arguments.input_path,
                "output_path": output_image_path,
                "palette": selected_palette.name,
            },
        ),
    )

    return 0
