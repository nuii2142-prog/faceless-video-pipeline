# Visual Style — Faceless Shorts (Soil & Signal identity, thin-line doodle)

Locked style for EVERY image in a clip, so the whole video looks consistent.
**Updated 2026-07-09** — "Soil & Signal identity" overhaul: the world is now explicitly rural
Thailand, the character gets a signature woven farmer hat (งอบ), and one reserved amber-gold
accent encodes the channel name into every frame. Goal: turn "consistent" into "recognizable" —
a viewer should know whose frame this is before any text appears.

## 🇹🇭 The identity system (v4, 2026-07-09 — content moved OUT of BASE_STYLE)

**The architecture rule that everything else hangs on: BASE_STYLE says HOW to draw (line, palette,
fill); each beat's `visual` says WHAT to draw (setting, props, camera).** v3.x put the world-cues
menu in BASE_STYLE and cfg-1 stamped the same road/jar/banana composition onto every frame —
including bedroom and laptop scenes (Nuay's exact complaint). Same failure class as the stray
gold digits. Content nouns in an every-frame block WILL appear in every frame.

| Element | Rule | What it buys |
|---|---|---|
| **Soil** (world) | Every place beat names ONE setting from the location menu below (drawn from Nuay's real farm photos in `farm view Ref/`) — the setting must MATCH the line's meaning: sleep happens in the room, work at the under-house table, harvest in the rows. | Frames tied to the real 30 rai, and the setting varies because the story moves, not because props got shuffled. |
| **Signal** (accent) | ONE reserved accent: deep warm **amber-gold** — the sun and dawn glow; stat beats write "large deep amber-gold number NN%" into their own `visual`. ⚠️ Never put a draw-the-number instruction in BASE_STYLE (v3/v3.1 tests: stray gold digit on nearly every frame). | Stat frames become brand-recognizable. The name "Soil & Signal" is literally in the palette. |
| **Character** | **Cute round big-head chibi** (locked 2026-07-11): a LARGE round white head with a soft, slightly UNEVEN hand-drawn wobble (not a perfect circle — the imperfection IS the cuteness), a SMALL soft rounded body (short, a little chubby, huggable — NOT tall/lanky/slim), MEDIUM line weight (some presence, not a hairline, not thick marker). | A silhouette that is OURS and reads "aww" instantly. Round + hand-wobble = endearing; a slim/tall version tested as "โย่ง" (lanky) and was rejected. |
| **Hat = story prop** | The conical farmer hat is NOT always on. It appears in farmer beats (waking as himself, returning to the soil, parents, lifting it, home) and comes OFF during the city/chasing-money beats (leaving the farm, direct-sales, trading, "I was ordinary", night rest). | The hat leaving and returning tracks his identity arc — a detail viewers feel without naming. Also fixes "hat on every frame" monotony. |
| **Horizon** | Farm wide shots end in **low forested hills** (the real valley) or a wall of trees — NEVER a city skyline. A city skyline appears ONLY in city/contrast beats, where it IS the point. | Kills the odd "Bangkok behind the paddies" clash; hills become a recognizable backdrop. |

### 📍 Location menu (from `farm view Ref/` — pick per beat, match the meaning)
- **Plowed beds** — freshly turned DARK soil beds, a banana clump at the edge, wall of dense trees behind.
- **Vegetable rows** — low green rows with thin drip-irrigation lines, straw mulch, simple bamboo trellis fences (climbing beans).
- **Sprinkler dawn** ⭐ signature — arcs of fine water mist over the rows, backlit amber by the rising sun, hills behind.
- **Rice paddy** — flooded paddy with young seedlings in neat rows, hills on the horizon.
- **Yellow cover-crop field** — a whole field of small yellow flowers (sunn hemp), hills behind.
- **Stilt house** — wooden house with corrugated roof half-hidden by big trees and bamboo; grassy two-track path curving in; a farm dog somewhere.
- **Under-house workspace** — the open-air space beneath the stilt house: wooden table, plastic chairs, baskets, hand tools.
- **Interior room** — plain wooden room: plank walls AND floor visible, woven sleeping mat, one window with a thin curtain. Interiors stay interiors.
- **Village lane** — small CONCRETE lane beside a tall banana grove, power poles and sagging wires, morning light.
- **Farm dog** — allowed as a small recurring life detail in any outdoor beat.

### 🎥 Camera menu (vary per beat — this is what kills the "same frame, swapped props" look)
wide establishing · medium action · close-up on hands/object · extreme close-up face ·
**overhead top-down (the plots as a quilt — great for scale/"30 rai" beats)** · POV (viewer's own
hands) · low angle looking up · over-the-shoulder. Consecutive beats must change SETTING or
CAMERA TIER (ideally both); no setting appears more than ~3 times per short unless it's a
planned callback.

**Updated 2026-06-28** after a 3-model A/B/C test (krea2 / flux2 / z-image). The thin-line
direction below is the current house style; superseded blocks are kept at the bottom as history.

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

**`BASE_STYLE` — appended to EVERY scene (never mentions a person). Current text lives in
`scripts/comfy_run.py`; the load-bearing parts:**
> Thin clean black pen lines (NOT thick/heavy/marker) · the story's world is RURAL THAILAND at first
> light (place scenes get 1-2 Thai countryside cues; city scenes read as a busy modern Thai city) ·
> palette = tropical greens (yellow-green → banana-leaf), warm red-brown earth/terracotta, soft cream,
> pale peach-to-blue dawn sky · ONE reserved accent = deep warm AMBER-GOLD (sun + dawn glow only in
> the every-frame sentence) · **one soft light source per scene with gentle two-tone CEL shading**
> (flat poster shapes; still NO airbrush gradients, NO fuzzy shadows, NO 3d, NO paper texture — grain
> comes from the grade pass) · a FEW well-chosen supporting details, then let the frame BREATHE
> (calm open areas; backgrounds muted/hazy so the white character is always the brightest thing) ·
> object/icon/stat beats = clean and simple, little or no background (the amber-gold number treatment
> is written into each stat beat's `visual`, NOT here) · subject MEDIUM-LARGE inside a safe area ·
> 16:9 landscape composition (batch flag flips to 9:16).

> Character stays plain WHITE (color goes into environments/objects only) — rich-ish Thai landscape +
> simple white character is the intended contrast.
> Batch flags: `batch_zturbo.py <slug> [--only 5,7,8] [--tag test]` (`--tag` writes to `frames_<tag>/` for A/B style tests; `--only` to re-roll specific scenes).

**`CHARACTER_STYLE` — appended ONLY when `shot_type == "CHARACTER"` (pins one consistent character):**
> The person is ALWAYS the exact same character, drawn identically in every image: a round WHITE head with a
> minimal face (two small black dot eyes, thin eyebrows, one small curved mouth), and a simple slim body with a
> clean thin OUTLINE — a narrow rounded torso with thin outlined arms and thin outlined legs (a soft cartoon
> stick figure with a lightly outlined body, NOT a single bare line, NOT a filled silhouette).
> **Cute round big-head chibi (locked 2026-07-11):** a LARGE round white head with a soft, slightly
> UNEVEN hand-drawn roundness (NOT a perfect circle — the little wobble is the cuteness), a SMALL soft
> ROUNDED body (short, a little chubby, huggable — NOT tall, NOT lanky, NOT slim/grown-up), and a
> MEDIUM even line weight (a bit heavier than a hairline = presence; not thick marker). Readability
> comes from the bright-white fill against muted graded backgrounds.
> **The EXPRESSION acts the story** — eyes close in peace / curve into a smile / widen; brows tilt;
> the small mouth smiles, falls flat, or opens.
> **The hat is NOT in CHARACTER_STYLE** (⚠️ any hat clause there = a hat on every frame, and "worn OR
> resting" = two hats, verified). It is added ONLY by the per-beat `visual` that wants it, as a story
> prop (see the "Hat = story prop" row above). When it appears it's the same wide conical woven bamboo
> farmer hat in pale straw-tan.
> Always the same round head, same small soft body, same medium line.

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
- **Any draw-instruction in BASE_STYLE fires on EVERY frame** (cfg 1 = no conditionals). Both
  "amber-gold for…numbers" (accent sentence) and "for a statistic beat, draw the number LARGE…"
  (a 'conditional' sentence) stamped a random gold digit on nearly every test frame (2026-07-09,
  v3 + v3.1). The passive old sentence "for a plain object, icon, number or stat card, keep it
  clean…" does NOT leak — describing how to treat a thing is safe, commanding that a thing be
  drawn is not. Brand treatment for stat numbers therefore lives in the per-beat `visual` text
  (SKILL.md B3), never in BASE_STYLE.
- **Isolated body parts fail.** A "feet only" beat rendered as a white mound, then as two puppies
  (v4 tests). For a body-part beat, keep the whole character in frame and pose him instead (e.g.
  "bending forward, head down, looking at his own bare feet") — the pinned character + pose reads
  the same meaning and never breaks.
- **Dark scenes render bright by default** (the warm dawn palette pulls everything to morning).
  For night/pre-dawn beats spell it out: "night scene, deep dark navy-blue, black silhouettes,
  faint moonlight, only a pale glow at the horizon" — that phrasing worked (v4 scenes 1, 18, 30).
- **City beats fight the rural default.** BASE_STYLE grounds place scenes in countryside cues, so a
  "city buildings behind" prompt comes out as paddies with a skyline. For a real city beat, write the
  visual as "in the middle of a dense modern Thai city street, tall buildings on every side, no
  fields" — surround the figure with the city so the rural default has nowhere to land.

---

## History — why the generic-countryside style was replaced (2026-07-09)
- The 2026-06-28 "lively" style was consistent but **placeless** — contact sheets read as generic
  Western meadow (could be Iowa), while the brand is a Thai organic farmer on 30 rai. Backgrounds
  now carry Thai cues, the character carries the hat, and amber-gold is reserved as the signature
  accent. Same thin-line/flat-fill mechanics, so all 2026-06-28 model findings still apply.
- The "morning-before-the-sun-short" contact sheet also showed 5 near-identical "character stands
  in a field" wide shots in the back third → repetition guard hardened in SKILL.md B3b.

## History — why the previous direction was replaced (2026-06-28)
- **krea2-turbo (thick marker)**: cfg 1 → negatives inert → shadows/texture crept in; strong big-figure bias;
  couldn't render digits. Replaced by z-turbo (thin lines, clean white).
- **"tiny figure / lots of empty space"** made thin-line art look disproportionate → switched to balanced
  MEDIUM-LARGE sizing.
- **Single `STYLE_BLOCK` describing the figure** got a stick figure injected into B-ROLL/landscapes → split into
  `BASE_STYLE` + `CHARACTER_STYLE`.
- **Ambiguous "thin line body"** gave inconsistent characters (outlined vs single-line) → pinned the outlined-body
  character with "always the same character."
