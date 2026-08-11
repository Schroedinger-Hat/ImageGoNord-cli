from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Optional, Tuple

try:
    from ImageGoNord import GoNord
except ModuleNotFoundError:
    GoNord = None

from image_go_nord_client import get_palette_list, search_palette_by_name

TUI_ACTIONS = {
    "convert-image": {
        "description": "Guided convert flow",
        "label": "Convert Image",
    },
    "browse-palettes": {
        "description": "Show available palettes",
        "label": "Browse Palettes",
    },
    "batch-conversion": {
        "description": "Batch conversion flow (coming soon)",
        "label": "Batch Conversion (coming soon)",
    },
}


def _parse_colors(colors: list[str]) -> list[str]:
    return [color.strip() for color in colors if color and color.strip()]


def convert_image_from_tui(
    *,
    colors: list[str],
    disable_avg_pixels: bool,
    enable_blur: bool,
    input_path: str,
    output_path: str,
    palette: str,
) -> Tuple[int, Dict[str, Any]]:
    if GoNord is None:
        return (
            4,
            {
                "message": "ImageGoNord package is required to run conversion.",
            },
        )

    if not input_path:
        return (2, {"message": "Input image path is required."})

    selected_palette = search_palette_by_name(palette)
    if selected_palette is None:
        return (
            2,
            {
                "message": f"No palette found with the name {palette}",
            },
        )

    input_file = Path(input_path)
    if not input_file.exists() or not input_file.is_file():
        return (
            2,
            {
                "message": f"Input image not found: {input_path}",
            },
        )

    palette_colors = sorted([color.name for color in selected_palette.colors])
    requested_colors = _parse_colors(colors)
    if requested_colors and not set(requested_colors).issubset(set(palette_colors)):
        return (
            2,
            {
                "message": (
                    f"Color {requested_colors} not found, possible colors are {palette_colors}"
                ),
            },
        )

    go_nord = GoNord()

    if enable_blur:
        go_nord.enable_gaussian_blur()

    if disable_avg_pixels:
        go_nord.disable_avg_algorithm()

    selected_colors = requested_colors if requested_colors else palette_colors

    go_nord.reset_palette()
    go_nord.set_palette_lookup_path(str(selected_palette.path) + "/")
    for color in selected_colors:
        go_nord.add_file_to_palette(str(color) + ".txt")

    output_parent = Path(output_path).parent
    if output_parent != Path(""):
        output_parent.mkdir(parents=True, exist_ok=True)

    try:
        image = go_nord.open_image(str(input_file))
        go_nord.convert_image(image, save_path=output_path)
    except Exception:
        return (3, {"message": "Failed to convert image"})

    return (
        0,
        {
            "colors": selected_colors,
            "input_path": str(input_file),
            "message": f"Converted image saved to {output_path}",
            "output_path": output_path,
            "palette": selected_palette.name,
        },
    )


def run_tui_action(
    action: str,
    *,
    colors: list[str],
    disable_avg_pixels: bool,
    enable_blur: bool,
    input_path: Optional[str],
    output_path: str,
    palette: str,
) -> Tuple[int, Dict[str, Any]]:
    if action not in TUI_ACTIONS:
        return (
            2,
            {
                "available_actions": sorted(TUI_ACTIONS.keys()),
                "message": f"Unknown action: {action}",
            },
        )

    if action == "convert-image":
        if input_path is None:
            return (
                2,
                {
                    "message": "convert-image action requires --img=<path>",
                },
            )

        return convert_image_from_tui(
            colors=colors,
            disable_avg_pixels=disable_avg_pixels,
            enable_blur=enable_blur,
            input_path=input_path,
            output_path=output_path,
            palette=palette,
        )

    if action == "browse-palettes":
        palette_names = sorted([palette.name for palette in get_palette_list()])
        return (
            0,
            {
                "count": len(palette_names),
                "palettes": palette_names,
            },
        )

    return (
        0,
        {
            "message": "Batch conversion flow is not implemented yet.",
        },
    )


