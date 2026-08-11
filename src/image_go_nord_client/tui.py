from pathlib import Path
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
        from textual.containers import Vertical
        from textual.widgets import Button, Checkbox, Footer, Header, Input, Select, Static
    except ModuleNotFoundError:
        return (
            4,
            "Textual is not installed. Install it with `pip install textual` to use the TUI.",
        )

    class ImageGoNordTui(App):
        TITLE = "ImageGoNord CLI"
        SUB_TITLE = "Interactive conversion"
        BINDINGS = [("q", "quit", "Quit")]

        def __init__(self) -> None:
            super().__init__()
            self._palette_names = sorted(
                [palette.name for palette in get_palette_list()]
            )

        def action_quit(self) -> None:
            self.exit()

        def compose(self) -> ComposeResult:
            palette_options = [(name, name) for name in self._palette_names]
            default_palette = self._palette_names[0] if self._palette_names else "nord"

            yield Header()
            with Vertical(id="layout"):
                yield Static("ImageGoNord Terminal UI", id="title")
                yield Static("Fill the fields and run conversion", id="hint")
                yield Input(placeholder="Input image path", id="input-path")
                yield Input(value="nord.png", id="output-path")
                yield Select(
                    palette_options,
                    value=default_palette,
                    id="palette-select",
                    allow_blank=False,
                    prompt="Choose a palette",
                )
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
                yield Button("Convert", id="convert-button", variant="primary")
                yield Button("Show palettes", id="palettes-button")
                yield Static("Ready", id="status")
            yield Footer()

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "palettes-button":
                names = ", ".join(self._palette_names) if self._palette_names else "none"
                self.query_one("#status", Static).update(f"Available palettes: {names}")
                return

            if event.button.id != "convert-button":
                return

            input_path = self.query_one("#input-path", Input).value.strip()
            output_path = self.query_one("#output-path", Input).value.strip() or "nord.png"
            palette_select = self.query_one("#palette-select", Select)
            palette = str(palette_select.value) if palette_select.value else "nord"
            raw_colors = self.query_one("#colors-input", Input).value
            colors = [value.strip() for value in raw_colors.split(",") if value.strip()]
            blur = self.query_one("#blur-check", Checkbox).value
            no_avg = self.query_one("#no-avg-check", Checkbox).value

            status, result = convert_image_from_tui(
                colors=colors,
                disable_avg_pixels=no_avg,
                enable_blur=blur,
                input_path=input_path,
                output_path=output_path,
                palette=palette,
            )
            if status == 0:
                self.query_one("#status", Static).update(result["message"])
            else:
                self.query_one("#status", Static).update(
                    f"Error ({status}): {result['message']}"
                )

    app = ImageGoNordTui()
    app.run()
    return 0, "TUI session closed"
