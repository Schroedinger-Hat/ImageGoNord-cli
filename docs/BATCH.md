# Batch Command

`batch` builds a dry-run conversion plan from an input directory.

By default the command is non-destructive and only generates a plan.

## Usage

Basic dry-run:

```shell
python src/image_go_nord_client batch ./images
```

Recursive dry-run:

```shell
python src/image_go_nord_client batch ./images --recursive
```

JSON output:

```shell
python src/image_go_nord_client batch ./images --format=json
```

Override output directory and palette in generated commands:

```shell
python src/image_go_nord_client batch ./images --out-dir ./converted --palette monokai
```

Execute conversions:

```shell
python src/image_go_nord_client batch ./images --apply
```

Execute conversions recursively with conversion options:

```shell
python src/image_go_nord_client batch ./images --recursive --apply --palette monokai --colors=Accent,Base --blur --no-avg
```

## Supported Extensions

- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.webp`
- `.tiff`
- `.gif`

## Current Scope

- Supports dry-run planning and execute mode (`--apply`)
- Validates input directory, palette, and selected colors
- Generates command previews for each detected image
- Reports per-file conversion results in JSON mode when executing
- Preserves relative input subfolders in output paths

Example path mapping with `--recursive --out-dir ./converted`:

- input: `./images/a/b/wall.png`
- output: `./converted/a/b/wall-nord.png`

## Exit Codes

- `0`: plan generated successfully, or all apply conversions succeeded
- `2`: validation error (for example missing input directory or invalid colors)
- `4`: dependency error (ImageGoNord missing for apply)
- `5`: one or more apply conversions failed
