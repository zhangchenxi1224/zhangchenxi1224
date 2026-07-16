"""Render the local, dependency-light artwork used by the profile README.

Run from the repository root with:
    python scripts/render_assets.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE_ASSETS = ASSETS / "source"

COLORS = {
    "dark_0": "#07111F",
    "dark_1": "#0B1220",
    "light": "#F8FAFC",
    "violet": "#8B5CF6",
    "indigo": "#6366F1",
    "cyan": "#22D3EE",
    "slate": "#94A3B8",
    "ink": "#0F172A",
}


def rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*rgb(hex_color), alpha)


def mix(a: str, b: str, t: float) -> tuple[int, int, int]:
    ca, cb = rgb(a), rgb(b)
    return tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        candidates = [
            Path("C:/Windows/Fonts/CascadiaMono.ttf"),
            Path("C:/Windows/Fonts/consola.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ]
    elif bold:
        candidates = [
            Path("C:/Windows/Fonts/seguisb.ttf"),
            Path("C:/Windows/Fonts/segoeuib.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]
    else:
        candidates = [
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def gradient(width: int, height: int, left: str, right: str) -> Image.Image:
    image = Image.new("RGB", (width, height), rgb(left))
    draw = ImageDraw.Draw(image)
    for x in range(width):
        draw.line((x, 0, x, height), fill=mix(left, right, x / max(1, width - 1)))
    return image.convert("RGBA")


def cover_crop(image: Image.Image, size: tuple[int, int], *, vertical_anchor: float = 0.5) -> Image.Image:
    """Resize and center-crop while preserving the image's full horizontal composition."""
    target_width, target_height = size
    scale = target_width / image.width
    resized_height = round(image.height * scale)
    resized = image.resize((target_width, resized_height), Image.Resampling.LANCZOS)
    if resized_height < target_height:
        scale = target_height / image.height
        resized_width = round(image.width * scale)
        resized = image.resize((resized_width, target_height), Image.Resampling.LANCZOS)
        left = max(0, (resized_width - target_width) // 2)
        return resized.crop((left, 0, left + target_width, target_height))
    available = resized_height - target_height
    top = round(available * max(0.0, min(1.0, vertical_anchor)))
    return resized.crop((0, top, target_width, top + target_height))


def image2_base(name: str, size: tuple[int, int], *, vertical_anchor: float = 0.5) -> Image.Image:
    path = SOURCE_ASSETS / name
    if not path.exists():
        raise FileNotFoundError(f"missing Image 2 source artwork: {path}")
    with Image.open(path) as source:
        result = cover_crop(source.convert("RGB"), size, vertical_anchor=vertical_anchor).convert("RGBA")
    result.info.clear()
    return result


def add_left_readability_gradient(
    image: Image.Image,
    color: str,
    *,
    start_alpha: int,
    solid_until: int,
    fade_until: int,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    base = rgb(color)
    for x in range(min(fade_until, image.width)):
        if x <= solid_until:
            alpha = start_alpha
        else:
            progress = (x - solid_until) / max(1, fade_until - solid_until)
            alpha = round(start_alpha * (1 - progress) ** 1.8)
        draw.line((x, 0, x, image.height), fill=(*base, alpha))
    image.alpha_composite(layer)


def add_glow(
    image: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: str,
    alpha: int,
    blur: int,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba(color, alpha))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    for x in range(32, width, 48):
        for y in range(24, height, 48):
            r = 1 if (x // 48 + y // 48) % 3 else 2
            draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int, int],
    width: int = 4,
) -> None:
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 13
    spread = math.pi / 6
    p1 = (end[0] - length * math.cos(angle - spread), end[1] - length * math.sin(angle - spread))
    p2 = (end[0] - length * math.cos(angle + spread), end[1] - length * math.sin(angle + spread))
    draw.polygon((end, p1, p2), fill=color)


def pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    label: str,
    *,
    fill: tuple[int, int, int, int],
    text_fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int] | None = None,
    text_font: ImageFont.FreeTypeFont | None = None,
    pad_x: int = 17,
    height: int = 34,
) -> int:
    text_font = text_font or font(15, bold=True)
    text_width = math.ceil(draw.textlength(label, font=text_font))
    width = text_width + pad_x * 2
    x, y = xy
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=fill, outline=outline, width=1)
    bbox = draw.textbbox((0, 0), label, font=text_font)
    text_height = bbox[3] - bbox[1]
    draw.text((x + pad_x, y + (height - text_height) / 2 - bbox[1] - 1), label, font=text_font, fill=text_fill)
    return width


