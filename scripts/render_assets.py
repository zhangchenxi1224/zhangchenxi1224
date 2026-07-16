"""Render the two responsive crops used by the profile README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source" / "spongebob-memory-lab-dark-image2-v2.png"


def save_indexed(image: Image.Image, path: Path) -> None:
    indexed = image.convert("RGB").quantize(
        colors=256,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.FLOYDSTEINBERG,
    )
    indexed.save(path, optimize=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        raise FileNotFoundError(f"missing Image 2 source illustration: {SOURCE}")

    with Image.open(SOURCE) as raw:
        artwork = raw.convert("RGB")

    desktop_left = round(artwork.width * 0.14)
    desktop_top = round(artwork.height * 0.09)
    desktop = artwork.crop(
        (desktop_left, desktop_top, desktop_left + 1600, desktop_top + 640)
    ).resize((1600, 640), Image.Resampling.LANCZOS)

    side = artwork.height
    left = round(artwork.width * 0.36)
    left = min(left, artwork.width - side)
    mobile = artwork.crop((left, 0, left + side, side)).resize((800, 800), Image.Resampling.LANCZOS)

    save_indexed(desktop, ASSETS / "spongebob-memory-lab.png")
    save_indexed(mobile, ASSETS / "spongebob-memory-lab-mobile.png")
    print("rendered two responsive SpongeBob Memory Lab crops")


if __name__ == "__main__":
    main()
