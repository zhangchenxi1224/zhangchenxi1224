"""Render the responsive light and dark profile banners.

The source illustrations are kept in ``assets/source`` so every deployed banner
can be reproduced locally with Pillow.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE_DIR = ASSETS / "source"

SOURCES = {
    "light": SOURCE_DIR / "underwater-code-light-source.png",
    "dark": SOURCE_DIR / "underwater-code-dark-source.png",
}

DESKTOP_SIZE = (1500, 500)
MOBILE_SIZE = (900, 600)
MOBILE_CROP = (320, 0, 1406, 724)

FONT_REGULAR = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_SEMIBOLD = Path(r"C:\Windows\Fonts\seguisb.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")

INK = "#F8FAFC"
MUTED = "#CFFAFE"
CYAN = "#22D3EE"
VIOLET = "#A78BFA"
DEEP_BLUE = (4, 17, 31)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise FileNotFoundError(f"missing required font: {path}")
    return ImageFont.truetype(str(path), size=size)


def horizontal_gradient(size: tuple[int, int], start_x: int, max_alpha: int) -> Image.Image:
    """Return a transparent-to-deep-blue right-side gradient."""

    width, height = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    pixels = layer.load()
    span = max(width - start_x - 1, 1)
    for x in range(start_x, width):
        progress = (x - start_x) / span
        eased = progress * progress * (3 - 2 * progress)
        alpha = round(max_alpha * eased)
        for y in range(height):
            pixels[x, y] = (*DEEP_BLUE, alpha)
    return layer


def vertical_gradient(size: tuple[int, int], start_y: int, max_alpha: int) -> Image.Image:
    """Return a transparent-to-deep-blue bottom gradient."""

    width, height = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    pixels = layer.load()
    span = max(height - start_y - 1, 1)
    for y in range(start_y, height):
        progress = (y - start_y) / span
        eased = progress * progress * (3 - 2 * progress)
        alpha = round(max_alpha * eased)
        for x in range(width):
            pixels[x, y] = (*DEEP_BLUE, alpha)
    return layer


def draw_pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    label: str,
    label_font: ImageFont.FreeTypeFont,
    accent: str,
) -> None:
    fill = (10, 25, 47, 190)
    draw.rounded_rectangle(xy, radius=(xy[3] - xy[1]) // 2, fill=fill, outline=accent, width=2)
    box = draw.textbbox((0, 0), label, font=label_font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    left, top, right, bottom = xy
    x = left + (right - left - text_width) / 2
    y = top + (bottom - top - text_height) / 2 - box[1]
    draw.text((x, y), label, font=label_font, fill=INK)


def render_desktop(source: Image.Image) -> Image.Image:
    canvas = source.resize(DESKTOP_SIZE, Image.Resampling.LANCZOS).convert("RGBA")
    canvas = Image.alpha_composite(canvas, horizontal_gradient(DESKTOP_SIZE, 880, 235))
    draw = ImageDraw.Draw(canvas)

    draw.text((1015, 102), "Chenxi Zhang", font=font(FONT_BOLD, 58), fill=INK)
    draw.text(
        (1018, 181),
        "CS UNDERGRADUATE  /  CLASS OF 2028",
        font=font(FONT_SEMIBOLD, 19),
        fill=MUTED,
    )

    pill_font = font(FONT_SEMIBOLD, 17)
    draw_pill(draw, (1018, 244, 1226, 284), "Multimodal Memory", pill_font, CYAN)
    draw_pill(draw, (1238, 244, 1436, 284), "LLM Post-Training", pill_font, VIOLET)
    draw_pill(draw, (1018, 298, 1200, 338), "Reproducible ML", pill_font, CYAN)

    draw.line((1018, 382, 1434, 382), fill=(34, 211, 238, 120), width=1)
    draw.text(
        (1018, 401),
        "FUDAN UNIVERSITY  ·  COMPUTER SCIENCE",
        font=font(FONT_REGULAR, 16),
        fill="#BAE6FD",
    )
    return canvas.convert("RGB")


def render_mobile(source: Image.Image) -> Image.Image:
    canvas = (
        source.crop(MOBILE_CROP)
        .resize(MOBILE_SIZE, Image.Resampling.LANCZOS)
        .convert("RGBA")
    )
    canvas = Image.alpha_composite(canvas, vertical_gradient(MOBILE_SIZE, 285, 248))
    draw = ImageDraw.Draw(canvas)

    draw.text((44, 370), "Chenxi Zhang", font=font(FONT_BOLD, 56), fill=INK)
    draw.text(
        (47, 444),
        "CS UNDERGRADUATE  /  CLASS OF 2028",
        font=font(FONT_SEMIBOLD, 24),
        fill=MUTED,
    )

    pill_font = font(FONT_SEMIBOLD, 19)
    draw_pill(draw, (46, 505, 278, 550), "Multimodal Memory", pill_font, CYAN)
    draw_pill(draw, (292, 505, 520, 550), "LLM Post-Training", pill_font, VIOLET)
    draw_pill(draw, (534, 505, 738, 550), "Reproducible ML", pill_font, CYAN)
    return canvas.convert("RGB")


def save_webp(image: Image.Image, path: Path) -> None:
    image.save(path, format="WEBP", quality=93, method=6, exact=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for theme, source_path in SOURCES.items():
        if not source_path.exists():
            raise FileNotFoundError(f"missing source illustration: {source_path}")
        with Image.open(source_path) as raw:
            artwork = raw.convert("RGB")
        if artwork.size != (2172, 724):
            raise ValueError(f"unexpected source size for {source_path}: {artwork.size}")

        save_webp(render_desktop(artwork), ASSETS / f"header-{theme}.webp")
        save_webp(render_mobile(artwork), ASSETS / f"header-mobile-{theme}.webp")

    print("rendered four responsive underwater profile banners")


if __name__ == "__main__":
    main()
