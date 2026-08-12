# Doctor Command

`doctor` provides quick diagnostics for the local CLI runtime.

## Usage

Text mode:

```shell
python src/image_go_nord_client doctor
```

JSON mode:

```shell
python src/image_go_nord_client doctor --format=json
```

## Checks

- Python runtime availability
- ImageGoNord dependency availability
- Palette inventory availability
- Textual dependency availability (optional)

## Exit Codes

- `0`: checks passed
- `4`: dependency failure (for example missing ImageGoNord)
- `2`: non-dependency validation failure
