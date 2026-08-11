#! /usr/bin/env python3

import json
import logging
import sys
import uuid
from importlib.util import find_spec
from pathlib import Path
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
    parse_batch_arguments,
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

    if result is not None:

        payload["result"] = result

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
            _print_palette_names(palette_names)

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


def _is_rich_available() -> bool:
    return find_spec("rich") is not None


def _print_palette_names(palette_names: list[str]) -> None:
    if not _is_rich_available():
        for palette_name in palette_names:
            print(palette_name)
        return

    from rich.console import Console
    from rich.table import Table

    table = Table(title="Available Palettes")
    table.add_column("Name", style="cyan")
    for palette_name in palette_names:
        table.add_row(palette_name)

    Console().print(table)


def _print_batch_summary(result: dict, *, apply_mode: bool, plan: list[dict]) -> None:
    if not _is_rich_available():
        print("batch apply summary" if apply_mode else "batch dry-run summary")
        print(f"- input_dir: {result['input_dir']}")
        print(f"- output_dir: {result['output_dir']}")
        print(f"- recursive: {result['recursive']}")
        print(f"- palette: {result['palette']}")
        print(f"- images_detected: {result['summary']['images_detected']}")
        if apply_mode:
            print(f"- converted: {result['summary'].get('converted', 0)}")
            print(f"- failed: {result['summary'].get('failed', 0)}")

        if plan:
            print("planned commands:")
            for step in plan:
                print(step["command"])
        return

    from rich.console import Console
    from rich.table import Table

    console = Console()
    summary_table = Table(
        title="Batch Apply Summary" if apply_mode else "Batch Dry-Run Summary"
    )
    summary_table.add_column("Field", style="cyan")
    summary_table.add_column("Value", style="white")
    summary_table.add_row("input_dir", result["input_dir"])
    summary_table.add_row("output_dir", result["output_dir"])
    summary_table.add_row("recursive", str(result["recursive"]))
    summary_table.add_row("palette", result["palette"])
    summary_table.add_row("images_detected", str(result["summary"]["images_detected"]))
    if apply_mode:
        summary_table.add_row("converted", str(result["summary"].get("converted", 0)))
        summary_table.add_row("failed", str(result["summary"].get("failed", 0)))

    console.print(summary_table)
    if plan:
        command_table = Table(title="Planned Commands")
        command_table.add_column("Command", style="green")
        for step in plan:
            command_table.add_row(step["command"])
        console.print(command_table)


def _print_batch_apply_progress_start(total: int) -> None:
    if not _is_rich_available():
        print(f"batch apply progress: 0/{total}")
        return

    from rich.console import Console

    Console().print(f"[bold cyan]batch apply progress:[/bold cyan] 0/{total}")


def _print_batch_apply_progress_step(
    *, index: int, total: int, input_path: str, ok: bool, error: Union[str, None] = None
) -> None:
    short_name = Path(input_path).name
    if not _is_rich_available():
        if ok:
            print(f"[{index}/{total}] ok {short_name}")
        else:
            print(f"[{index}/{total}] failed {short_name}: {error}")
        return

    from rich.console import Console

    console = Console()
    if ok:
        console.print(f"[green][{index}/{total}] ok[/green] {short_name}")
    else:
        console.print(f"[red][{index}/{total}] failed[/red] {short_name}: {error}")


def _is_supported_image_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".webp",
        ".tiff",
        ".gif",
    }


def _build_output_path(input_dir: Path, output_dir: Path, input_file: Path) -> Path:
    relative_parent = input_file.relative_to(input_dir).parent
    return output_dir / relative_parent / f"{input_file.stem}-nord{input_file.suffix.lower()}"