def launch_tui() -> Tuple[int, str]:
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Horizontal, Vertical
        from textual.widgets import (
            Button,
            Checkbox,
            Footer,
            Header,
            Input,
            RichLog,
            Static,
        )
    except ModuleNotFoundError:
        return (
            4,
            "Textual is not installed. Install it with `pip install textual` to use the TUI.",
        )

    class ImageGoNordTui(App):
        CSS = """
        Screen {
            background: #0b132b;
            color: #f3f4f6;
        }

        #hero {
            background: #1c2541;
            border: tall #3a506b;
            color: #f7f9fb;
            height: 10;
            margin: 1 2 0 2;
            padding: 1 2;
            content-align: left middle;
            text-style: bold;
        }

        #workspace {
            margin: 1 2;
            height: 1fr;
        }

        .panel {
            background: #16213e;
            border: round #4f709c;
            padding: 1;
        }

        #left-panel {
            width: 2fr;
            margin-right: 1;
        }

        #right-panel {
            width: 3fr;
            margin-left: 1;
        }

        .title {
            text-style: bold;
            color: #9ad1ff;
            margin-bottom: 1;
        }

        #status {
            margin-top: 1;
            border: heavy #5bc0be;
            padding: 0 1;
            color: #e9fff8;
            min-height: 3;
        }

        #palette-preview {
            margin-top: 1;
            color: #dbeafe;
            min-height: 7;
        }

        #last-conversion {
            margin-top: 1;
            min-height: 8;
            color: #d6e4ff;
        }

        #action-row {
            margin-top: 1;
            height: auto;
        }

        #palette-row {
            height: auto;
            margin-top: 1;
            margin-bottom: 1;
        }

        #palette-input {
            width: 1fr;
            margin: 0 1;
        }

        #log {
            margin-top: 1;
            height: 1fr;
            border: round #3a506b;
            background: #0f1d35;
        }

        .hint {
            color: #a5b4fc;
            margin-top: 1;
        }
        """

        TITLE = "ImageGoNord CLI"
        SUB_TITLE = "Studio TUI"
        BINDINGS = [
            ("q", "quit", "Quit"),
            ("c", "convert", "Convert"),
            ("r", "reset_form", "Reset"),
            ("p", "show_palettes", "Palettes"),
            ("[", "previous_palette", "Prev Palette"),
            ("]", "next_palette", "Next Palette"),
        ]

        def __init__(self) -> None:
            super().__init__()
            self._palette_names = sorted(
                [palette.name for palette in get_palette_list()]
            )
            self._hero_banner = dedent(
                r"""
                  ___                                 _____       _   _               _
                 |_ _|_ __ ___   __ _  __ _  ___     / ____|___   | \ | | ___  _ __ __| |
                  | || '_ ` _ \ / _` |/ _` |/ _ \   | |  _ / _ \  |  \| |/ _ \| '__/ _` |
                  | || | | | | | (_| | (_| |  __/   | |_| | (_) | | |\  | (_) | | | (_| |
                 |___|_| |_| |_|\__,_|\__, |\___|    \_____\___/  |_| \_|\___/|_|  \__,_|
                                       |___/

                  Fast terminal image stylizer
                """
            ).strip("\n")

        def _default_palette_name(self) -> str:
            if "nord" in self._palette_names:
                return "nord"
            if self._palette_names:
                return self._palette_names[0]
            return "nord"

        def _normalize_palette_name(self, value: str) -> str:
            normalized = value.strip().lower()
            return normalized or self._default_palette_name()

        def _set_palette_name(self, palette_name: str) -> None:
            self.query_one("#palette-input", Input).value = palette_name

        def _selected_palette_name(self) -> str:
            palette_value = self.query_one("#palette-input", Input).value
            return self._normalize_palette_name(palette_value)

        def _selected_palette_index(self) -> int:
            palette_name = self._selected_palette_name()
            if palette_name in self._palette_names:
                return self._palette_names.index(palette_name)
            return self._palette_names.index(self._default_palette_name())

        def _get_palette_preview_text(self, palette_name: str) -> str:
            selected_palette = search_palette_by_name(palette_name)
            if selected_palette is None:
                return "Palette details unavailable"

            colors = sorted([color.name for color in selected_palette.colors])
            color_lines = "\n".join([f"- {name}" for name in colors])
            return (
                f"Palette: {selected_palette.name}\n"
                f"Colors: {len(colors)}\n"
                f"{color_lines}"
            )

        def _build_swatch_text(self, hex_value: str):
            from rich.text import Text

            swatch = Text("  ")
            swatch.stylize(f"on {hex_value}")
            return swatch

        def _build_palette_band(self, hex_values: list[str]):
            from rich.text import Text

            band = Text()
            for hex_value in hex_values:
                segment = Text("        ")
                segment.stylize(f"on {hex_value}")
                band.append(segment)
            return band

        def _read_hex_value(self, color_path: Path) -> str:
            return color_path.read_text(encoding="utf-8").splitlines()[0].strip()

        def _get_palette_preview_renderable(self, palette_name: str):
            from rich.console import Group
            from rich.table import Table
            from rich.text import Text

            selected_palette = search_palette_by_name(palette_name)
            if selected_palette is None:
                return "Palette details unavailable"

            colors = sorted(selected_palette.colors, key=lambda color: color.name.lower())

            summary = Text()
            summary.append(f"Palette: {selected_palette.name}\n", style="bold cyan")
            summary.append(f"Colors: {len(colors)}", style="bold white")

            hex_values = [self._read_hex_value(color.path) for color in colors]
            band = self._build_palette_band(hex_values)

            band_caption = Text(" ".join(hex_values), style="bright_black")

            table = Table.grid(padding=(0, 1))
            table.add_column("Swatch", width=8)
            table.add_column("Name", style="white")
            table.add_column("Hex", style="bright_black")

            for color, hex_value in zip(colors, hex_values):
                table.add_row(self._build_swatch_text(hex_value), color.name, hex_value)

            return Group(summary, Text(""), band, band_caption, Text(""), table)

        def _write_status(self, message: str, *, is_error: bool = False) -> None:
            status_widget = self.query_one("#status", Static)
            prefix = "Error" if is_error else "Status"
            status_widget.update(f"{prefix}: {message}")

            log_widget = self.query_one("#log", RichLog)
            tone = "[red]" if is_error else "[green]"
            log_widget.write(f"{tone}{prefix}[/] {message}")

        def _refresh_palette_preview(self) -> None:
            palette_name = self._selected_palette_name()
            preview = self._get_palette_preview_renderable(palette_name)
            self.query_one("#palette-preview", Static).update(preview)

        def _update_last_conversion(self, *, status: int | None = None, result: dict | None = None) -> None:
            from rich.console import Group
            from rich.text import Text

            if status is None or result is None:
                empty_state = Text()
                empty_state.append("Last run: ", style="bold white")
                empty_state.append("idle", style="bold black on #7b8794")
                empty_state.append(
                    "\nRun a conversion to see the latest result summary.",
                    style="bright_black",
                )
                self.query_one("#last-conversion", Static).update(empty_state)
                return

            badge = Text()
            badge.append("Last run: ", style="bold white")
            if status == 0:
                badge.append("success", style="bold black on #a3be8c")
            else:
                badge.append(f"error ({status})", style="bold white on #bf616a")

            details = Text()
            if status == 0:
                details.append(f"\nInput: {result.get('input_path', '-')}", style="white")
                details.append(f"\nOutput: {result.get('output_path', '-')}", style="white")
                details.append(f"\nPalette: {result.get('palette', '-')}", style="cyan")
                details.append(
                    f"\nColors: {', '.join(result.get('colors', [])) or '-'}",
                    style="bright_white",
                )
            else:
                details.append(
                    f"\nMessage: {result.get('message', '-')}",
                    style="white",
                )

            self.query_one("#last-conversion", Static).update(Group(badge, details))

        def _cycle_palette(self, offset: int) -> None:
            if not self._palette_names:
                self._write_status("No palettes available", is_error=True)
                return

            next_index = (self._selected_palette_index() + offset) % len(self._palette_names)
            next_palette = self._palette_names[next_index]
            self._set_palette_name(next_palette)
            self._refresh_palette_preview()
            self._write_status(f"Palette selected: {next_palette}")

        def _run_conversion(self) -> None:
            input_path = self.query_one("#input-path", Input).value.strip()
            output_path = self.query_one("#output-path", Input).value.strip() or "nord.png"
            palette = self._selected_palette_name()
            raw_colors = self.query_one("#colors-input", Input).value
            colors = [value.strip() for value in raw_colors.split(",") if value.strip()]
            blur = self.query_one("#blur-check", Checkbox).value
            no_avg = self.query_one("#no-avg-check", Checkbox).value

            self._write_status("Running conversion...")
            status, result = convert_image_from_tui(
                colors=colors,
                disable_avg_pixels=no_avg,
                enable_blur=blur,
                input_path=input_path,
                output_path=output_path,
                palette=palette,
            )
            self._update_last_conversion(status=status, result=result)
            if status == 0:
                self._write_status(result["message"])
            else:
                self._write_status(f"({status}) {result['message']}", is_error=True)

        def action_convert(self) -> None:
            self._run_conversion()

        def action_previous_palette(self) -> None:
            self._cycle_palette(-1)

        def action_next_palette(self) -> None:
            self._cycle_palette(1)

        def action_reset_form(self) -> None:
            self.query_one("#input-path", Input).value = ""
            self.query_one("#output-path", Input).value = "nord.png"
            self.query_one("#colors-input", Input).value = ""
            self.query_one("#blur-check", Checkbox).value = False
            self.query_one("#no-avg-check", Checkbox).value = False
            self._set_palette_name(self._default_palette_name())
            self._refresh_palette_preview()
            self._write_status("Form reset")

        def action_show_palettes(self) -> None:
            names = ", ".join(self._palette_names) if self._palette_names else "none"
            self._write_status(f"Available palettes: {names}")

        def action_quit(self) -> None:
            self.exit()

        def compose(self) -> ComposeResult:
            default_palette = self._default_palette_name()

            yield Header()
            yield Static(self._hero_banner, id="hero")
            with Horizontal(id="workspace"):
                with Vertical(id="left-panel", classes="panel"):
                    yield Static("Conversion Controls", classes="title")
                    yield Input(placeholder="Input image path", id="input-path")
                    yield Input(value="nord.png", id="output-path")
                    yield Static("Palette", classes="title")
                    with Horizontal(id="palette-row"):
                        yield Button("<", id="prev-palette-button")
                        yield Input(value=default_palette, id="palette-input")
                        yield Button(">", id="next-palette-button")
                    yield Input(
                        placeholder="Optional colors (comma separated)",
                        id="colors-input",
                    )
                    yield Checkbox("Enable blur", value=False, id="blur-check")
                    yield Checkbox(
                        "Disable average algorithm",
                        value=False,
                        id="no-avg-check",
                    )
                    with Horizontal(id="action-row"):
                        yield Button("Convert", id="convert-button", variant="primary")
                        yield Button("Reset", id="reset-button")
                        yield Button("Palettes", id="palettes-button")
                    yield Static("Status: Ready", id="status")

                with Vertical(id="right-panel", classes="panel"):
                    yield Static("Palette Preview", classes="title")
                    yield Static("", id="palette-preview")
                    yield Static("Last Conversion", classes="title")
                    yield Static("", id="last-conversion")
                    yield Static("Activity", classes="title")
                    yield RichLog(id="log", wrap=True, highlight=True, markup=True)
                    yield Static(
                        "Shortcuts: [ prev | ] next | c convert | r reset | p palettes | q quit",
                        classes="hint",
                    )
            yield Footer()

        def on_mount(self) -> None:
            self._refresh_palette_preview()
            self._update_last_conversion()
            self._write_status("Ready")

        def on_input_submitted(self, event: Input.Submitted) -> None:
            if event.input.id != "palette-input":
                return

            palette_name = self._selected_palette_name()
            self._set_palette_name(palette_name)
            self._refresh_palette_preview()
            if search_palette_by_name(palette_name) is None:
                self._write_status(
                    f"Unknown palette: {palette_name}. Press p for available palettes.",
                    is_error=True,
                )
                return
            self._write_status(f"Palette selected: {palette_name}")

        def on_input_changed(self, event: Input.Changed) -> None:
            if event.input.id != "palette-input":
                return
            self._refresh_palette_preview()

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "prev-palette-button":
                self.action_previous_palette()
                return

            if event.button.id == "next-palette-button":
                self.action_next_palette()
                return

            if event.button.id == "reset-button":
                self.action_reset_form()
                return

            if event.button.id == "palettes-button":
                self.action_show_palettes()
                return

            if event.button.id != "convert-button":
                return
            self._run_conversion()

    app = ImageGoNordTui()
    app.run()
    return 0, "TUI session closed"
