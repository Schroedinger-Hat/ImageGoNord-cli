# Poetry and PyPI Release

This project uses Poetry for packaging and publishing.

## Prerequisites

- Python 3.10+
- Poetry installed

Install Poetry (if needed):

```shell
pip install poetry
```

## Install dependencies

```shell
poetry install
```

Run locally with Poetry:

```shell
poetry run ign --help
poetry run image-go-nord-client --help
```

## Build artifacts

```shell
poetry build
```

Expected output in `dist/`:

- source distribution (`.tar.gz`)
- wheel (`.whl`)

## Local install test

```shell
pip install dist/image_go_nord_client-1.0.0-py3-none-any.whl
image-go-nord-client --help
ign --help
```

## Publish to PyPI

```shell
poetry config pypi-token.pypi <your-token>
poetry publish --build
```

## Notes

- Package metadata is defined in `pyproject.toml`.
- Console scripts are `image-go-nord-client` and `ign`.
- Palette `.txt` files and `VERSION` are included in package data.

## Troubleshooting

If `poetry install` fails on Pillow build backends:

```shell
poetry lock
poetry install
```

If needed, switch Poetry to a compatible interpreter:

```shell
poetry env use 3.13
poetry install
```
