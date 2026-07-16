# Image 2 source artwork

The published profile uses one text-free Image 2 illustration as its visual anchor. All interface text, theme frames, project widgets, responsive mobile layouts, and animation frames are rendered deterministically by `scripts/render_assets.py`.

## `spongebob-memory-lab-dark-image2-v2.png`

- **Mode:** built-in OpenAI Image 2 generation
- **Reference:** the SpongeBob avatar image supplied by Chenxi Zhang; used for character identity only, not pasted or enlarged
- **Use case:** `stylized-concept`
- **Asset type:** dark-theme GitHub profile hero artwork

### Final prompt

```text
Create an original polished scene titled conceptually “Chenxi’s Underwater Memory Lab.” SpongeBob is a joyful young research assistant inside a whimsical underwater laboratory, carefully feeding three floating visual-frame postcards into a glowing bubble-shaped memory chamber. The chamber stores small luminous memory bubbles, then releases an ordered stream of tiny cyan and violet token bubbles suggesting language reasoning. Include one small jellyfish-shaped signal monitor and playful porthole details.

Use the supplied avatar only as a character identity and visual reference. Keep SpongeBob immediately recognizable, including the yellow square sponge body, large expressive eyes, white shirt, red tie, brown shorts, and cheerful energy. Do not simply enlarge or paste the low-resolution reference.

Scene/backdrop: elegant deep-sea research desk and spatial interface, sparse and uncluttered, midnight navy water with subtle bubbles and soft caustic light.

Style/medium: premium editorial 3D illustration with tactile clay, acrylic, and softly translucent bubble materials; charming and sophisticated, suitable for a polished personal tech profile rather than a children’s screenshot.

Composition/framing: wide landscape; keep the left 52% calm and low-detail for deterministic UI text overlays; place SpongeBob, the memory chamber, and visual-to-memory-to-reasoning action on the right 48%; preserve generous margins; readable when cropped to a 1600×560 banner.

Lighting/mood: curious, optimistic, playful, soft studio-underwater glow.

Color palette: #07111F and #0B1220, violet #8B5CF6, indigo #6366F1, cyan #22D3EE, SpongeBob yellow as a controlled accent.

Constraints: recognizable SpongeBob only; no other characters; no text, letters, numbers, logos, brand marks, watermark, or institutional logos.

Avoid: copying the exact source pose, low-resolution texture, chaotic cartoon background, corporate stock-tech imagery, robot heads, literal brains or circuit boards, aggressive neon cyberpunk, dense clutter.
```

The light and dark GitHub variants deliberately share this same illustration. Theme adaptation happens in the surrounding Memory Lab interface, which keeps the character colors stable and avoids a visually inconsistent second composition.
