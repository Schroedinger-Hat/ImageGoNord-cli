from typing import Any

try:
    from ImageGoNord.contracts import (  # type: ignore
        ERROR_CODES as SHARED_ERROR_CODES,
        get_engine_capabilities,
        normalize_convert_config,
    )

    CONTRACT_SOURCE = "imagegonord"
except Exception:  # pragma: no cover - fallback when older ImageGoNord is installed
    SHARED_ERROR_CODES = {
        "validation": "E_VALIDATION",
        "dependency": "E_DEPENDENCY",
        "palette_not_found": "E_PALETTE_NOT_FOUND",
        "conversion_failed": "E_CONVERSION_FAILED",
        "internal": "E_INTERNAL",
    }

    CONTRACT_SOURCE = "cli-fallback"

    def normalize_convert_config(raw: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = raw or {}
        palette = str(payload.get("palette", "nord")).strip().lower()
        if not palette:
            raise ValueError("palette must be a non-empty string")

        colors = payload.get("colors", [])
        if colors is None:
            colors = []
        if not isinstance(colors, (list, tuple)):
            raise ValueError("colors must be a list of strings")

        normalized_colors = [str(color).strip() for color in colors if str(color).strip()]

        return {
            "palette": palette,
            "colors": normalized_colors,
            "enable_blur": bool(payload.get("enable_blur", False)),
            "disable_avg_pixels": bool(payload.get("disable_avg_pixels", False)),
        }

    def get_engine_capabilities() -> dict[str, Any]:
        return {
            "contract_version": "1.0",
            "engine": "ImageGoNord",
            "features": {
                "palette_selection": True,
                "color_filtering": True,
                "gaussian_blur": True,
                "avg_algorithm_toggle": True,
                "batch_planning": True,
                "batch_apply": True,
                "tui": True,
                "json_output": True,
            },
            "supported_image_extensions": [
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".bmp",
                ".gif",
            ],
        }


def normalize_cli_convert_config(raw: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_convert_config(raw)
    if hasattr(normalized, "to_dict"):
        return normalized.to_dict()
    return normalized


def get_engine_capabilities_snapshot() -> tuple[str, dict[str, Any]]:
    return CONTRACT_SOURCE, get_engine_capabilities()


def error_code(name: str, default: str = "E_INTERNAL") -> str:
    return SHARED_ERROR_CODES.get(name, default)
