"""Checks for the intentionally minimal profile README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

EXPECTED_IMAGES = {
    "spongebob-memory-lab.png": (1600, 640),
    "spongebob-memory-lab-mobile.png": (800, 800),
}

REQUIRED_COPY = (
    "Chenxi Zhang",
    "Undergraduate Student in Computer Science · Class of 2028",
    "College of Computer Science and Artificial Intelligence, Fudan University",
    "Shanghai Innovation Institute",
    "Fudan NLP Lab",
    "Building reproducible multimodal memory and LLM post-training systems.",
    "关注可复现的多模态记忆、LLM 后训练与可靠评测。",
    "mailto:OLzcx1224@outlook.com",
)

FORBIDDEN_COPY = (
    "Vision-Language-Memory",
    "Fudan2026AIProjectSubmission",
    "66.56%",
    "Selected Work",
    "Research Interests",
    "Toolbox",
    "Current Loop",
    "Bubble Buffer",
    "Jellyfish Signal",
    "Experiment Recipe",
    "Research Mixtape",
    "Open the lab notebook",
    "internship opportunities",
    "available for hire",
    "github-readme-stats",
    "visitor count",
)


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in REQUIRED_COPY:
        assert required in readme, f"missing required copy: {required}"
    for forbidden in FORBIDDEN_COPY:
        assert forbidden.lower() not in readme.lower(), f"forbidden copy: {forbidden}"
    assert readme.count("<picture>") == 1, "README should contain exactly one visual"
    assert "<details>" not in readme, "README should not contain collapsed sections"

    total = 0
    for name, expected_size in EXPECTED_IMAGES.items():
        path = ASSETS / name
        assert path.exists(), f"missing {path}"
        assert f"./assets/{name}" in readme, f"README does not reference {name}"
        with Image.open(path) as image:
            assert image.size == expected_size, f"{name}: expected {expected_size}, got {image.size}"
            assert image.mode in {"RGB", "P"}, f"unexpected mode for {name}: {image.mode}"
        total += path.stat().st_size
    assert total <= 700_000, f"two-image payload is too large: {total:,} bytes"
    print(f"minimal profile checks passed; visual payload {total:,} bytes")


if __name__ == "__main__":
    main()
