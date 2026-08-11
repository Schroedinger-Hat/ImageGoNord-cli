# TUI Guide

This document describes the terminal UI direction for ImageGoNord CLI.

## Goals

- Keep an interactive entrypoint for users who prefer guided flows.
- Keep deterministic non-interactive action mode for automation and tests.
- Ensure TUI outcomes map to standard CLI commands.

## Commands

Interactive mode:

```shell
python src/image_go_nord_client tui
```

Non-interactive action mode:

```shell
python src/image_go_nord_client tui --action=<action-name>
```

## Actions

- `convert-image`
- `browse-palettes`
- `batch-conversion` (placeholder)

### convert-image

`convert-image` builds a concrete CLI command from options.

Example:

```shell
python src/image_go_nord_client tui --action=convert-image --img=wall.png --out=wall-nord.png --palette=nord --colors=Aurora,Frost --blur
```

Supported options:

- `--img` (required)
- `--out`
- `--palette`
- `--colors`
- `--blur`
- `--no-avg`

### browse-palettes

Returns available palettes from the installed palette set.

Example:

```shell
python src/image_go_nord_client tui --action=browse-palettes --format=json
```

## Output Contract

TUI action mode follows the CLI output contract:

- text output by default
- JSON output with `--format=json`
- deterministic exit codes
