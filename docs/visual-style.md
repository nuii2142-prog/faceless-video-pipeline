# Visual Style — Faceless Shorts (thin-line stickman doodle)

Locked style for EVERY image in a clip, so the whole video looks consistent.
**Updated 2026-06-28** after a 3-model A/B/C test (krea2 / flux2 / z-image). The thin-line
direction below is the current house style; the old thick-marker block is kept at the bottom
as history.

---

## 🏆 Production model = z-image-turbo

- Workflow: `ComfyUi Api Workflow/image_z_image_turbo (2).json`
- Nodes: positive `57:27.text`, seed `57:3.seed`, save `9`, cfg 1, 8 steps, 1936×1088 (16:9).
- ~26 s/img on the RTX 5070 → ~27 min for a 62-image clip (the only model fast enough for full clips).
- Driver: `scripts/batch_zturbo.py <slug>` (reads `scene_prompts.json`, applies the split style below, fixed seed 42).
- **flux2-dev / flux2-turbo** = beautiful but ~3 min / ~2 min per image → use ONLY for one-off thumbnails.

---

## ✅ Split style (the key to no figure-injection)

The style is SPLIT so non-character scenes don't get a stick figure drawn into them.
Both blocks live in `scripts/comfy_run.py` (single source) and are imported by the batch/test scripts.

**`BASE_STYLE` — appended to EVERY scene (never mentions a person):**
> Minimalist hand-drawn doodle drawn with THIN, fine, clean black pen lines — light and delicate, even
> single-stroke weight, NOT thick, NOT heavy, NOT marker (keep this exact line style). Use a FEW soft, gentle,
> muted flat colors as light accents (soft green, warm tan, gentle sky-blue, soft yellow) — calm and subtle,
> never saturated, never busy; keep the image mostly white and airy. Flat fills only — absolutely NO shading,
> NO gradient, NO drop shadow, NO paper texture. When the scene shows a place or a person, add a FEW small,
> light supporting details that hint at the surroundings and help tell the story (a couple of small plants, a
> little sun, a few soft ground or horizon lines) — gentle, sparse, uncluttered. For a plain object, icon, or
> number, keep it clean and simple with little or no background. Compose the subject at a comfortable
> MEDIUM-LARGE size, well-proportioned and balanced, kept fully inside a safe area so nothing touches the edges.
> Clean, childlike, calm, low-to-medium detail. 16:9 landscape composition.

> Color/detail level locked at "subtle" (Nuay 2026-06-28): thin lines kept, character stays plain WHITE
> (color goes into environments/objects only), rich-ish landscapes + simple character is the intended contrast.
> Batch flags: `batch_zturbo.py <slug> [--only 5,7,8] [--tag test]` (`--tag` writes to `frames_<tag>/` for A/B style tests; `--only` to re-roll specific scenes).

**`CHARACTER_STYLE` — appended ONLY when `shot_type == "CHARACTER"` (pins one consistent character):**
> The person is ALWAYS the exact same character, drawn identically in every image: a round WHITE head with a
> minimal face (two small black dot eyes, thin eyebrows, one small curved mouth), and a simple slim body with a
> clean thin OUTLINE — a narrow rounded torso with thin outlined arms and thin outlined legs (a soft cartoon
> stick figure with a lightly outlined body, NOT a single bare line, NOT a filled silhouette).
> Always the same head, same body shape, same thin even line weight.

---

## ⛔ NEGATIVE prompt (`NEGATIVE` in comfy_run.py)

INERT on cfg-1 turbo models (z-turbo, krea2) but ACTIVE on real-cfg models (z-image base, etc.).
Wire into the workflow's negative-text node when using a cfg>1 model.
> thick heavy outlines, bold marker strokes, shading, gradients, drop shadows, paper texture, realistic,
> 3d render, photo, painterly, cluttered, busy, crowded, subject touching the edge, cropped at the frame edge,
> text, words, letters, captions, watermark, signature, blurry, low quality

---

## Shot types (set per beat in `scene_prompts.json`)

- **CHARACTER** — the figure does the one action the caption names. Gets `CHARACTER_STYLE`. Use "the character".
- **B-ROLL** — an object / icon / chart / a short NUMBER (e.g. `58`, `40%`). No person → no `CHARACTER_STYLE`.
- **ATMOSPHERE** — a place / landscape. Pure place = "no people"; a person-in-the-scene = "one small figure" (stays generic, not the full spec, since it is small/distant).

There are NO quotas — the mix emerges from what each line means (the method lives in
`skills/script-breakdown/SKILL.md` B3). Keep each visual to ONE clear idea, staged as simply as it
can be while still telling the story; BASE_STYLE already invites a few small supporting details, so
a real scene is welcome — "two tiny icons side by side" is a last resort, not a default.
Do NOT make the model render words/sentences (it garbles them) — only a short standalone number
when the caption is a statistic. Symbols (`?`, `=`, `X`, `%`, arrow) render fine.

---

## Aspect ratio
- **16:9** long-form (the latent node in the workflow already sets this).
- **9:16** vertical Shorts — `python scripts/batch_zturbo.py <slug> --portrait` flips BOTH the
  latent resolution and the aspect line inside BASE_STYLE (no manual edits).

## Known model quirks (z-turbo, cfg 1)
- Negatives are inert → rely on the split style + positive wording to keep scenes clean.
- **Numbers: reliable up to ~2 digits, garbles 3+.** "82%" and "49%" render fine; "10,000" came out
  "1000" and "82%" once dropped to "2%" (re-roll fixed the 2-digit one; 5-digit stayed broken).
  So: keep stat cards ≤2 digits + %, and for big narrative numbers ("10,000 years") make the beat a
  SCENE instead (an ancient hand planting the first seed) rather than a number card — or overlay the
  number in post. A distant/prominent human in an ATMOSPHERE beat can also drift realistic; if a beat
  needs a clear figure, mark it CHARACTER so it gets the pinned doodle style.
- Occasional faint texture/grass squiggles in landscapes — acceptable at video speed.

---

## History — why the previous direction was replaced (2026-06-28)
- **krea2-turbo (thick marker)**: cfg 1 → negatives inert → shadows/texture crept in; strong big-figure bias;
  couldn't render digits. Replaced by z-turbo (thin lines, clean white).
- **"tiny figure / lots of empty space"** made thin-line art look disproportionate → switched to balanced
  MEDIUM-LARGE sizing.
- **Single `STYLE_BLOCK` describing the figure** got a stick figure injected into B-ROLL/landscapes → split into
  `BASE_STYLE` + `CHARACTER_STYLE`.
- **Ambiguous "thin line body"** gave inconsistent characters (outlined vs single-line) → pinned the outlined-body
  character with "always the same character."
