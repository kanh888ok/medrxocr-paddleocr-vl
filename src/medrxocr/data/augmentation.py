"""Small camera-style image augmentations used for OCR experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageEnhance, ImageFilter


@dataclass(frozen=True)
class AugmentationSpec:
    name: str
    blur_radius: float = 0.0
    brightness: float = 1.0
    contrast: float = 1.0
    rotate_degrees: float = 0.0
    perspective_shift: float = 0.0


DEFAULT_CAMERA_VARIANTS: tuple[AugmentationSpec, ...] = (
    AugmentationSpec("blur", blur_radius=1.2),
    AugmentationSpec("bright", brightness=1.18, contrast=1.05),
    AugmentationSpec("dim", brightness=0.82, contrast=1.1),
    AugmentationSpec("rotate", rotate_degrees=3.0),
    AugmentationSpec("perspective", perspective_shift=0.035),
)


def variant_names() -> list[str]:
    return [spec.name for spec in DEFAULT_CAMERA_VARIANTS]


def get_variant(name: str) -> AugmentationSpec:
    for spec in DEFAULT_CAMERA_VARIANTS:
        if spec.name == name:
            return spec
    raise ValueError(f"Unknown augmentation variant: {name}. Available: {', '.join(variant_names())}")


def resolve_variants(names: Iterable[str] | None) -> list[AugmentationSpec]:
    if not names:
        return list(DEFAULT_CAMERA_VARIANTS)
    return [get_variant(name.strip()) for name in names if name.strip()]


def apply_augmentation(image: Image.Image, spec: AugmentationSpec) -> Image.Image:
    out = image.convert("RGB")
    if spec.perspective_shift:
        out = _apply_simple_perspective(out, spec.perspective_shift)
    if spec.rotate_degrees:
        out = out.rotate(spec.rotate_degrees, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=(255, 255, 255))
    if spec.blur_radius:
        out = out.filter(ImageFilter.GaussianBlur(radius=spec.blur_radius))
    if spec.brightness != 1.0:
        out = ImageEnhance.Brightness(out).enhance(spec.brightness)
    if spec.contrast != 1.0:
        out = ImageEnhance.Contrast(out).enhance(spec.contrast)
    return out


def save_augmented_image(input_path: str | Path, output_path: str | Path, spec: AugmentationSpec) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        apply_augmentation(image, spec).save(output_path)


def _apply_simple_perspective(image: Image.Image, shift_ratio: float) -> Image.Image:
    width, height = image.size
    shift = max(1, int(min(width, height) * shift_ratio))
    source = [(0, 0), (width, 0), (width, height), (0, height)]
    target = [(shift, 0), (width - shift, shift), (width, height - shift), (0, height)]
    coeffs = _perspective_coefficients(target, source)
    return image.transform(
        image.size,
        Image.Transform.PERSPECTIVE,
        coeffs,
        Image.Resampling.BICUBIC,
        fillcolor=(255, 255, 255),
    )


def _perspective_coefficients(source: list[tuple[int, int]], target: list[tuple[int, int]]) -> tuple[float, ...]:
    import numpy as np

    matrix = []
    for (x, y), (u, v) in zip(source, target):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    a = np.asarray(matrix, dtype=float)
    b = np.asarray(target, dtype=float).reshape(8)
    return tuple(np.linalg.solve(a, b).tolist())
