# Image 2 source prompts

The four `.webp` files in this directory are compressed source artworks generated with OpenAI Image 2 through Codex's built-in image-generation tool. Exact typography, cropping, theme treatment, and output compression are applied deterministically by `scripts/render_assets.py`.

All prompts shared these constraints: no text, letters, numbers, logos, watermarks, people, university marks, generic circuit boards, or dense visual noise.

## Dark hero

- **Use:** GitHub Profile README hero background.
- **Composition:** Ultra-wide; left 55% calm negative space; three translucent visual-state planes on the right flow into a circular latent-memory core and then an ordered language-token lattice.
- **Style:** Premium editorial technology illustration with refined glass and matte surfaces.
- **Palette:** `#07111F`, `#0B1220`, `#8B5CF6`, `#6366F1`, `#22D3EE`, and restrained off-white highlights.

## Light hero

- **Use:** Light-theme counterpart to the hero above.
- **Composition:** Same visual-state-to-memory-to-language flow, with left 55% reserved for typography.
- **Style:** Airy editorial technology illustration using frosted glass and matte ceramic surfaces.
- **Palette:** `#F8FAFC`, `#07111F`, `#8B5CF6`, `#6366F1`, and restrained `#22D3EE` accents.

## Vision-language memory cover

- **Use:** Wide project cover.
- **Composition:** Left 60% negative space; a sequence of observation panels enters a compact recurrent memory chamber with a looped state path and a language-reasoning output structure on the right.
- **Mood:** Scientific, credible, stateful, and engineered.

## Math reasoning cover

- **Use:** Wide project cover.
- **Composition:** Left 60% negative space; an abstract problem card passes through three reasoning transformations, branches into candidate paths, and converges on one verified output state.
- **Mood:** Rigorous, analytical, empirical, and honest about selection and fallback.