def _run_batch_command(argv: list[str], request_id: str) -> int:
    arguments = parse_batch_arguments(argv)

    input_dir = Path(arguments.input_dir).expanduser().resolve()
    output_dir = (
        Path(arguments.output_dir).expanduser().resolve()
        if arguments.output_dir
        else input_dir
    )

    if not input_dir.exists() or not input_dir.is_dir():
        message = f"Input directory does not exist: {input_dir}"
        if arguments.output_format == "json":
            print(
                json.dumps(
                    _json_response(
                        request_id=request_id,
                        ok=False,
                        error={
                            "code": "E_VALIDATION",
                            "message": message,
                        },
                    ),
                    sort_keys=True,
                )
            )
        else:
            logging.error(message)

        return 2

    walk_iter = input_dir.rglob("*") if arguments.recursive else input_dir.glob("*")
    image_files = sorted(
        [path for path in walk_iter if path.is_file() and _is_supported_image_file(path)]
    )

    plan = []
    for image_file in image_files:
        out_path = _build_output_path(input_dir, output_dir, image_file)
        command_parts = [
            "image-go-nord-client",
            f"--img={image_file}",
            f"--out={out_path}",
            f"--palette={arguments.palette}",
        ]
        if arguments.colors:
            command_parts.append(f"--colors={','.join(arguments.colors)}")
        if arguments.enable_blur:
            command_parts.append("--blur")
        if arguments.disable_avg_pixels:
            command_parts.append("--no-avg")

        plan.append(
            {
                "input": str(image_file),
                "output": str(out_path),
                "command": " ".join(command_parts),
            }
        )

    result = {
        "dry_run": not arguments.apply,
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "palette": arguments.palette,
        "colors": arguments.colors,
        "enable_blur": arguments.enable_blur,
        "disable_avg_pixels": arguments.disable_avg_pixels,
        "recursive": arguments.recursive,
        "summary": {
            "images_detected": len(image_files),
            "planned_conversions": len(plan),
        },
        "plan": plan,
    }

    if arguments.apply:
        if GoNord is None:
            message = (
                "ImageGoNord package is required to run batch apply. "
                "Install dependencies from requirements.txt."
            )
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
                            result=result,
                        ),
                        sort_keys=True,
                    )
                )
            else:
                logging.error(message)

            return 4

        selected_palette = get_palette_dict().get(arguments.palette)
        if selected_palette is None:
            message = f"No palette found with the name {arguments.palette}"
            if arguments.output_format == "json":
                print(
                    json.dumps(
                        _json_response(
                            request_id=request_id,
                            ok=False,
                            error={
                                "code": "E_PALETTE_NOT_FOUND",
                                "message": message,
                            },
                            result=result,
                        ),
                        sort_keys=True,
                    )
                )
            else:
                logging.warning(message)

            return 2

        all_colors_names = sorted([color.name for color in selected_palette.colors])
        if not set(arguments.colors).issubset(set(all_colors_names)):
            message = (
                f"Color {arguments.colors} not found, "
                f"possible colors are {all_colors_names}"
            )
            if arguments.output_format == "json":
                print(
                    json.dumps(
                        _json_response(
                            request_id=request_id,
                            ok=False,
                            error={
                                "code": "E_VALIDATION",
                                "message": message,
                            },
                            result=result,
                        ),
                        sort_keys=True,
                    )
                )
            else:
                logging.warning(message)

            return 2

        output_dir.mkdir(parents=True, exist_ok=True)
        selected_colors = arguments.colors if arguments.colors else all_colors_names
        file_results = []
        if arguments.output_format == "text":
            _print_batch_apply_progress_start(len(plan))

        for index, step in enumerate(plan, start=1):
            file_status = {"input": step["input"], "output": step["output"], "ok": True}
            try:
                go_nord = GoNord()
                if arguments.enable_blur:
                    go_nord.enable_gaussian_blur()
                if arguments.disable_avg_pixels:
                    go_nord.disable_avg_algorithm()

                go_nord.reset_palette()
                go_nord.set_palette_lookup_path(str(selected_palette.path) + "/")
                for color in selected_colors:
                    go_nord.add_file_to_palette(str(color) + ".txt")

                image = go_nord.open_image(step["input"])
                Path(step["output"]).parent.mkdir(parents=True, exist_ok=True)
                go_nord.convert_image(image, save_path=step["output"])
            except Exception as exc:
                file_status["ok"] = False
                file_status["error"] = str(exc)

            file_results.append(file_status)
            if arguments.output_format == "text":
                _print_batch_apply_progress_step(
                    index=index,
                    total=len(plan),
                    input_path=step["input"],
                    ok=file_status["ok"],
                    error=file_status.get("error"),
                )

        converted = len([item for item in file_results if item["ok"]])
        failed = len(file_results) - converted
        result["files"] = file_results
        result["summary"]["converted"] = converted
        result["summary"]["failed"] = failed

        if failed > 0:
            if arguments.output_format == "json":
                print(
                    json.dumps(
                        _json_response(
                            request_id=request_id,
                            ok=False,
                            error={
                                "code": "E_CONVERSION_FAILED",
                                "message": "One or more files failed during batch apply",
                            },
                            result=result,
                        ),
                        sort_keys=True,
                    )
                )
            else:
                print("batch apply completed with failures")
                print(f"- converted: {converted}")
                print(f"- failed: {failed}")

            return 5

    if arguments.output_format == "json":
        print(
            json.dumps(
                _json_response(
                    request_id=request_id,
                    ok=True,
                    result=result,
                ),
                sort_keys=True,
            )
        )
    else:
        _print_batch_summary(result, apply_mode=arguments.apply, plan=plan)

    return 0


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

    if normalized_argv and normalized_argv[0] == "batch":
        return _run_batch_command(argv, request_id)

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
