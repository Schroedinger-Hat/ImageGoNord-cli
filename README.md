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

### Contributing
- Follow the contributor guidelines
- Follow the code style / requirements
- Format for commit messages


# Authors
[TheJoin95](https://github.com/TheJoin95) & [Wabri](https://github.com/Wabri)

**NOTE**: we are not (yet) affiliated with the Nordtheme or [Arcticicestudio](https://github.com/arcticicestudio).

# Credits

[Nordtheme](https://www.nordtheme.com/)
