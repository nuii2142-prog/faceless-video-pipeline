# script-breakdown — DRAFT for review (not yet installed)

> This is a draft of `~/.claude/skills/script-breakdown/SKILL.md`.
> Read it, mark anything you want changed, then I'll install it. Nothing is live yet.

---

# script-breakdown — Viral-format script writer + per-phrase breakdown

Turn a topic (or Thai notes from Nuay's real life) into ONE flowing English narration that
follows the **extracted Zen format**, shaped by **HEIGHT as a whole-clip arc** (not rigid
chunks), then break it into **per-phrase scenes** — one future image per phrase.

This skill does the SCRIPT stage only. Voice, images, and assembly are done manually afterward.

## Invoke

```
/script-breakdown "topic or Thai notes"
/script-breakdown notes/today.md
/script-breakdown "topic" --length long      # 8-min, 3-pillar long-form (default is 90s short)
```

**Working directory:** always `C:\Users\Darks\Documents\2026 YT Short Project\`

---

## Step 1 — Read input & length

- If the argument ends in `.md`, Read that file (Thai is fine). Else treat the string as the topic.
- `--length`: `short` (default) = ~90s, ~200–230 words, 1 pillar. `long` = ~8 min, ~1,300 words, 3 pillars.

## Step 2 — Load the references

- Read `docs/format-spec.md` — the Zen format (hook 4-beats, pillars, transitions, authority, close).
- Read `docs/visual-style.md` — for later image work (not used to write the script; just confirm it exists).
- **Persona (first person — this IS Nuay, not a character):** Nuay wakes before sunrise to tend
  vegetables with his parents on their organic farm (ผักประสานใจ) in rural Thailand. Daily vipassana
  (sampajañña — continuous clear awareness). Teaching himself AI/coding from scratch. Audience:
  English-speaking "simple living / self-improvement" (US, UK, Australia).

## Step 3 — Research REAL evidence (your "personal + real stats" choice)

Find genuine evidence that fits the topic, to give the script Zen-style authority:
- **short:** 1 real study/stat. **long:** 1 real anchor per pillar (3 total).
- Each anchor needs: researcher/source + year + institution/journal + a specific number.
- ⚠️ **REAL ONLY.** Use web search to verify. NEVER invent a study, number, or name. If nothing solid
  is found, tell Nuay and offer to write it experience-only instead of faking a citation.

## Step 4 — Write ONE flowing narration

Write continuous spoken English — NO beat labels in the text, NO stage directions. HEIGHT is the
emotional arc of the WHOLE piece, blended with the Zen mechanics from format-spec.md:

**short (~90s) arc:**
1. **Hook (H)** — Zen 4-beat hook, compressed: immersive 2nd-person present moment → contrarian
   "but for most of history / most people…" pivot → the central question → a one-line promise.
2. **Explain (E)** — the core idea, anchored by the 1 real stat (authority).
3. **Illustrate (I)** — ONE concrete, sensory scene from Nuay's real life (farm / meditation /
   coding). Smell, sight, sound. This is where personal experience carries the meaning.
4. **Teach (T)** — one quiet, non-preachy takeaway, then a **callback to the opening image**.

**long arc:** Hook (4 beats) → **3 pillars** (each = transition sentence → real anchor → a
Nuay-life illustration → one memorable line) → close (reframe + 3-beat recap + callback).

**Language rules (read aloud by you / TTS):** short declarative sentences; second person where it
fits; present tense for immediacy; calm, awe-building, not hype; no emojis/hashtags.

## Step 5 — Break into per-phrase scenes (the "breakdown")

Split the finished narration into natural spoken phrases (~3–10 words, ≈1.5–3s each) — the way you'd
pause if reading it aloud. Number them 1..N. **Each phrase = one future image.**

> Note: these phrase splits are PROVISIONAL planning units. The definitive split comes from Whisper
> after you record the audio (same as the reference video). This preview just shows the
> overall → per-phrase shape and lets you sanity-check image count.

## Step 6 — Length check

Count words in the full narration.
- short: warn if <170 (`hook may feel thin`) or >260 (`will run over ~100s`).
- long: warn if <1,000 or >1,600.
Estimate duration = round(words / 2.5) seconds. Show the warning and wait if triggered.

## Step 7 — Display

```
NARRATION (read this aloud / feed to TTS):
[full flowing narration — no labels]

──────────────── BREAKDOWN (N scenes) ────────────────
 1 | [phrase text]
 2 | [phrase text]
 ...
Words: N | Est. duration: Ns | Scenes: N | Real source used: <citation>
```

## Step 8 — Confirm

Print exactly: `Save? [y = save / n = discard / e = I'll edit narration first]` and wait.
- **y** → Step 9. **n** → `Discarded.` stop. **e** → take edited narration, re-split (Step 5),
  recount, then save.

## Step 9 — Save

Slug = lowercase topic, spaces→hyphens, punctuation removed. Write into `output/<slug>/`:
- `script.txt` — clean narration only (for recording / TTS). No labels, no trailing whitespace.
- `breakdown.md` — the numbered phrase table + the real source citation at the bottom.
- `script.json`:
```json
{
  "slug": "...", "topic": "...", "length_mode": "short|long",
  "narration": "...", "phrases": ["phrase 1", "phrase 2", "..."],
  "source": "researcher, year, institution — the real stat used",
  "word_count": 0, "scene_count": 0, "est_duration_sec": 0
}
```

## Step 10 — Report & next step

```
✅ Saved: output/<slug>/script.txt, breakdown.md, script.json
Next (manual): record yourself reading script.txt → drop the .wav in output/<slug>/ →
then we run Whisper for real per-phrase timestamps → then generate 1 image per phrase.
```

---

## What changed vs the old /faceless-short (why this fixes the broken output)

- **HEIGHT is now one arc, not 4 fixed beats → 4 images.** Narration flows; images come from
  phrase-level splits (~30–50 for 90s), matching how the reference channel actually does it.
- **Grounded in a real extracted format** (`format-spec.md`), not an invented framework.
- **Authority from real, researched stats** + Nuay's lived experience.
- **Length is a setting** (90s Short now / 8-min long-form later) instead of hard-coded ~35s.
