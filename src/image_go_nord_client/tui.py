from typing import Any, Dict, Optional, Tuple

from image_go_nord_client import get_palette_list

TUI_ACTIONS = {
    "convert-image": {
        "description": "Guided convert flow (preview)",
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

        command_parts = [
            "image-go-nord-client",
            f"--img={input_path}",
            f"--out={output_path}",
            f"--palette={palette}",
        ]
        if colors:
            command_parts.append(f"--colors={','.join(colors)}")
        if enable_blur:
            command_parts.append("--blur")
        if disable_avg_pixels:
            command_parts.append("--no-avg")

        next_command = " ".join(command_parts)
        return (
            0,
            {
                "message": "Generated convert command from TUI action.",
                "next_command": next_command,
            },
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
        from textual.widgets import Footer, Header, ListItem, ListView, Static
    except ModuleNotFoundError:
        return (
            4,
            "Textual is not installed. Install it with `pip install textual` to use the TUI.",
        )

    class ImageGoNordTui(App):
        TITLE = "ImageGoNord CLI"
        SUB_TITLE = "Interactive mode (spike)"

        def compose(self) -> ComposeResult:
            yield Header()
            yield Static("Choose an action", id="title")
            yield ListView(
                ListItem(Static(TUI_ACTIONS["convert-image"]["label"])),
                ListItem(Static(TUI_ACTIONS["browse-palettes"]["label"])),
                ListItem(Static(TUI_ACTIONS["batch-conversion"]["label"])),
                id="menu",
            )
            yield Static("Press q to quit", id="hint")
            yield Footer()

    app = ImageGoNordTui()
    app.run()
    return 0, "TUI session closed"
