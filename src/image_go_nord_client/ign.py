import sys
from importlib.util import find_spec
from typing import Optional

from image_go_nord_client.main import main as legacy_main


def _is_typer_available() -> bool:
    return find_spec("typer") is not None and find_spec("click") is not None


def _looks_like_legacy_argv(argv: list[str]) -> bool:
    if not argv:
        return False

    if argv[0].startswith("-"):
        return True

    if argv[0] == "convert" and any(arg.startswith("--img") or arg == "-i" for arg in argv):
        return True

    return False


def _run_typer_app(argv: list[str]) -> int:
    import typer

    app = typer.Typer(
        help="Modern ImageGoNord CLI",
        no_args_is_help=True,
        add_completion=False,
    )

    palette_app = typer.Typer(help="Palette management")
    app.add_typer(palette_app, name="palette")

    @app.command("convert")
    def convert_command(
        image: str = typer.Argument(..., help="Input image path"),
        out: str = typer.Option("nord.png", "--out", help="Output image path"),
        palette: str = typer.Option("nord", "--palette", help="Palette to use"),
        colors: str = typer.Option("", "--colors", help="Comma-separated colors"),
        blur: bool = typer.Option(False, "--blur", help="Enable blur"),
        no_avg: bool = typer.Option(False, "--no-avg", help="Disable avg optimization"),
        output_format: str = typer.Option("text", "--format", help="Output format"),
    ) -> None:
        legacy_argv = [
            "image-go-nord-client",
            f"--img={image}",
            f"--out={out}",
            f"--palette={palette}",
            f"--format={output_format}",
        ]
        if colors:
            legacy_argv.append(f"--colors={colors}")
        if blur:
            legacy_argv.append("--blur")
        if no_avg:
            legacy_argv.append("--no-avg")

        raise typer.Exit(code=legacy_main(legacy_argv))

    @app.command("batch")
    def batch_command(
        input_dir: str = typer.Argument(..., help="Input directory"),
        recursive: bool = typer.Option(False, "--recursive", help="Scan recursively"),
        apply_mode: bool = typer.Option(False, "--apply", help="Execute conversions"),
        out_dir: Optional[str] = typer.Option(None, "--out-dir", help="Output directory"),
        palette: str = typer.Option("nord", "--palette", help="Palette to use"),
        colors: str = typer.Option("", "--colors", help="Comma-separated colors"),
        blur: bool = typer.Option(False, "--blur", help="Enable blur"),
        no_avg: bool = typer.Option(False, "--no-avg", help="Disable avg optimization"),
        output_format: str = typer.Option("text", "--format", help="Output format"),
    ) -> None:
        legacy_argv = [
            "image-go-nord-client",
            "batch",
            input_dir,
            f"--palette={palette}",
            f"--format={output_format}",
        ]
        if recursive:
            legacy_argv.append("--recursive")
        if apply_mode:
            legacy_argv.append("--apply")
        if out_dir:
            legacy_argv.append(f"--out-dir={out_dir}")
        if colors:
            legacy_argv.append(f"--colors={colors}")
        if blur:
            legacy_argv.append("--blur")
        if no_avg:
            legacy_argv.append("--no-avg")

        raise typer.Exit(code=legacy_main(legacy_argv))

    @palette_app.command("list")
    def palette_list_command(
        output_format: str = typer.Option("text", "--format", help="Output format"),
    ) -> None:
        raise typer.Exit(
            code=legacy_main(
                [
                    "image-go-nord-client",
                    "palette",
                    f"--format={output_format}",
                    "list",
                ]
            )
        )

    @palette_app.command("info")
    def palette_info_command(
        name: str = typer.Argument(..., help="Palette name"),
        output_format: str = typer.Option("text", "--format", help="Output format"),
    ) -> None:
        raise typer.Exit(
            code=legacy_main(
                [
                    "image-go-nord-client",
                    "palette",
                    "info",
                    name,
                    f"--format={output_format}",
                ]
            )
        )

    @app.command("doctor")
    def doctor_command(
        output_format: str = typer.Option("text", "--format", help="Output format"),
    ) -> None:
        raise typer.Exit(
            code=legacy_main(
                ["image-go-nord-client", "doctor", f"--format={output_format}"]
            )
        )

    @app.command("tui")
    def tui_command(
        action: Optional[str] = typer.Option(None, "--action", help="TUI action"),
        image: Optional[str] = typer.Option(None, "--img", help="Input image path"),
        out: str = typer.Option("nord.png", "--out", help="Output image path"),
        palette: str = typer.Option("nord", "--palette", help="Palette to use"),
        colors: str = typer.Option("", "--colors", help="Comma-separated colors"),
        blur: bool = typer.Option(False, "--blur", help="Enable blur"),
        no_avg: bool = typer.Option(False, "--no-avg", help="Disable avg optimization"),
        output_format: str = typer.Option("text", "--format", help="Output format"),
    ) -> None:
        legacy_argv = ["image-go-nord-client", "tui", f"--format={output_format}"]
        if action:
            legacy_argv.append(f"--action={action}")
        if image:
            legacy_argv.append(f"--img={image}")
        legacy_argv.append(f"--out={out}")
        legacy_argv.append(f"--palette={palette}")
        if colors:
            legacy_argv.append(f"--colors={colors}")
        if blur:
            legacy_argv.append("--blur")
        if no_avg:
            legacy_argv.append("--no-avg")

        raise typer.Exit(code=legacy_main(legacy_argv))

    app(prog_name="ign", args=argv, standalone_mode=False)
    return 0


def run(argv: Optional[list[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if _looks_like_legacy_argv(args):
        return legacy_main(["image-go-nord-client", *args])

    if not _is_typer_available():
        return legacy_main(["image-go-nord-client", *args])

    return _run_typer_app(args)
