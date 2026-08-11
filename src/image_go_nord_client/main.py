#! /usr/bin/env python3

import json
import logging
import sys
import uuid
from importlib.util import find_spec
from typing import Union

try:
    from ImageGoNord import GoNord
except ModuleNotFoundError:
    GoNord = None

from image_go_nord_client import (
    get_palette_dict,
    get_palette_list,
    normalize_argv,
    parse_arguments,
    parse_doctor_arguments,
    parse_palette_arguments,
    parse_tui_arguments,
    search_palette_by_name,
)
from image_go_nord_client.tui import launch_tui as _launch_tui
from image_go_nord_client.tui import run_tui_action as _run_tui_action_helper

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


def _run_palette_command(argv: list[str], request_id: str) -> int:
    arguments = parse_palette_arguments(argv)

    if arguments.palette_action == "list":
        palette_names = sorted([palette.name for palette in get_palette_list()])

        if arguments.output_format == "json":
            print(
                json.dumps(
                    _json_response(
                        request_id=request_id,
                        ok=True,
                        result={"palettes": palette_names},
                    ),
                    sort_keys=True,
                )
            )
        else:
            for palette_name in palette_names:
                print(palette_name)

        return 0

    selected_palette = search_palette_by_name(arguments.name)
    if selected_palette is None:
        if arguments.output_format == "json":
            print(
                json.dumps(
                    _json_response(
                        request_id=request_id,
                        ok=False,
                        error={
                            "code": "E_PALETTE_NOT_FOUND",
                            "message": (
                                f"No palette found with the name {arguments.name}"
                            ),
                        },
                    ),
                    sort_keys=True,
                )
            )
        else:
            logging.warning("No palette found with the name %s", arguments.name)

        return 2

    colors = sorted([color.name for color in selected_palette.colors])
    if arguments.output_format == "json":
        print(
            json.dumps(
                _json_response(
                    request_id=request_id,
                    ok=True,
                    result={
                        "colors": colors,
                        "name": selected_palette.name,
                        "path": str(selected_palette.path),
                    },
                ),
                sort_keys=True,
            )
        )
    else:
        print(f"name: {selected_palette.name}")
        print(f"path: {selected_palette.path}")
        print(f"colors: {', '.join(colors)}")

    return 0


def _run_tui_command(argv: list[str], request_id: str) -> int:
    arguments = parse_tui_arguments(argv)

    if arguments.action is not None:
        status, result = _run_tui_action_helper(
            arguments.action,
            colors=arguments.colors,
            disable_avg_pixels=arguments.disable_avg_pixels,
            enable_blur=arguments.enable_blur,
            input_path=arguments.input_path,
            output_path=arguments.output_path,
            palette=arguments.palette,
        )
        if arguments.output_format == "json":
            if status == 0:
                print(
                    json.dumps(
                        _json_response(
                            request_id=request_id,
                            ok=True,
                            result={
                                "action": arguments.action,
                                "mode": "tui-action",
                                **result,
                            },
                        ),
                        sort_keys=True,
                    )
                )
            else:
                print(
                    json.dumps(
                        _json_response(
                            request_id=request_id,
                            ok=False,
                            error={
                                "code": "E_VALIDATION",
                                "message": result["message"],
                            },
                        ),
                        sort_keys=True,
                    )
                )
        else:
            print(result["message"])
            if "next_command" in result:
                print(result["next_command"])

        return status

    status, message = _launch_tui()

    if status == 0:
        if arguments.output_format == "json":
            print(
                json.dumps(
                    _json_response(
                        request_id=request_id,
                        ok=True,
                        result={
                            "message": message,
                            "mode": "tui",
                        },
                    ),
                    sort_keys=True,
                )
            )
        elif message:
            print(message)

        return 0

    if arguments.output_format == "json":
        print(
            json.dumps(
                _json_response(
                    request_id=request_id,
                    ok=False,
                    error={
                        "code": "E_DEPENDENCY",
                        "message": message,
                    },
                ),
                sort_keys=True,
            )
        )
    else:
        logging.error(message)

    return status


def _is_textual_available() -> bool:
    return find_spec("textual") is not None


def _run_doctor_command(argv: list[str], request_id: str) -> int:
    arguments = parse_doctor_arguments(argv)

    checks = []
    checks.append(
        {
            "hint": "Use Python 3.10+ for best compatibility.",
            "message": f"Python {sys.version.split()[0]}",
            "name": "python",
            "status": "pass",
        }
    )

    go_nord_available = GoNord is not None
    checks.append(
        {
            "hint": "Install dependencies with `pip install -r requirements.txt`.",
            "message": "ImageGoNord dependency available"
            if go_nord_available
            else "ImageGoNord dependency missing",
            "name": "image_go_nord",
            "status": "pass" if go_nord_available else "fail",
        }
    )

    palette_count = len(get_palette_list())
    checks.append(
        {
            "hint": "Ensure palette files are present in src/image_go_nord_client/palettes.",
            "message": f"Detected {palette_count} palettes",
            "name": "palettes",
            "status": "pass" if palette_count > 0 else "fail",
        }
    )

    textual_available = _is_textual_available()
    checks.append(
        {
            "hint": "Install optional dependency with `pip install textual`.",
            "message": "Textual dependency available"
            if textual_available
            else "Textual dependency missing (optional)",
            "name": "textual",
            "status": "pass" if textual_available else "warn",
        }
    )

    failed_checks = [check for check in checks if check["status"] == "fail"]
    warning_checks = [check for check in checks if check["status"] == "warn"]

    summary = {
        "failed": len(failed_checks),
        "passed": len([check for check in checks if check["status"] == "pass"]),
        "warnings": len(warning_checks),
    }

    if failed_checks:
        error_code = (
            "E_DEPENDENCY"
            if any(check["name"] == "image_go_nord" for check in failed_checks)
            else "E_VALIDATION"
        )
        status = 4 if error_code == "E_DEPENDENCY" else 2

        if arguments.output_format == "json":
            print(
                json.dumps(
                    _json_response(
                        request_id=request_id,
                        ok=False,
                        error={
                            "code": error_code,
                            "message": "Doctor checks failed",
                        },
                        result={"checks": checks, "summary": summary},
                    ),
                    sort_keys=True,
                )
            )
        else:
            print("doctor checks failed")
            for check in checks:
                print(f"- {check['name']}: {check['status']} ({check['message']})")

        return status

    if arguments.output_format == "json":
        print(
            json.dumps(
                _json_response(
                    request_id=request_id,
                    ok=True,
                    result={"checks": checks, "summary": summary},
                ),
                sort_keys=True,
            )
        )
    else:
        print("doctor checks passed")
        for check in checks:
            print(f"- {check['name']}: {check['status']} ({check['message']})")

    return 0


def main(argv: Union[list[str], None] = None):

    if argv is None:
        argv = sys.argv.copy()

    request_id = str(uuid.uuid4())

    normalized_argv = normalize_argv(argv)
    if normalized_argv and normalized_argv[0] == "palette":
        return _run_palette_command(argv, request_id)

    if normalized_argv and normalized_argv[0] == "tui":
        return _run_tui_command(argv, request_id)

    if normalized_argv and normalized_argv[0] == "doctor":
        return _run_doctor_command(argv, request_id)

    arguments, _ = parse_arguments(argv)
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
        return 2

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
        return 2

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