def visual_frame(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    accent: tuple[int, int, int, int],
    active: bool = True,
) -> None:
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0
    draw.rounded_rectangle(box, radius=14, fill=fill, outline=outline, width=2)
    alpha = 255 if active else 90
    sun_radius = max(3, round(min(width, height) * 0.10))
    sun_x = round(x0 + width * 0.24)
    sun_y = round(y0 + height * 0.31)
    draw.ellipse((sun_x - sun_radius, sun_y - sun_radius, sun_x + sun_radius, sun_y + sun_radius), fill=(*accent[:3], alpha))
    baseline = round(y1 - height * 0.20)
    draw.polygon(
        (
            (round(x0 + width * 0.10), baseline),
            (round(x0 + width * 0.38), round(y0 + height * 0.45)),
            (round(x0 + width * 0.58), round(y1 - height * 0.30)),
            (round(x0 + width * 0.90), baseline),
        ),
        fill=(*outline[:3], 120 if active else 50),
    )
    draw.line((round(x0 + width * 0.10), baseline, round(x1 - width * 0.10), baseline), fill=(*accent[:3], alpha), width=max(2, round(height * 0.05)))


def memory_core(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    *,
    radius: int,
    surface: tuple[int, int, int, int],
    ring: tuple[int, int, int, int],
    cyan: tuple[int, int, int, int],
    strength: float = 1.0,
) -> None:
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=surface, outline=(*ring[:3], int(230 * strength)), width=5)
    draw.arc((cx - radius + 12, cy - radius + 12, cx + radius - 12, cy + radius - 12), 205, 505, fill=(*cyan[:3], int(255 * strength)), width=7)
    draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=(*ring[:3], int(230 * strength)))
    for angle in (-55, 35, 145):
        rad = math.radians(angle)
        x = cx + int((radius - 10) * math.cos(rad))
        y = cy + int((radius - 10) * math.sin(rad))
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(*cyan[:3], int(255 * strength)))


