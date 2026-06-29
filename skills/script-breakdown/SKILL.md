# script-breakdown — Viral-format script writer + (post-audio) per-phrase breakdown

Turn a topic (or Thai notes from Nuay's real life) into ONE flowing English narration in the
reverse-engineered **Zen format**, shaped by **HEIGHT as a whole-clip arc** (not rigid chunks).

> ⚠️ **WORKFLOW IS TWO PHASES, SPLIT BY THE AUDIO.** The scene breakdown does **NOT** happen while
> writing the script. It happens **AFTER** Nuay records the voice, driven by the **real Whisper
> timestamps** — because the only correct phrase boundaries are the ones the audio actually speaks.
> Pre-guessing scenes at script time and force-aligning them to audio later is WRONG (it drifts).

```
PHASE A  (this skill, first run)         PHASE B  (after Nuay returns audio)
─────────────────────────────────       ─────────────────────────────────────
topic → research → write narration       audio → Whisper timestamps
      → save script.txt/json                   → segment scenes FROM the audio
      → STOP. hand off to Nuay.                → write 1 image-prompt per phrase
        (he records the voice)                 → hand off to ComfyUI batch
```

> 🎯 North star = **long-form** (~8 min — the format that earns watch-hours / money). Short form is
> the validation step. Both via `--length`.

## Model guidance (READ FIRST)
- **PHASE A — narration writing = use Opus.** It is the creative core (emotion, rhythm, the Zen
  hook). Sonnet is not reliable enough here. Do not write the script on Sonnet.
- **PHASE B — mechanical (run Whisper, segment scenes, write image prompts, drive ComfyUI) = use
  Sonnet** to save Pro/Opus quota. These follow fixed templates and locked style; Sonnet is fine.

## Invoke
```
/script-breakdown "topic or Thai notes"
/script-breakdown notes/today.md

Options (append after the topic):
  --length  short | long      default short (~90s, 1 pillar). long = ~8 min, 3 pillars.
  --research none | light | deep
        default light. none = experience only; light = 1 real stat; deep = 2-3 real stats.
        If --length long and --research is not given, default to deep.
```
Working directory: `C:\Users\Darks\Documents\2026 YT Short Project\`

---

# PHASE A — Write the narration, then STOP

## A1 — Read input & options
- If the argument ends in `.md`, Read it (Thai is fine). Otherwise treat the string as the topic.
- Parse `--length` (default `short`) and `--research` (default `light`; `deep` if length=long and unset).

## A2 — Load references
- Read `docs/format-spec.md` — the Zen format (hook 4-beats / 3 pillars / transitions / authority / close).
- **Persona (first person — this IS Nuay, not a character):** wakes before sunrise to tend vegetables
  with his parents on their organic farm (ผักประสานใจ) in rural Thailand; practices daily vipassana
  (sampajañña — continuous clear awareness); teaching himself AI/coding from scratch. Audience:
  English-speaking "simple living / self-improvement" (US, UK, Australia).

## A3 — Research REAL evidence (amount = `--research`)
- `none` → skip. `light` → 1 genuine stat/study. `deep` → 2-3 (for long-form, ~1 per pillar).
- Each anchor needs: source/researcher + year + institution or journal + a specific number.
- ⚠️ **REAL ONLY.** Use web search and verify. NEVER invent a study, number, or name. If nothing
  solid is found, tell Nuay and offer to write it experience-only.

## A4 — Write ONE flowing narration (HEIGHT arc × Zen mechanics)
Continuous spoken English — NO beat labels, NO stage directions, NO scene numbers in the text.
HEIGHT is the emotional arc of the WHOLE piece, blended with `format-spec.md`:

**short (~90s):** Hook (4-beat, compressed: immersive 2nd-person moment → contrarian pivot →
central question → one-line promise) → core idea + the real stat (authority) → ONE sensory scene
from Nuay's real life → quiet takeaway + **callback to the opening image**.

**long (~8 min):** Hook (4 beats) → **3 pillars** (each: transition sentence → real anchor → a
Nuay-life illustration → one memorable line) → close (reframe + 3-beat recap + callback).

Personal experience = the heart; the researched stat(s) = the authority. Short declarative sentences,
second person where it fits, present tense, calm/awe-building, no emojis.

## A4b — Kill the AI tells (genre-tuned anti-slop)
A script that reads like ChatGPT is what gets a faceless channel dismissed as "AI slop"
and hurts both retention and monetization review. But the Zen format *wants* some
heightening — do not strip it flat. Cut the tells, keep the voice.

**REMOVE always:**
- **Em dashes (—).** They leak into the .srt captions. Use a period or "and".
- **Throat-clearing openers:** "Here's the number that…", "Here's the thing", "The truth is",
  "What's fascinating is". Cut straight to the fact.
- **Intensifiers / adverbs:** very, really, simply, truly, incredibly, just. Delete — let the
  noun and verb carry the weight ("hard to count" > "very hard to count").
- **Inanimate agency:** "the data tells us", "the decision emerges". Name who acts.

**USE SPARINGLY — max ONCE per script each (potent, but formulaic in bulk):**
- "Not X. It's Y." contrast.
- Negative listing ("Not a paycheck. Not on time.").
- Three-fragment staccato ("The land is aging. The children left. So who grows it?").
- A pull-quote closing line.

**KEEP — this is the Zen voice, not slop:**
- One rhetorical-question pivot per section.
- One anaphora triad for rhythm ("We told them… We told them… We never told them…").
- The closing callback to the opening image.

**Final check:** read the draft out loud. If a line sounds like a LinkedIn post, rewrite it
as something Nuay would actually say standing in a field at 5am.

## A5 — Length check
Count words. short: warn if <170 or >260. long: warn if <1000 or >1600.
est_duration_sec = round(words / 2.5). Show the warning and wait if triggered.
> Nuay may cap length for TTS-credit reasons — honor an explicit word target over these defaults.

## A6 — Display the NARRATION ONLY (no breakdown here)
```
NARRATION (read aloud / feed to TTS):
[full flowing narration]

Words: N | Est: ~Ns | Length: short/long | Research: level
Real source(s): <citation(s)>
```
> Do **NOT** print a numbered phrase/scene table in Phase A. Scenes come from the audio in Phase B.

## A7 — Confirm
`Save? [y / n / e = edit narration first]` — wait. On `e`, take the edited narration, recount (A5), save.

## A8 — Save to `output/<slug>/` (slug = lowercase topic, spaces→hyphens, punctuation removed)
- `script.txt` — clean narration only (for recording / TTS). No labels, no trailing whitespace.
- `script.json`:
```json
{
  "slug": "...", "topic": "...", "length_mode": "short|long", "research_level": "none|light|deep",
  "narration": "...",
  "sources": ["researcher, year, institution — the real stat"],
  "word_count": 0, "est_duration_sec": 0
}
```
> No `phrases` / `scene_count` here — those are NOT decided yet. They are produced in Phase B from
> the real audio. (A provisional split, if ever shown, is throwaway and never saved.)

## A9 — Hand off and STOP
```
✅ Saved: output/<slug>/script.txt, script.json
Next (you): record script.txt IN YOUR OWN VOICE (a calm, slow read — your accent is the brand,
not a flaw). Drop the .mp3/.wav into output/<slug>/, then tell me and I'll run Phase B.
> Why your real voice: it is the one asset no competitor can clone, the strongest authenticity
> signal for YouTube's anti-"inauthentic content" review, and it removes the synthetic-media
> disclosure question. AI TTS (VoiceBox / Google AI Studio) only as a stopgap while you build
> the habit — and if you do use it, tick YouTube's altered-content disclosure on upload.
```
Then **stop**. Do not run Whisper, do not invent scenes, do not generate images. If you have a genuinely
useful idea (a stronger hook, a better stat, a thumbnail/title angle), offer it briefly. Ask if anything
is unclear. Otherwise wait for Nuay's audio.

---

# PHASE B — After Nuay returns the audio: breakdown FROM the audio

> Trigger: an audio file exists in `output/<slug>/` and Nuay says to continue. Prefer **Sonnet** here.

## B1 — Whisper timestamps + audio-driven scene segmentation
Run (uses the project's `ml-env` Python, which has faster-whisper):
```
ml-env\Scripts\python.exe scripts\whisper_phrases.py "<audio path>" <slug>
```
This writes:
- `words.json` — every word with start/end (reference).
- `scenes.json` — **phrases segmented from the audio itself** (punctuation + real pauses), one timed
  scene per phrase. This is the DEFINITIVE breakdown. It does **not** read any pre-split phrase list.

Review the printed report: audio duration, scene count, and that **no scene has zero/negative duration**.
Show Nuay the scene list (or a summary) so he can sanity-check the segmentation before images.

## B2 — Write one image prompt per scene → `scene_prompts.json`
- Read `docs/visual-style.md` (locked style) for the rules + negatives.
- For EACH scene in `scenes.json`, write a `visual` that **faithfully depicts that phrase's meaning**
  (FAITHFULNESS FIRST — if someone saw the image without the caption, they should guess the phrase).
- Mix shot types for variety (~40% B-ROLL / ~30% CHARACTER / ~30% ATMOSPHERE):
  - **CHARACTER** — the stick figure actively doing the action.
  - **B-ROLL** — an object / stat card / chart / icon (no figure).
  - **ATMOSPHERE** — a wide landscape / setting, figure tiny or absent.
- Aspect: match the clip. **9:16** for Shorts, **16:9** for long-form (the STYLE_BLOCK in
  `comfy_run.py` and `assemble_clip.py --landscape` must agree).
- Schema (one object per scene, same `scene` numbers as `scenes.json`):
```json
[{ "scene": 1, "phrase": "...", "shot_type": "B-ROLL|CHARACTER|ATMOSPHERE", "visual": "..." }]
```
> **Faithfulness on numbers:** when a phrase states a statistic, make its scene a clean
> B-ROLL number/chart card ("58", "40%", a simple pie) so the viewer *sees* the fact and the
> authority beat lands. (z-turbo renders digits imperfectly — overlay the number in post if needed.)
> **Watch pacing:** a single still held >~8s drags. If a phrase runs that long, add a second
> visual element or have Nuay read it with a cut. (Future upgrade: a slow Ken Burns push-in in
> assembly would soften static holds globally.)

## B2c — Breathing room (intro / outro) — automatic in assembly
These come from `assemble_clip.py`; do NOT time them in scenes.json:
- **Lead-in ~1s** — frame 1 shows before the voice starts (the viewer settles in).
- **Outro ~2.5s** — a final frame holds in silence after the voice ends (let it land).
- **Fade** — gentle fade in from black at the start, fade out to black at the end.
Optionally author ONE dedicated **outro visual** (a calm resolution image — e.g. the figure
looking at the horizon, lots of empty space) and save it as `frames/scene_end.png`; assembly
holds THAT through the outro instead of freezing the last narration frame. Tune per clip with
`--lead-in` / `--outro`.

## B3 — Captions + images + assembly
- **Captions (sidecar, do NOT burn in):** `python scripts/make_srt.py <slug>` → `output/<slug>/<slug>.srt`.
  Upload it in YouTube Studio → Subtitles. Keep a CORRECTIONS map in `make_srt.py` for Whisper mishears.
- **Images:** `python scripts/comfy_run.py --slug <slug> --batch`  (skips existing frames)
- **Assemble:** `python scripts/assemble_clip.py <slug> [--landscape]`  (16:9 → `--landscape`)
```
ComfyUI open → python scripts/comfy_run.py --slug <slug> --batch
then          → python scripts/make_srt.py <slug>
then          → python scripts/assemble_clip.py <slug> [--landscape]
```

---

## Cost map per clip
- **Script writing** (Phase A): **Opus** — creative, worth the quota.
- **Voice:** Nuay's own (VoiceBox / Google AI Studio) — free.
- **Timestamps + segmentation + image prompts + assembly** (Phase B): **Sonnet** + local tools — cheap/free.
- **Images:** local ComfyUI on the RTX 5070 (free). ~30-50 imgs (short), ~70-90 (long). ~19-35s/img.

---

## Monetization guardrails (keep the channel eligible)
YouTube de-monetizes faceless channels under its **"inauthentic / repetitious content"** policy,
not for using AI. This project's defense is real: a real person's life + real, cited stats. Protect it.
- **Voice = Nuay's own** (see A9). The single biggest authenticity signal and the hardest thing to copy.
- **Music = cleared only.** YouTube Audio Library or owned tracks. A Content-ID claim on a random
  track (e.g. "Way Back Home") diverts the ad revenue or blocks the video — verify before every upload.
- **No mass-production look.** One genuine point of view per video. Never re-skin the same script with
  a new topic; vary the hook and structure. Quantity-farming is exactly what the policy targets.
- **Stats stay REAL and cited** (enforced in A3). One fabricated number that gets caught kills trust.
- **YPP bar to aim for:** 1,000 subscribers + 4,000 public watch-hours/12mo (long-form) OR 10M Shorts
  views/90 days. Long-form watch-hours are the realistic path here — which is why long-form is the north star.
