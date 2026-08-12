# ImageGoNord CLI Roadmap

> A modern command-line interface for ImageGoNord.

## Status Snapshot (2026-08-11)

- Completed: modern command framework (`ign` style via module entrypoint) with compatibility fallback.
- Completed: command structure foundations (`convert`, `batch`, `palette`, `doctor`, `tui`) and JSON contract continuity.
- Completed: batch dry-run and apply execution with deterministic error/exit semantics.
- Completed: preserved recursive output folder mapping for batch conversions.
- Completed: beautiful terminal output baseline (Rich tables for palette/batch, batch apply progress bar, structured doctor report).
- Next: richer terminal presentation (tables/progress/spinners), watch mode, analyze/benchmark/compare commands.

## Vision

ImageGoNord CLI aims to provide the fastest and most enjoyable way to convert images directly from the terminal.

The CLI should feel modern, discoverable, scriptable and powerful enough for both casual users and production workflows.

It is built on top of the ImageGoNord Python library and exposes its capabilities through an intuitive command-line experience.

---

# Guiding Principles

- Simple for beginners
- Powerful for automation
- Beautiful terminal output
- Script-friendly
- Cross-platform
- Zero configuration for common use cases

---

# Version 1.x

## Modern CLI Framework

Replace the current CLI with a modern framework.

Possible stack:

- Typer
- Rich
- Click (internally if needed)

Benefits

- Autocomplete
- Better help pages
- Colored output
- Progress bars
- Interactive prompts

---

# Command Structure

Current goal:

```bash
ign convert image.png
```

Future commands

```bash
ign convert image.png

ign batch ./images

ign palette list

ign palette install catppuccin

ign palette info nord

ign extract image.jpg

ign benchmark

ign doctor

ign config

ign watch wallpapers/
```

---

# Beautiful Terminal UI

Inspired by tools like:

- uv
- gh
- docker
- npm
- cargo

Features

- Colors
- Icons
- Tables
- Progress bars
- Spinners
- Live updates

Example

```text
✔ Loading image

✔ Loading palette

⠙ Applying Floyd-Steinberg

████████████████████ 100%

✔ Saved output.png
```

---

# Interactive Mode

Launching

```bash
ign
```

could open an interactive terminal application.

Example

```
Choose an action

❯ Convert Image

  Extract Palette

  Batch Conversion

  Browse Palettes

  Settings
```

---

# Batch Processing

```bash
ign batch wallpapers/
```

Options

- Recursive folders
- Parallel workers
- Progress summary
- Resume support

---

# Watch Mode

```bash
ign watch ./wallpapers
```

Automatically converts newly added files.

Useful for artists and designers.

---

# Palette Management

```bash
ign palette list

ign palette search nord

ign palette install gruvbox

ign palette remove dracula

ign palette export
```

---

# Image Analysis

```bash
ign analyze image.png
```

Display

- Resolution
- Dominant colors
- Color count
- Suggested palettes
- File size
- Estimated quality

---

# Compare

```bash
ign compare original.png converted.png
```

Show

- SSIM
- DeltaE
- Palette usage
- Histogram similarity

---

# Preview

Allow previews directly inside supported terminals.

Possible implementations

- Kitty Graphics Protocol
- iTerm2 Images
- sixel
- chafa fallback

Example

```bash
ign preview image.png
```

---

# Benchmarking

```bash
ign benchmark image.png
```

Display

- Processing time
- Memory usage
- Algorithm timings
- Output quality

---

# Configuration

```bash
ign config init
```

Global configuration

```yaml
default_palette: nord

default_dither: atkinson

workers: auto
```

---

# Shell Completion

Support

- Bash
- Zsh
- Fish
- PowerShell

---

# Documentation

Improve

- Help pages
- Examples
- Recipes
- Common workflows

---

# Future

## Interactive Terminal UI

Investigate building a full-screen terminal interface.

Possible technologies

Python

- Textual
- Rich Live

Alternative

- Ink (React)

The TUI should provide

- Image browser
- Palette explorer
- Live conversion preview
- Batch queue
- Settings

---

# CI/CD Integration

Provide examples for

GitHub Actions

GitLab CI

Azure Pipelines

Jenkins

Docker

---

# Packaging

Easy installation

```bash
pip install image-go-nord-cli
```

Future

```bash
brew install image-go-nord

scoop install image-go-nord

apt install image-go-nord
```

---

# Not Planned

The CLI is **not** intended to replace the web application.

Its purpose is to provide a fast, scriptable and developer-friendly interface for the ImageGoNord library.

---

# Long-Term Goal

ImageGoNord CLI should become the easiest way to process palette-constrained images from the terminal.

Whether converting a single wallpaper, processing thousands of images in CI/CD, or experimenting interactively, the CLI should provide a consistent and delightful experience while remaining fully compatible with the ImageGoNord Python library.