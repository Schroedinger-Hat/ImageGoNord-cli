# ImageGoNord client

ImageGoNord is a tool that can convert your rgb images to nordtheme palette.

You can find more information here: [ImageGoNord](https://github.com/schroedinger-Hat/ImageGoNord)

This repository is a client, written in python, that can convert any sort of image into a nordtheme palette image.

## Getting Started
Include any essential instructions for:

- Getting it:
  ```
  git clone https://github.com/schroedinger-Hat/ImageGoNord-cli
  ```

- Install dependencies
  ```shell
  pip install -r requirements.txt
  ```

- Install with Poetry
  ```shell
  poetry install
  ```

- Local development commands with Poetry
  ```shell
  poetry run ign
  poetry run ign --help
  poetry run image-go-nord-client --img='<path_to_your_image>'
  poetry run python -m unittest tests.unit.mocked.test_client_batch_behavior
  ```
  Running `poetry run ign` without parameters opens the interactive terminal UI.
- Running it
  ```shell
  export PYTHONPATH=$PYTHONPATH:$PWD/src:$PWD/tests
  python src/image_go_nord_client --img='<path_to_your_image>'
  ```
  Or if you prefer
  ```shell
  export PYTHONPATH=$PYTHONPATH:$PWD/src:$PWD/tests
  cd src
  python image_go_nord_client --img='<path_to_your_image>'
  ```

## Modern CLI Framework (v1.x)

The CLI now exposes a modern command surface using `ign` command patterns:

```shell
python -m image_go_nord_client convert ./image.png
python -m image_go_nord_client palette list
python -m image_go_nord_client batch ./images --recursive
python -m image_go_nord_client doctor
```

Compatibility behavior:

- Existing flag-first usage is still supported (example: `--img=...`).
- If `typer` is not installed, the client automatically falls back to the legacy parser.
- Modern `convert` positional syntax is translated to legacy flags when Typer is unavailable.

Shell completion (when Typer is installed):

```shell
python -m image_go_nord_client --install-completion
python -m image_go_nord_client --show-completion
```

Text-mode UI enhancement:

- When `rich` is installed, `palette list` and `batch` text outputs are rendered as tables.
- Without `rich`, the CLI keeps the existing plain-text output format.
- `batch --apply` now shows per-file progress in text mode (for example `[1/5] ok file.png`).
- With `rich`, `batch --apply` uses a progress bar and keeps per-file updates concise.

The algorithm can take some time (we are working on improving it), you can find the result with the name *nord.png*.

You can define some more configuration and use different palettes, find more using:

```shell
python src/image_go_nord_client --img='<path_to_your_image>'
```

## CLI Contract

### Output Formats

- Default output is human-readable logs.
- Use `--format=json` for machine-readable output.

Example:

```shell
python src/image_go_nord_client --img='<path_to_your_image>' --format=json
```

Successful JSON output example:

```json
{
  "contract_version": "3.0",
  "ok": true,
  "request_id": "8d7ed9d6-e10d-4f8e-99ea-d31c8f07f34b",
  "result": {
    "colors": ["Aurora", "Frost", "PolarNight", "SnowStorm"],
    "input_path": "input.png",
    "output_path": "nord.png",
    "palette": "nord"
  }
}
```

Validation error JSON output example:

```json
{
  "contract_version": "3.0",
  "ok": false,
  "request_id": "5939121b-fb7d-4be8-8ef2-8d0eb3ebd5ec",
  "error": {
    "code": "E_VALIDATION",
    "message": "Color ['NOT_FOUND'] not found, possible colors are ['Aurora', 'Frost', 'PolarNight', 'SnowStorm']"
  }
}
```

### Exit Codes

- `0`: success
- `2`: invalid input or validation error (for example palette or color selection)
- `3`: conversion failure
- `4`: dependency or environment failure
- `5`: internal unexpected failure (reserved)

### Palette Commands

List installed palettes:

```shell
python src/image_go_nord_client palette list
```

List installed palettes in JSON:

```shell
python src/image_go_nord_client palette --format=json list
```

Show details for a specific palette:

```shell
python src/image_go_nord_client palette info nord
```

Show palette details in JSON:

```shell
python src/image_go_nord_client palette info nord --format=json
```

### Terminal UI (TUI)

Start interactive mode:

```shell
python src/image_go_nord_client tui
```

TUI status as JSON envelope:

```shell
python src/image_go_nord_client tui --format=json
```

Run a TUI action without opening the full-screen interface:

```shell
python src/image_go_nord_client tui --action=browse-palettes --format=json
```

Run conversion directly from TUI action options:

```shell
python src/image_go_nord_client tui --action=convert-image --img=wall.png --out=wall-nord.png --palette=nord --colors=Aurora,Frost --blur
```

With Poetry:

```shell
poetry run ign tui
```

Available actions:

- `convert-image`
- `browse-palettes`
- `batch-conversion`

Convert action options:

- `--img` (required)
- `--out`
- `--palette`
- `--colors`
- `--blur`
- `--no-avg`

The TUI command is powered by [Textual](https://textual.textualize.io/) and supports:

- selecting a palette from an interactive dropdown
- optional color filtering, blur, and no-avg flags
- direct image conversion from the terminal UI
- palette browsing from the same screen

If Textual is not installed, the command returns exit code `4` and a dependency error.

When installing through Poetry, Textual is installed automatically because it is part of the default project dependencies.

Install Textual:

```shell
pip install textual
```

### Diagnostics (Doctor)

Run environment diagnostics:

```shell
python src/image_go_nord_client doctor
```

Run diagnostics in JSON mode:

```shell
python src/image_go_nord_client doctor --format=json
```

Doctor currently validates:

- Python runtime
- ImageGoNord dependency availability
- Palette inventory availability
- Textual dependency availability (optional)

Doctor text output now includes a compact summary and a structured checks report.

### Batch Dry-Run

Generate a batch conversion plan from a directory:

```shell
python src/image_go_nord_client batch ./images
```

Generate plan recursively and print JSON output:

```shell
python src/image_go_nord_client batch ./images --recursive --format=json
```

Set output directory and palette in the generated plan:

```shell
python src/image_go_nord_client batch ./images --out-dir ./converted --palette monokai
```

Current `batch` behavior is a dry-run planner only. It does not convert files yet.

When scanning recursively, output paths preserve the input directory structure.
For example `images/a/b/wall.png` becomes `converted/a/b/wall-nord.png` when using `--out-dir ./converted`.

Execute conversion for the detected files:

```shell
python src/image_go_nord_client batch ./images --apply
```

Execute conversion with explicit conversion options:

```shell
python src/image_go_nord_client batch ./images --apply --palette monokai --colors=Accent,Base --blur --no-avg
```

When `--apply` is used, the command returns:

- `0` when all files are converted successfully
- `5` when one or more files fail to convert (with per-file details in JSON mode)

### Contributing
- Follow the contributor guidelines
- Follow the code style / requirements
- Format for commit messages

## Packaging and PyPI

This repository is now Poetry-managed for packaging and release.

Build distributions:

```shell
poetry build
```

Install locally from wheel:

```shell
pip install dist/image_go_nord_client-1.0.0-py3-none-any.whl
```

Publish to PyPI:

```shell
poetry config pypi-token.pypi <your-token>
poetry publish --build
```

If `poetry install` fails while building Pillow, update the lock and install again:

```shell
poetry lock
poetry install
```

If your machine has multiple Python versions, prefer Python 3.12 or 3.13 for local dev:

```shell
poetry env use 3.13
poetry install
```

After installation, command entrypoints are:

- `image-go-nord-client`
- `ign`


# Authors
[TheJoin95](https://github.com/TheJoin95) & [Wabri](https://github.com/Wabri)

**NOTE**: we are not (yet) affiliated with the Nordtheme or [Arcticicestudio](https://github.com/arcticicestudio).

# Credits

[Nordtheme](https://www.nordtheme.com/)
