from typing import Tuple


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
                ListItem(Static("Convert Image")),
                ListItem(Static("Browse Palettes")),
                ListItem(Static("Batch Conversion (coming soon)")),
                id="menu",
            )
            yield Static("Press q to quit", id="hint")
            yield Footer()

    app = ImageGoNordTui()
    app.run()
    return 0, "TUI session closed"
