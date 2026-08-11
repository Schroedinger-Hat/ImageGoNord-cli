# Modern CLI Framework

This repository now includes a modern command-oriented CLI surface.

## Primary Command Style

Use module execution with subcommands:

```shell
python -m image_go_nord_client convert ./image.png
python -m image_go_nord_client palette list
python -m image_go_nord_client palette info nord
python -m image_go_nord_client batch ./images --recursive
python -m image_go_nord_client doctor
python -m image_go_nord_client tui
```

## Compatibility

The previous flag-first style remains supported:

```shell
python src/image_go_nord_client --img=./image.png
python src/image_go_nord_client palette list
```

When `typer` is unavailable, the CLI falls back to legacy parsing automatically.

## Dependencies

Modern framework dependencies:

- `typer`
- `rich`

Install with:

```shell
pip install -r requirements.txt
```
