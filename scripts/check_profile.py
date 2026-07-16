"""Fail-fast checks for the visual-first GitHub profile."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

EXPECTED_IMAGES = {
    "playground-hero-light.png": ((1600, 620), 250_000),
    "playground-hero-dark.png": ((1600, 620), 250_000),
    "playground-hero-mobile-light.png": ((800, 1040), 250_000),
    "playground-hero-mobile-dark.png": ((800, 1040), 250_000),
    "system-now-light.png": ((1600, 360), 80_000),
    "system-now-dark.png": ((1600, 360), 80_000),
    "system-now-mobile-light.png": ((800, 850), 80_000),
    "system-now-mobile-dark.png": ((800, 850), 80_000),
    "bubble-pulse-static.png": ((1600, 270), 80_000),
    "bubble-pulse-mobile-static.png": ((800, 620), 80_000),
    "project-memory.png": ((1600, 470), 200_000),
    "project-memory-mobile.png": ((800, 820), 180_000),
    "project-reasoning.png": ((1600, 440), 80_000),
    "project-reasoning-mobile.png": ((800, 790), 80_000),
    "widget-deck-light.png": ((1600, 720), 80_000),
    "widget-deck-dark.png": ((1600, 720), 80_000),
    "widget-deck-mobile-light.png": ((800, 1340), 80_000),
    "widget-deck-mobile-dark.png": ((800, 1340), 80_000),
    "signal-bar-light.png": ((1600, 230), 80_000),
    "signal-bar-dark.png": ((1600, 230), 80_000),
    "signal-bar-mobile-light.png": ((800, 350), 80_000),
    "signal-bar-mobile-dark.png": ((800, 350), 80_000),
}

EXPECTED_GIFS = {
    "bubble-pulse.gif": ((1600, 270), 500_000),
    "bubble-pulse-mobile.gif": ((800, 620), 500_000),
}

REQUIRED_COPY = (
    "CHENXI ZHANG · FUDAN CS · CLASS OF 2028 · SII STUDENT · FNLP MEMBER",
    "Vision-Language-Memory",
    "Fudan2026AIProjectSubmission",
    "66.56% local validation accuracy (798/1,199)",
    "Local validation metric only · not an official online score",
    "Shanghai Innovation Institute",
    "Fudan NLP Lab",
    "Open the lab notebook",
    "mailto:OLzcx1224@outlook.com",
)

FORBIDDEN_COPY = (
    "internship opportunities",
    "available for hire",
    "open to work",
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
    for asset in (*EXPECTED_IMAGES, *EXPECTED_GIFS):
        assert f"./assets/{asset}" in readme, f"README does not reference {asset}"
    assert readme.count("<picture>") >= 7, "profile should be built from visual components"
    assert "<details>" in readme and "</details>" in readme, "lab notes must stay collapsible"
    assert 'alt=""' in readme, "decorative one-shot animation must have an empty alt"
    assert "prefers-reduced-motion: reduce" in readme, "animation needs a reduced-motion fallback"
    assert "max-width: 600px" in readme, "mobile-specific artwork is required"


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


def check_gifs() -> int:
    total = 0
    for name, (expected_size, max_bytes) in EXPECTED_GIFS.items():
        path = ASSETS / name
        assert path.exists(), f"missing {path}"
        with Image.open(path) as image:
            assert image.size == expected_size, f"{name}: expected {expected_size}, got {image.size}"
            assert image.info.get("loop") is None, f"{name}: GIF must play only once"
            durations = []
            for frame_index in range(image.n_frames):
                image.seek(frame_index)
                durations.append(image.info.get("duration", 0))
            assert image.n_frames == 16, f"{name}: expected 16 frames, got {image.n_frames}"
            assert sum(durations) == 3_400, f"{name}: expected 3400 ms, got {sum(durations)} ms"
        size = path.stat().st_size
        assert size <= max_bytes, f"{name}: {size:,} bytes exceeds {max_bytes:,}"
        total += size
    return total


def main() -> None:
    check_readme()
    total = check_images() + check_gifs()
    assert total <= 2_500_000, f"visual assets exceed total budget: {total:,} bytes"
    source = ASSETS / "source" / "spongebob-memory-lab-dark-image2-v2.png"
    assert source.exists(), "missing final Image 2 source artwork"
    print(f"profile checks passed; referenced visual assets total {total:,} bytes")


if __name__ == "__main__":
    main()
