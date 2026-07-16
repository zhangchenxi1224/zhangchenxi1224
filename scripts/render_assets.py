"""Render Chenxi's playful, self-contained GitHub profile artwork.

The Image 2 source illustration is intentionally text-free. Every label, widget,
button, mobile layout, and animation frame is rendered here so the final profile
is crisp, reproducible, and independent of third-party badge services.

Run from the repository root:
    python scripts/render_assets.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source" / "spongebob-memory-lab-dark-image2-v2.png"

COLORS = {
    "deep": "#07111F",
    "navy": "#0B1220",
    "light": "#F8FAFC",
    "paper": "#EEF4FF",
    "ink": "#0F172A",
    "slate": "#64748B",
    "muted": "#94A3B8",
    "violet": "#8B5CF6",
    "indigo": "#6366F1",
    "cyan": "#22D3EE",
    "yellow": "#FFD84D",
    "coral": "#FF7A90",
    "white": "#FFFFFF",
}


def rgb(value: str) -> tuple[int, int, int]:
    value = COLORS.get(value, value)
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*rgb(value), alpha)


def blend(left: str, right: str, amount: float) -> tuple[int, int, int, int]:
    a, b = rgb(left), rgb(right)
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b)) + (255,)


def font(size: int, *, bold: bool = False, mono: bool = False, cjk: bool = False) -> ImageFont.FreeTypeFont:
    if cjk:
        candidates = [
            Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ]
    elif mono:
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


def theme(theme_name: str) -> dict[str, tuple[int, int, int, int]]:
    if theme_name == "dark":
        return {
            "bg0": rgba(COLORS["deep"]),
            "bg1": rgba(COLORS["navy"]),
            "panel": (16, 28, 47, 238),
            "panel2": (20, 35, 58, 228),
            "text": rgba(COLORS["white"]),
            "muted": rgba(COLORS["muted"]),
            "line": (99, 102, 241, 92),
            "grid": (15, 58, 76, 255),
        }
    return {
        "bg0": rgba(COLORS["light"]),
        "bg1": rgba(COLORS["paper"]),
        "panel": (255, 255, 255, 238),
        "panel2": (239, 246, 255, 230),
        "text": rgba(COLORS["ink"]),
        "muted": rgba(COLORS["slate"]),
        "line": (99, 102, 241, 70),
        "grid": (216, 222, 244, 255),
    }


def surface(size: tuple[int, int], theme_name: str, *, grid: bool = True) -> Image.Image:
    width, height = size
    colors = theme(theme_name)
    image = Image.new("RGBA", size, colors["bg0"])
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(height):
        progress = y / max(1, height - 1)
        row = tuple(round(a + (b - a) * progress) for a, b in zip(colors["bg0"], colors["bg1"]))
        draw.line((0, y, width, y), fill=row)
    if grid:
        spacing = 44 if width > 1000 else 36
        for x in range(spacing, width, spacing):
            for y in range(spacing, height, spacing):
                radius = 2 if (x // spacing + y // spacing) % 5 == 0 else 1
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colors["grid"])
    return image


def add_glow(image: Image.Image, center: tuple[int, int], radius: int, color: str, alpha: int = 110) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(color, alpha))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(max(8, radius // 2))))


def bubble(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, color: str, *, active: bool = True) -> None:
    x, y = center
    alpha = 220 if active else 55
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(color, alpha // 5), outline=rgba(color, alpha), width=max(2, radius // 8))
    highlight = max(2, radius // 5)
    draw.ellipse((x - radius // 2, y - radius // 2, x - radius // 2 + highlight, y - radius // 2 + highlight), fill=(255, 255, 255, alpha))


def cover_crop(image: Image.Image, size: tuple[int, int], *, anchor_x: float = 0.5, anchor_y: float = 0.5) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    extra_x = max(0, resized.width - target_w)
    extra_y = max(0, resized.height - target_h)
    left = round(extra_x * max(0.0, min(1.0, anchor_x)))
    top = round(extra_y * max(0.0, min(1.0, anchor_y)))
    return resized.crop((left, top, left + target_w, top + target_h))


def load_art(*, right_crop: bool = False) -> Image.Image:
    if not SOURCE.exists():
        raise FileNotFoundError(f"missing Image 2 source illustration: {SOURCE}")
    with Image.open(SOURCE) as raw:
        art = raw.convert("RGBA")
    if right_crop:
        art = art.crop((round(art.width * 0.32), 0, art.width, art.height))
    return art


def paste_rounded(image: Image.Image, art: Image.Image, box: tuple[int, int, int, int], *, radius: int = 28, anchor_x: float = 0.58) -> None:
    x0, y0, x1, y1 = box
    fitted = cover_crop(art, (x1 - x0, y1 - y0), anchor_x=anchor_x)
    mask = Image.new("L", fitted.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, fitted.width - 1, fitted.height - 1), radius=radius, fill=255)
    image.paste(fitted, (x0, y0), mask)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle(box, radius=radius, outline=rgba(COLORS["cyan"], 125), width=3)


def window_chrome(draw: ImageDraw.ImageDraw, size: tuple[int, int], label: str, status: str, colors: dict[str, tuple[int, int, int, int]]) -> None:
    width, height = size
    draw.rounded_rectangle((2, 2, width - 3, height - 3), radius=28, outline=colors["line"], width=3)
    draw.line((24, 70, width - 24, 70), fill=colors["line"], width=2)
    for x, color in ((34, COLORS["coral"]), (58, COLORS["yellow"]), (82, COLORS["cyan"])):
        draw.ellipse((x - 6, 35 - 6, x + 6, 35 + 6), fill=rgba(color, 235))
    draw.text((108, 22), label, font=font(18, mono=True), fill=colors["muted"])
    status_font = font(17, mono=True)
    status_width = draw.textlength(status, font=status_font)
    draw.text((width - status_width - 34, 23), status, font=status_font, fill=rgba(COLORS["cyan"]))


def pill(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label: str,
    *,
    fill: tuple[int, int, int, int],
    text_fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int] | None = None,
    size: int = 18,
    height: int = 40,
    pad: int = 18,
) -> int:
    text_font = font(size, bold=True, mono=True)
    width = math.ceil(draw.textlength(label, font=text_font)) + pad * 2
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=fill, outline=outline, width=2)
    bbox = draw.textbbox((0, 0), label, font=text_font)
    draw.text((x + pad, y + (height - (bbox[3] - bbox[1])) / 2 - bbox[1] - 1), label, font=text_font, fill=text_fill)
    return width


def wrap(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=text_font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, text_font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int], max_width: int, spacing: int = 8) -> int:
    x, y = xy
    for line in wrap(draw, text, text_font, max_width):
        draw.text((x, y), line, font=text_font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=text_font)
        y = bbox[3] + spacing
    return y


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], colors: dict[str, tuple[int, int, int, int]], *, accent: str = "violet") -> None:
    draw.rounded_rectangle(box, radius=24, fill=colors["panel"], outline=rgba(COLORS[accent], 95), width=2)


def button(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, *, color: str = "violet") -> None:
    draw.rounded_rectangle(box, radius=18, fill=rgba(COLORS[color]), outline=rgba(COLORS["white"], 50), width=2)
    text_font = font(20, bold=True, mono=True)
    bbox = draw.textbbox((0, 0), label, font=text_font)
    x0, y0, x1, y1 = box
    draw.text(((x0 + x1 - (bbox[2] - bbox[0])) / 2, (y0 + y1 - (bbox[3] - bbox[1])) / 2 - bbox[1]), label, font=text_font, fill=rgba(COLORS["white"]))


def save_png(image: Image.Image, name: str) -> None:
    path = ASSETS / name
    palette = image.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    palette.save(path, optimize=True)


def render_hero(theme_name: str, *, mobile: bool) -> Image.Image:
    size = (800, 1040) if mobile else (1600, 620)
    image = surface(size, theme_name)
    colors = theme(theme_name)
    add_glow(image, (size[0] // 4, size[1] // 2), 240 if mobile else 310, "violet", 42)
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "bikini-bottom://chenxi/memory-lab", "LAB ONLINE", colors)

    if mobile:
        x, y = 44, 108
        badge_width = pill(draw, x, y, "CHENXI / RESEARCH PLAYGROUND", fill=rgba(COLORS["indigo"]), text_fill=rgba(COLORS["white"]), outline=rgba(COLORS["indigo"]), size=16, height=38)
        bubble(draw, (x + badge_width + 32, y + 19), 13, "yellow")
        draw.text((x, 166), "Memory Lab", font=font(74, bold=True), fill=colors["text"])
        draw.text((x, 256), "Teach pixels to remember.", font=font(32, bold=True), fill=colors["text"])
        draw.text((x, 304), "Replay every experiment.", font=font(32, bold=True), fill=colors["muted"])
        draw.text((x, 360), "把视觉、记忆与推理装进同一只泡泡。", font=font(23, cjk=True), fill=colors["muted"])
        art_box = (36, 425, 764, 970)
        paste_rounded(image, load_art(right_crop=True), art_box, radius=28, anchor_x=0.52)
        draw = ImageDraw.Draw(image, "RGBA")
        chip_y = 986
        cursor = 42
        for label, accent in (("FUDAN CS", "yellow"), ("CLASS 2028", "cyan"), ("FNLP", "violet")):
            cursor += pill(draw, cursor, chip_y, label, fill=rgba(COLORS[accent], 38), text_fill=colors["text"], outline=rgba(COLORS[accent], 110), size=14, height=34, pad=12) + 10
    else:
        x, y = 64, 126
        badge_width = pill(draw, x, y, "CHENXI / RESEARCH PLAYGROUND", fill=rgba(COLORS["indigo"]), text_fill=rgba(COLORS["white"]), outline=rgba(COLORS["indigo"]), size=17, height=40)
        bubble(draw, (x + badge_width + 34, y + 20), 14, "yellow")
        draw.text((x, 190), "Memory Lab", font=font(88, bold=True), fill=colors["text"])
        draw.text((x, 302), "Teach pixels to remember.", font=font(35, bold=True), fill=colors["text"])
        draw.text((x, 352), "Replay every experiment.", font=font(35, bold=True), fill=colors["muted"])
        draw.text((x, 418), "把视觉、记忆与推理装进同一只泡泡。", font=font(25, cjk=True), fill=colors["muted"])
        cursor = x
        for label, accent in (("FUDAN CS", "yellow"), ("CLASS 2028", "cyan"), ("FNLP", "violet")):
            cursor += pill(draw, cursor, 486, label, fill=rgba(COLORS[accent], 38), text_fill=colors["text"], outline=rgba(COLORS[accent], 110), size=15, height=36, pad=14) + 12
        paste_rounded(image, load_art(right_crop=True), (812, 88, 1554, 568), radius=30, anchor_x=0.52)
    return image


def draw_loop_widget(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], colors: dict[str, tuple[int, int, int, int]]) -> None:
    card(draw, box, colors, accent="yellow")
    x0, y0, x1, y1 = box
    draw.text((x0 + 26, y0 + 22), "CURRENT LOOP", font=font(18, mono=True, bold=True), fill=rgba(COLORS["yellow"]))
    labels = ("SEE", "STORE", "READ", "CHECK")
    line_y = y0 + 132
    left, right = x0 + 58, x1 - 58
    draw.line((left, line_y, right, line_y), fill=colors["line"], width=5)
    for index, label in enumerate(labels):
        x = round(left + (right - left) * index / 3)
        bubble(draw, (x, line_y), 15, "cyan" if index < 3 else "yellow")
        label_font = font(14, mono=True, bold=True)
        width = draw.textlength(label, font=label_font)
        draw.text((x - width / 2, line_y + 32), label, font=label_font, fill=colors["muted"])


def draw_engine_widget(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], colors: dict[str, tuple[int, int, int, int]]) -> None:
    card(draw, box, colors, accent="cyan")
    x0, y0, x1, _ = box
    draw.text((x0 + 26, y0 + 22), "ACTIVE ENGINE", font=font(18, mono=True, bold=True), fill=rgba(COLORS["cyan"]))
    draw.text((x0 + 26, y0 + 72), "Qwen3-VL", font=font(38, bold=True), fill=colors["text"])
    draw.text((x0 + 26, y0 + 122), "× DreamLite", font=font(30, bold=True), fill=rgba(COLORS["violet"]))
    draw.text((x0 + 26, y0 + 174), "persistent visual state", font=font(16, mono=True), fill=colors["muted"])
    for index in range(3):
        bubble(draw, (x1 - 52 - index * 30, y0 + 42 + index * 28), 9 + index * 2, "cyan" if index % 2 == 0 else "violet")


def draw_mode_widget(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], colors: dict[str, tuple[int, int, int, int]]) -> None:
    card(draw, box, colors, accent="violet")
    x0, y0, x1, _ = box
    draw.text((x0 + 26, y0 + 22), "LAB MODE", font=font(18, mono=True, bold=True), fill=rgba(COLORS["violet"]))
    draw.text((x0 + 26, y0 + 70), "CURIOUS", font=font(42, bold=True), fill=colors["text"])
    draw.text((x0 + 26, y0 + 126), "reproduce / probe / iterate", font=font(16, mono=True), fill=colors["muted"])
    bar = (x0 + 26, y0 + 176, x1 - 26, y0 + 190)
    draw.rounded_rectangle(bar, radius=7, fill=colors["line"])
    draw.rounded_rectangle((bar[0], bar[1], round(bar[0] + (bar[2] - bar[0]) * 0.78), bar[3]), radius=7, fill=rgba(COLORS["violet"]))


def render_system(theme_name: str, *, mobile: bool) -> Image.Image:
    size = (800, 850) if mobile else (1600, 360)
    image = surface(size, theme_name)
    colors = theme(theme_name)
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "STATUS / NOW", "SYNC 03:42", colors)
    if mobile:
        boxes = [(34, 92, 766, 322), (34, 340, 766, 570), (34, 588, 766, 818)]
    else:
        boxes = [(34, 92, 518, 326), (558, 92, 1042, 326), (1082, 92, 1566, 326)]
    draw_loop_widget(draw, boxes[0], colors)
    draw_engine_widget(draw, boxes[1], colors)
    draw_mode_widget(draw, boxes[2], colors)
    return image


def render_pulse_frame(*, mobile: bool, frame_index: int) -> Image.Image:
    size = (800, 620) if mobile else (1600, 270)
    image = surface(size, "dark")
    colors = theme("dark")
    progress = frame_index / 15
    add_glow(image, (size[0] // 2, size[1] // 2), 210 if mobile else 260, "cyan", 32 + round(35 * progress))
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "BUBBLE BUFFER / ONE-SHOT", f"FRAME {frame_index + 1:02d} / 16", colors)
    labels = ("OBSERVE", "WRITE", "READ", "VERIFY")
    if mobile:
        points = [(142, 152), (142, 278), (142, 404), (142, 530)]
        for start, end in zip(points, points[1:]):
            draw.line((*start, *end), fill=colors["line"], width=7)
        total_start, total_end = points[0][1], points[-1][1]
        active_end = round(total_start + (total_end - total_start) * progress)
        draw.line((points[0][0], total_start, points[0][0], active_end), fill=rgba(COLORS["cyan"]), width=7)
        for index, ((x, y), label) in enumerate(zip(points, labels)):
            active = progress >= index / 3
            bubble(draw, (x, y), 24, "yellow" if index == 3 and active else "cyan", active=active)
            draw.text((210, y - 23), label, font=font(25, mono=True, bold=True), fill=colors["text"] if active else colors["muted"])
            sub = ("visual frame", "latent state", "frozen reader", "honest result")[index]
            draw.text((210, y + 15), sub, font=font(17, mono=True), fill=colors["muted"])
        if frame_index == 15:
            pill(draw, 494, 516, "MEMORY STABLE", fill=rgba(COLORS["yellow"]), text_fill=rgba(COLORS["deep"]), outline=rgba(COLORS["yellow"]), size=14, height=34)
    else:
        points = [(245, 158), (615, 158), (985, 158), (1355, 158)]
        start_x, end_x = points[0][0], points[-1][0]
        draw.line((start_x, 158, end_x, 158), fill=colors["line"], width=8)
        draw.line((start_x, 158, round(start_x + (end_x - start_x) * progress), 158), fill=rgba(COLORS["cyan"]), width=8)
        for index, ((x, y), label) in enumerate(zip(points, labels)):
            active = progress >= index / 3
            bubble(draw, (x, y), 25, "yellow" if index == 3 and active else "cyan", active=active)
            label_font = font(18, mono=True, bold=True)
            width = draw.textlength(label, font=label_font)
            draw.text((x - width / 2, y + 42), label, font=label_font, fill=colors["text"] if active else colors["muted"])
        if frame_index == 15:
            pill(draw, 1268, 87, "MEMORY STABLE", fill=rgba(COLORS["yellow"]), text_fill=rgba(COLORS["deep"]), outline=rgba(COLORS["yellow"]), size=14, height=34)
    return image


def save_pulse(*, mobile: bool) -> None:
    frames = [render_pulse_frame(mobile=mobile, frame_index=index) for index in range(16)]
    stem = "bubble-pulse-mobile" if mobile else "bubble-pulse"
    save_png(frames[-1], f"{stem}-static.png")
    palette = frames[-1].convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    indexed = [frame.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(
        ASSETS / f"{stem}.gif",
        save_all=True,
        append_images=indexed[1:],
        duration=[200] * 15 + [400],
        disposal=2,
        optimize=True,
    )


def render_memory_project(*, mobile: bool) -> Image.Image:
    size = (800, 820) if mobile else (1600, 470)
    image = surface(size, "dark")
    colors = theme("dark")
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "EXPERIMENT / 01 / MEMORY TANK", "LIVE · WIP", colors)
    if mobile:
        paste_rounded(image, load_art(right_crop=True), (32, 88, 768, 382), radius=24, anchor_x=0.46)
        draw = ImageDraw.Draw(image, "RGBA")
        x, y, width = 42, 414, 716
        pill(draw, x, y, "VISION · MEMORY · LANGUAGE", fill=rgba(COLORS["cyan"]), text_fill=rgba(COLORS["deep"]), outline=rgba(COLORS["cyan"]), size=14, height=34)
        draw.text((x, y + 56), "Vision-Language-", font=font(51, bold=True), fill=colors["text"])
        draw.text((x, y + 112), "Memory", font=font(51, bold=True), fill=colors["text"])
        next_y = draw_wrapped(draw, (x, y + 184), "A reproducible sandbox for models that remember what they see.", font(24), colors["muted"], width)
        draw.text((x, next_y + 14), "QWEN3-VL  →  DREAMLITE  →  CONTINUAL STATE", font=font(15, mono=True, bold=True), fill=rgba(COLORS["cyan"]))
        button(draw, (x, 744, 438, 796), "ENTER MEMORY LAB", color="violet")
    else:
        x, y, width = 56, 112, 700
        pill(draw, x, y, "VISION · MEMORY · LANGUAGE", fill=rgba(COLORS["cyan"]), text_fill=rgba(COLORS["deep"]), outline=rgba(COLORS["cyan"]), size=15, height=36)
        draw.text((x, y + 58), "Vision-Language-Memory", font=font(55, bold=True), fill=colors["text"])
        next_y = draw_wrapped(draw, (x, y + 130), "A reproducible sandbox for models that remember what they see.", font(27), colors["muted"], width)
        draw.text((x, next_y + 20), "QWEN3-VL  →  DREAMLITE  →  CONTINUAL STATE", font=font(17, mono=True, bold=True), fill=rgba(COLORS["cyan"]))
        button(draw, (x, 364, 452, 424), "ENTER MEMORY LAB", color="violet")
        paste_rounded(image, load_art(right_crop=True), (830, 92, 1566, 438), radius=26, anchor_x=0.50)
    return image


def draw_reasoning_route(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], labels: tuple[str, ...], colors: dict[str, tuple[int, int, int, int]]) -> None:
    for start, end in zip(points, points[1:]):
        draw.line((*start, *end), fill=rgba(COLORS["violet"], 180), width=5)
    for index, ((x, y), label) in enumerate(zip(points, labels)):
        accent = "yellow" if index == len(points) - 1 else ("cyan" if index % 2 == 0 else "violet")
        bubble(draw, (x, y), 20, accent)
        label_font = font(16, mono=True, bold=True)
        width = draw.textlength(label, font=label_font)
        draw.text((x - width / 2, y + 32), label, font=label_font, fill=colors["muted"])


def render_reasoning_project(*, mobile: bool) -> Image.Image:
    size = (800, 790) if mobile else (1600, 440)
    image = surface(size, "dark")
    colors = theme("dark")
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "EXPERIMENT / 02 / REASONING RECIPE", "COMPLETE", colors)
    if mobile:
        x, y, width = 42, 104, 716
        pill(draw, x, y, "COURSE RESEARCH · COMPLETE", fill=rgba(COLORS["yellow"]), text_fill=rgba(COLORS["deep"]), outline=rgba(COLORS["yellow"]), size=14, height=34)
        draw.text((x, y + 58), "Math Word Problem", font=font(46, bold=True), fill=colors["text"])
        draw.text((x, y + 112), "Reasoning", font=font(46, bold=True), fill=colors["text"])
        draw_reasoning_route(draw, [(110, 338), (300, 338), (490, 338), (680, 338)], ("PROMPT", "SFT", "DPO", "OPD"), colors)
        metric_box = (42, 420, 758, 662)
        card(draw, metric_box, colors, accent="yellow")
        draw.text((70, 448), "66.56%", font=font(88, bold=True), fill=rgba(COLORS["yellow"]))
        draw.text((70, 552), "LOCAL VALIDATION", font=font(20, mono=True, bold=True), fill=colors["text"])
        draw.text((70, 594), "798 / 1,199 · BEST RECORDED RUN", font=font(16, mono=True), fill=colors["muted"])
        button(draw, (42, 704, 460, 758), "INSPECT THE RUN", color="indigo")
    else:
        x, y = 56, 112
        pill(draw, x, y, "COURSE RESEARCH · COMPLETE", fill=rgba(COLORS["yellow"]), text_fill=rgba(COLORS["deep"]), outline=rgba(COLORS["yellow"]), size=15, height=36)
        draw.text((x, y + 62), "Math Word Problem Reasoning", font=font(52, bold=True), fill=colors["text"])
        draw.text((x, y + 132), "One problem set. Four post-training routes.", font=font(27), fill=colors["muted"])
        draw_reasoning_route(draw, [(124, 330), (308, 330), (492, 330), (676, 330)], ("PROMPT", "SFT", "DPO", "OPD"), colors)
        button(draw, (820, 342, 1204, 402), "INSPECT THE RUN", color="indigo")
        metric_box = (914, 102, 1548, 314)
        card(draw, metric_box, colors, accent="yellow")
        draw.text((954, 126), "66.56%", font=font(88, bold=True), fill=rgba(COLORS["yellow"]))
        draw.text((1248, 151), "LOCAL", font=font(19, mono=True, bold=True), fill=colors["text"])
        draw.text((1248, 183), "VALIDATION", font=font(19, mono=True, bold=True), fill=colors["text"])
        draw.text((954, 251), "798 / 1,199 · BEST RECORDED RUN", font=font(16, mono=True), fill=colors["muted"])
    return image


def wave_points(box: tuple[int, int, int, int], *, phases: float = 0.0) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    points = []
    for x in range(x0, x1 + 1, 5):
        t = (x - x0) / max(1, x1 - x0)
        wave = math.sin(t * math.pi * 4 + phases) * 0.34 + math.sin(t * math.pi * 9 + phases * 0.7) * 0.12
        y = round((y0 + y1) / 2 + wave * (y1 - y0))
        points.append((x, y))
    return points


def render_widget_deck(theme_name: str, *, mobile: bool) -> Image.Image:
    size = (800, 1340) if mobile else (1600, 720)
    image = surface(size, theme_name)
    colors = theme(theme_name)
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "PLAYGROUND / WIDGET DECK", "4 MODULES", colors)
    if mobile:
        boxes = [(34, 92, 766, 334), (34, 352, 766, 594), (34, 612, 766, 854), (34, 872, 766, 1114)]
        kit_box = (34, 1132, 766, 1308)
    else:
        boxes = [(34, 92, 782, 322), (818, 92, 1566, 322), (34, 342, 782, 572), (818, 342, 1566, 572)]
        kit_box = (34, 592, 1566, 686)

    # Bubble buffer
    card(draw, boxes[0], colors, accent="cyan")
    x0, y0, x1, _ = boxes[0]
    draw.text((x0 + 26, y0 + 20), "BUBBLE BUFFER", font=font(18, mono=True, bold=True), fill=rgba(COLORS["cyan"]))
    centers = [x0 + 84 + index * ((x1 - x0 - 168) // 3) for index in range(4)]
    for index, x in enumerate(centers):
        bubble(draw, (x, y0 + 126), 29, "cyan" if index < 3 else "violet", active=index < 3)
    draw.text((x0 + 26, y0 + 190), "3 STORED  /  1 LISTENING", font=font(15, mono=True), fill=colors["muted"])

    # Jellyfish signal
    card(draw, boxes[1], colors, accent="violet")
    x0, y0, x1, _ = boxes[1]
    draw.text((x0 + 26, y0 + 20), "JELLYFISH SIGNAL", font=font(18, mono=True, bold=True), fill=rgba(COLORS["violet"]))
    cap_center = (x0 + 88, y0 + 116)
    draw.arc((cap_center[0] - 38, cap_center[1] - 34, cap_center[0] + 38, cap_center[1] + 34), 180, 360, fill=rgba(COLORS["violet"]), width=6)
    for offset in (-24, -8, 8, 24):
        draw.arc((cap_center[0] + offset - 8, cap_center[1], cap_center[0] + offset + 8, cap_center[1] + 58), 70, 270, fill=rgba(COLORS["cyan"], 180), width=4)
    draw.line(wave_points((x0 + 160, y0 + 78, x1 - 28, y0 + 166), phases=0.7), fill=rgba(COLORS["cyan"]), width=5, joint="curve")
    draw.text((x0 + 26, y0 + 190), "SIGNAL CLEAN  ·  NO CLAIM DRIFT", font=font(15, mono=True), fill=colors["muted"])

    # Experiment recipe
    card(draw, boxes[2], colors, accent="yellow")
    x0, y0, x1, _ = boxes[2]
    draw.text((x0 + 26, y0 + 20), "EXPERIMENT RECIPE", font=font(18, mono=True, bold=True), fill=rgba(COLORS["yellow"]))
    steps = (("CAPTURE", True), ("COMPRESS", True), ("RETRIEVE", True), ("VERIFY", False))
    for index, (label, done) in enumerate(steps):
        row_y = y0 + 66 + index * 36
        draw.rounded_rectangle((x0 + 28, row_y, x0 + 50, row_y + 22), radius=6, fill=rgba(COLORS["yellow"], 210 if done else 35), outline=rgba(COLORS["yellow"], 140), width=2)
        if done:
            draw.line((x0 + 34, row_y + 11, x0 + 39, row_y + 16, x0 + 47, row_y + 6), fill=rgba(COLORS["deep"]), width=3)
        draw.text((x0 + 68, row_y - 1), label, font=font(16, mono=True, bold=True), fill=colors["text"] if done else colors["muted"])
    draw.text((x1 - 220, y0 + 190), "REPEAT LOOP", font=font(15, mono=True, bold=True), fill=rgba(COLORS["yellow"]))

    # Research mixtape
    card(draw, boxes[3], colors, accent="coral")
    x0, y0, x1, _ = boxes[3]
    draw.text((x0 + 26, y0 + 20), "RESEARCH MIXTAPE", font=font(18, mono=True, bold=True), fill=rgba(COLORS["coral"]))
    tape = (x0 + 28, y0 + 66, x0 + 220, y0 + 170)
    draw.rounded_rectangle(tape, radius=18, fill=colors["panel2"], outline=rgba(COLORS["coral"]), width=3)
    for cx in (tape[0] + 55, tape[2] - 55):
        draw.ellipse((cx - 20, y0 + 96, cx + 20, y0 + 136), fill=rgba(COLORS["deep"]), outline=rgba(COLORS["coral"]), width=5)
    draw.line((tape[0] + 50, y0 + 148, tape[2] - 50, y0 + 148), fill=rgba(COLORS["coral"], 160), width=4)
    labels = ("VISION", "MEMORY", "POST-TRAIN", "EVAL")
    cursor_x, cursor_y = x0 + 250, y0 + 70
    for index, label in enumerate(labels):
        if index == 2:
            cursor_x, cursor_y = x0 + 250, y0 + 126
        cursor_x += pill(draw, cursor_x, cursor_y, label, fill=rgba(COLORS["coral"], 25), text_fill=colors["text"], outline=rgba(COLORS["coral"], 80), size=13, height=34, pad=12) + 10

    # Lab kit strip
    card(draw, kit_box, colors, accent="indigo")
    x0, y0, x1, y1 = kit_box
    draw.text((x0 + 24, y0 + 18), "LAB KIT", font=font(16, mono=True, bold=True), fill=rgba(COLORS["indigo"]))
    tools = ("PYTHON", "PYTORCH", "TRANSFORMERS", "DIFFUSERS", "PEFT / LORA", "SLURM")
    if mobile:
        cursor_x, cursor_y = x0 + 24, y0 + 58
        for index, label in enumerate(tools):
            if index == 3:
                cursor_x, cursor_y = x0 + 24, y0 + 106
            cursor_x += pill(draw, cursor_x, cursor_y, label, fill=rgba(COLORS["indigo"], 24), text_fill=colors["text"], outline=rgba(COLORS["indigo"], 75), size=12, height=32, pad=10) + 8
    else:
        cursor_x = x0 + 130
        for label in tools:
            cursor_x += pill(draw, cursor_x, y0 + 29, label, fill=rgba(COLORS["indigo"], 24), text_fill=colors["text"], outline=rgba(COLORS["indigo"], 75), size=13, height=34, pad=12) + 10
    return image


def render_footer(theme_name: str, *, mobile: bool) -> Image.Image:
    size = (800, 350) if mobile else (1600, 230)
    image = surface(size, theme_name)
    colors = theme(theme_name)
    draw = ImageDraw.Draw(image, "RGBA")
    window_chrome(draw, size, "signal://olzcx1224", "CHANNEL OPEN", colors)
    if mobile:
        bubble(draw, (92, 143), 34, "yellow")
        draw.text((148, 103), "SEND A SIGNAL", font=font(45, bold=True), fill=colors["text"])
        draw.text((148, 164), "ideas / notes / hello", font=font(19, mono=True), fill=colors["muted"])
        button(draw, (44, 226, 756, 286), "OLZCX1224@OUTLOOK.COM", color="violet")
        draw.text((50, 309), "FUDAN CS  ·  SII STUDENT  ·  FNLP MEMBER", font=font(14, mono=True), fill=colors["muted"])
    else:
        bubble(draw, (100, 142), 34, "yellow")
        draw.text((160, 98), "SEND A SIGNAL", font=font(48, bold=True), fill=colors["text"])
        draw.text((160, 160), "ideas / reproducibility notes / hello", font=font(18, mono=True), fill=colors["muted"])
        button(draw, (884, 104, 1518, 170), "OLZCX1224@OUTLOOK.COM", color="violet")
        draw.text((884, 184), "FUDAN CS  ·  SII STUDENT  ·  FNLP MEMBER", font=font(14, mono=True), fill=colors["muted"])
    return image


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for theme_name in ("light", "dark"):
        save_png(render_hero(theme_name, mobile=False), f"playground-hero-{theme_name}.png")
        save_png(render_hero(theme_name, mobile=True), f"playground-hero-mobile-{theme_name}.png")
        save_png(render_system(theme_name, mobile=False), f"system-now-{theme_name}.png")
        save_png(render_system(theme_name, mobile=True), f"system-now-mobile-{theme_name}.png")
        save_png(render_widget_deck(theme_name, mobile=False), f"widget-deck-{theme_name}.png")
        save_png(render_widget_deck(theme_name, mobile=True), f"widget-deck-mobile-{theme_name}.png")
        save_png(render_footer(theme_name, mobile=False), f"signal-bar-{theme_name}.png")
        save_png(render_footer(theme_name, mobile=True), f"signal-bar-mobile-{theme_name}.png")
    save_png(render_memory_project(mobile=False), "project-memory.png")
    save_png(render_memory_project(mobile=True), "project-memory-mobile.png")
    save_png(render_reasoning_project(mobile=False), "project-reasoning.png")
    save_png(render_reasoning_project(mobile=True), "project-reasoning-mobile.png")
    save_pulse(mobile=False)
    save_pulse(mobile=True)
    print("rendered Memory Lab profile assets")


if __name__ == "__main__":
    main()
