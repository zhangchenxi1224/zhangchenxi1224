"""Validate the visual profile README and its generated local assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

EXPECTED_BANNERS = {
    "header-light.webp": (1500, 500),
    "header-dark.webp": (1500, 500),
    "header-mobile-light.webp": (900, 600),
    "header-mobile-dark.webp": (900, 600),
}

EXPECTED_SOURCES = {
    "underwater-code-light-source.png": (2172, 724),
    "underwater-code-dark-source.png": (2172, 724),
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
    "Toolbox",
    "GitHub Activity",
    "Contribution Current",
)

REQUIRED_COMPONENTS = (
    "readme-typing-svg.demolab.com",
    "repeat=false",
    "img.shields.io/badge/Python",
    "img.shields.io/badge/PyTorch",
    "img.shields.io/badge/Transformers",
    "img.shields.io/badge/Diffusers",
    "PEFT%20%2F%20LoRA",
    "img.shields.io/badge/Slurm",
    "./profile/stats-light.svg",
    "./profile/stats-dark.svg",
    "./profile/top-langs-light.svg",
    "./profile/top-langs-dark.svg",
    "/output/github-contribution-grid-snake.svg",
    "/output/github-contribution-grid-snake-dark.svg",
)

FORBIDDEN_COPY = (
    "Vision-Language-Memory",
    "Fudan2026AIProjectSubmission",
    "66.56%",
    "Selected Work",
    "Completed Course Research",
    "Current Focus",
    "Research Interests",
    "AI Researcher",
    "Quant Finance",
    "visitor count",
)

PINNED_ACTIONS = {
    ".github/workflows/update-stats.yml": (
        "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
        "stats-organization/github-readme-stats-action@f9d8133845f40d659a754f78b8484983ba766448",
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
        "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
    ),
    ".github/workflows/snake.yml": (
        "Platane/snk/svg-only@d8f6715049803e982ee5ff501b6b9b7d5deeb09b",
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
        "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
        "crazy-max/ghaction-github-pages@1d6ee9b181a81033a16bd707a1401afa978daab4",
    ),
}


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in (*REQUIRED_COPY, *REQUIRED_COMPONENTS):
        assert required in readme, f"missing required README content: {required}"
    for forbidden in FORBIDDEN_COPY:
        assert forbidden.lower() not in readme.lower(), f"forbidden project/copy content: {forbidden}"

    assert readme.count("<picture>") == 4, "README should contain four responsive visuals"
    assert readme.count("<h3") == 3, "README should stay compact with three component labels"
    assert "width=\"48%\"" not in readme, "stats cards should remain legible on mobile"
    assert "spongebob-memory-lab" not in readme, "README still references retired artwork"

    payload = 0
    for name, expected_size in EXPECTED_BANNERS.items():
        path = ASSETS / name
        assert path.exists(), f"missing banner: {path}"
        assert f"./assets/{name}" in readme, f"README does not reference {name}"
        with Image.open(path) as image:
            assert image.size == expected_size, f"{name}: expected {expected_size}, got {image.size}"
            assert image.format == "WEBP", f"{name}: expected WebP, got {image.format}"
            assert image.mode == "RGB", f"{name}: unexpected mode {image.mode}"
        payload += path.stat().st_size

    for name, expected_size in EXPECTED_SOURCES.items():
        path = ASSETS / "source" / name
        assert path.exists(), f"missing reproducible source: {path}"
        with Image.open(path) as image:
            assert image.size == expected_size, f"{name}: expected {expected_size}, got {image.size}"

    assert payload <= 650_000, f"responsive banner payload is too large: {payload:,} bytes"

    for relative_path, expected_actions in PINNED_ACTIONS.items():
        workflow = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "permissions: {}" in workflow, f"{relative_path}: missing deny-by-default permissions"
        assert "workflow_dispatch:" in workflow, f"{relative_path}: missing manual trigger"
        for action in expected_actions:
            assert action in workflow, f"{relative_path}: unpinned or missing action {action}"

    snake = (ROOT / ".github/workflows/snake.yml").read_text(encoding="utf-8")
    assert "contents: read" in snake and "contents: write" in snake
    assert "pull_request:" not in snake, "snake publisher must not run on pull requests"

    print(f"profile checks passed; four-banner payload {payload:,} bytes")


if __name__ == "__main__":
    main()
