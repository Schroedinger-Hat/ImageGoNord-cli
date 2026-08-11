# Batch Command

`batch` builds a dry-run conversion plan from an input directory.

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

## Supported Extensions

- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.webp`
- `.tiff`
- `.gif`

## Current Scope

- Builds a conversion plan only (dry-run)
- Validates input directory
- Generates command previews for each detected image
- Does not execute conversions yet

## Exit Codes

- `0`: plan generated successfully
- `2`: validation error (for example missing input directory)
