"""Fail-fast checks for profile copy, local artwork, and animation behavior."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

EXPECTED_IMAGES = {
    "hero-light.png": ((1600, 400), 500_000),
    "hero-dark.png": ((1600, 400), 500_000),
    "vision-language-memory.png": ((1200, 260), 300_000),
    "math-word-reasoning.png": ((1200, 260), 300_000),
    "memory-flow-static.png": ((800, 80), 180_000),
}

REQUIRED_COPY = (
    "Chenxi Zhang",
    "Undergraduate Student in Computer Science · Class of 2028",
    "College of Computer Science and Artificial Intelligence, Fudan University",
    "Student at <a href=\"https://www.sii.edu.cn/\">Shanghai Innovation Institute</a>",
    "Member of <a href=\"https://nlp.fudan.edu.cn/nlpen/main.htm\">Fudan NLP Lab</a>",
    "Open to research collaborations and AI internship opportunities.",
    "66.56% local validation accuracy (798/1,199)",
    "This figure is a local validation metric, not an official online score.",
)

FORBIDDEN_COPY = (
    "github-readme-stats",
    "visitor count",
    "readme-typing-svg",
    "TODO",
    "PLACEHOLDER",
)


def check_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in REQUIRED_COPY:
        assert required in readme, f"missing required copy: {required}"
    for forbidden in FORBIDDEN_COPY:
        assert forbidden.lower() not in readme.lower(), f"forbidden copy or dependency: {forbidden}"
    for asset in (*EXPECTED_IMAGES, "memory-flow.gif"):
        assert f"./assets/{asset}" in readme, f"README does not reference {asset}"
    assert 'alt=""' in readme, "decorative animation must have an empty alt"


def check_images() -> int:
    total = 0
    for name, (expected_size, max_bytes) in EXPECTED_IMAGES.items():
        path = ASSETS / name
        assert path.exists(), f"missing {path}"
        with Image.open(path) as image:
            assert image.size == expected_size, f"{name}: expected {expected_size}, got {image.size}"
            assert image.mode in {"RGB", "P"}, f"{name}: expected RGB or indexed PNG, got {image.mode}"
        size = path.stat().st_size
        assert size <= max_bytes, f"{name}: {size:,} bytes exceeds {max_bytes:,}"
        total += size
    return total


def check_gif() -> int:
    path = ASSETS / "memory-flow.gif"
    assert path.exists(), f"missing {path}"
    with Image.open(path) as image:
        assert image.size == (800, 80), f"unexpected GIF size: {image.size}"
        assert image.info.get("loop") is None, "GIF must omit loop metadata and play only once"
        durations = []
        for frame_index in range(image.n_frames):
            image.seek(frame_index)
            durations.append(image.info.get("duration", 0))
        total_duration = sum(durations)
        assert 3_000 <= total_duration <= 4_000, f"unexpected GIF duration: {total_duration} ms"
        assert 10 <= image.n_frames <= 40, f"unexpected frame count: {image.n_frames}"
    size = path.stat().st_size
    assert size <= 800_000, f"GIF exceeds budget: {size:,} bytes"
    return size


def main() -> None:
    check_readme()
    total = check_images() + check_gif()
    assert total <= 2_500_000, f"visual assets exceed total budget: {total:,} bytes"
    print(f"profile checks passed; visual assets total {total:,} bytes")


if __name__ == "__main__":
    main()