def output_tokens(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    *,
    fill: tuple[int, int, int, int],
    accent: tuple[int, int, int, int],
    active_count: int = 4,
    widths: tuple[int, ...] = (86, 62, 98, 70),
    spacing: int = 32,
    token_height: int = 18,
) -> None:
    x, y = origin
    for index, token_width in enumerate(widths):
        alpha = 235 if index < active_count else 60
        draw.rounded_rectangle(
            (x, y + index * spacing, x + token_width, y + token_height + index * spacing),
            radius=max(4, token_height // 2),
            fill=(*fill[:3], alpha),
            outline=(*accent[:3], min(255, alpha)),
            width=2,
        )


def render_hero(theme: str) -> Path:
    width, height = 1600, 400
    dark = theme == "dark"
    image = image2_base(f"hero-{theme}-image2.webp", (width, height))
    add_left_readability_gradient(
        image,
        COLORS["dark_0"] if dark else COLORS["light"],
        start_alpha=232 if dark else 242,
        solid_until=500,
        fade_until=1010,
    )
    draw = ImageDraw.Draw(image, "RGBA")

    text = rgba("#F8FAFC" if dark else COLORS["ink"])
    muted = rgba("#A5B4FC" if dark else "#475569")
    draw.rounded_rectangle((72, 54, 142, 124), radius=22, fill=rgba(COLORS["indigo"], 48), outline=rgba(COLORS["cyan"], 210), width=2)
    draw.text((91, 70), "CZ", font=font(25, bold=True), fill=text)
    draw.text((170, 61), "RESEARCH / ENGINEERING", font=font(18, bold=True), fill=muted)
    draw.text((76, 132), "CHENXI ZHANG", font=font(58, bold=True), fill=text)
    draw.text((78, 214), "MULTIMODAL MEMORY  ·  LLM POST-TRAINING", font=font(24, bold=True), fill=muted)
    draw.line((78, 263, 690, 263), fill=rgba("#64748B", 125), width=2)
    x = 78
    for label, color in (
        ("PERSISTENT STATE", COLORS["violet"]),
        ("RELIABLE EVALUATION", COLORS["indigo"]),
        ("REPRODUCIBLE ML", COLORS["cyan"]),
    ):
        used = pill(
            draw,
            (x, 294),
            label,
            fill=rgba(color, 28 if dark else 24),
            text_fill=rgba("#E2E8F0" if dark else COLORS["ink"]),
            outline=rgba(color, 145),
            text_font=font(14, bold=True),
            height=36,
        )
        x += used + 12

    output = ASSETS / f"hero-{theme}.png"
    final = image.convert("RGB")
    if dark:
        final = final.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    final.save(output, optimize=True, compress_level=9)
    return output


def base_card(source_name: str) -> Image.Image:
    image = image2_base(source_name, (1200, 260))
    tint = Image.new("RGBA", image.size, rgba(COLORS["dark_0"], 35))
    image.alpha_composite(tint)
    add_left_readability_gradient(image, COLORS["dark_0"], start_alpha=245, solid_until=430, fade_until=850)
    return image


def render_vision_card() -> Path:
    image = base_card("vision-memory-image2.webp")
    draw = ImageDraw.Draw(image, "RGBA")
    pill(draw, (62, 43), "RESEARCH  ·  WORK IN PROGRESS", fill=rgba(COLORS["violet"], 34), text_fill=rgba("#EDE9FE"), outline=rgba(COLORS["violet"], 175), text_font=font(14, bold=True), height=34)
    draw.text((62, 95), "VISION–LANGUAGE MEMORY", font=font(42, bold=True), fill=rgba("#F8FAFC"))
    draw.text((64, 155), "Persistent visual state with Qwen3-VL + DreamLite", font=font(21), fill=rgba("#A5B4FC"))
    draw.text((64, 199), "DIFFERENTIABLE UPDATES  ·  CONTROLLED EVALUATION  ·  REPRODUCIBLE SYSTEMS", font=font(14, bold=True), fill=rgba("#94A3B8"))

    output = ASSETS / "vision-language-memory.png"
    image.convert("RGB").save(output, optimize=True, compress_level=9)
    return output


def render_math_card() -> Path:
    image = base_card("math-reasoning-image2.webp")
    draw = ImageDraw.Draw(image, "RGBA")
    pill(draw, (62, 43), "COMPLETED COURSE RESEARCH", fill=rgba(COLORS["indigo"], 36), text_fill=rgba("#E0E7FF"), outline=rgba(COLORS["indigo"], 180), text_font=font(14, bold=True), height=34)
    draw.text((62, 95), "MATH WORD PROBLEM REASONING", font=font(40, bold=True), fill=rgba("#F8FAFC"))
    draw.text((64, 153), "From prompting to supervised and preference post-training", font=font(21), fill=rgba("#A5B4FC"))
    draw.text((64, 199), "PROMPT  →  SFT  →  TEACHER CoT-SFT  →  DPO / OPD", font=font(15, bold=True, mono=True), fill=rgba("#94A3B8"))

    draw.rounded_rectangle((927, 36, 1148, 78), radius=21, fill=rgba(COLORS["cyan"], 32), outline=rgba(COLORS["cyan"], 190), width=2)
    draw.text((950, 47), "66.56% LOCAL VALIDATION", font=font(14, bold=True), fill=rgba("#CFFAFE"))

    output = ASSETS / "math-word-reasoning.png"
    image.convert("RGB").save(output, optimize=True, compress_level=9)
    return output


def render_memory_flow() -> Path:
    width, height = 800, 80
    frames: list[Image.Image] = []
    frame_count = 18
    for step in range(frame_count):
        image = image2_base("vision-memory-image2.webp", (width, height))
        image.alpha_composite(Image.new("RGBA", image.size, rgba(COLORS["dark_0"], 38)))
        add_left_readability_gradient(image, COLORS["dark_0"], start_alpha=224, solid_until=180, fade_until=385)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=22, outline=rgba("#334155", 180), width=2)
        draw.text((42, 22), "PERSISTENT", font=font(13, bold=True), fill=rgba("#A5B4FC"))
        draw.text((42, 40), "MULTIMODAL MEMORY", font=font(16, bold=True), fill=rgba("#F8FAFC"))

        progress = min(1.0, max(0.0, step / (frame_count - 3)))
        start_x, end_x, y = 292, 718, 40
        particle_x = round(start_x + (end_x - start_x) * progress)
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow, "RGBA")
        glow_draw.ellipse((particle_x - 16, y - 16, particle_x + 16, y + 16), fill=rgba(COLORS["cyan"], 120))
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
        draw = ImageDraw.Draw(image, "RGBA")
        draw.ellipse((particle_x - 4, y - 4, particle_x + 4, y + 4), fill=rgba("#F8FAFC"), outline=rgba(COLORS["cyan"]), width=2)
        if step >= 10:
            strength = min(1.0, (step - 9) / 5)
            draw.ellipse((559, 14, 611, 66), outline=rgba(COLORS["cyan"], round(190 * strength)), width=2)
        frames.append(image.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))

    static_output = ASSETS / "memory-flow-static.png"
    frames[-1].convert("RGB").save(static_output, optimize=True, compress_level=9)

    output = ASSETS / "memory-flow.gif"
    durations = [100] * (frame_count - 1) + [1700]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        disposal=2,
        optimize=True,
    )
    return output


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    outputs = [
        render_hero("light"),
        render_hero("dark"),
        render_vision_card(),
        render_math_card(),
        render_memory_flow(),
    ]
    for output in outputs:
        print(f"rendered {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
