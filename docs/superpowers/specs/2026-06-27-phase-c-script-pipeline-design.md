# Phase C: Script Pipeline Design
_Date: 2026-06-27_

## What Phase C Does

Takes a topic or Thai notes → Claude (inside the skill) writes a 4-beat HEIGHT-framework English script → writes two output files for downstream phases.

No external LLM API call needed. Script generation happens entirely within Claude Code (uses Claude Pro subscription already paid for).

---

## HEIGHT Framework (4 beats)

| Beat | Purpose | Target length |
|------|---------|--------------|
| **H**ook | Contrarian/surprising opening — stops scroll in 3s, concrete, not generic | 1–2 sentences |
| **E**xplain | Unpack the hook — why it's true | 2–3 sentences |
| **I**llustrate | One sensory example from Nuay's real life (farm / meditation / coding) | 2–3 sentences |
| **T**each | One simple actionable insight — calm, don't overwhelm | 1–2 sentences |

**Total target:** ~90–120 words, ~35–45 seconds at TTS pace.

---

## Character Persona (baked into Claude prompt)

- **Voice:** First-person Nuay — Thai organic farmer, vipassana practitioner, self-taught coder
- **Audience:** English "simple living / self-improvement" — US/AU/UK
- **Tone:** Calm, grounded, authentic. Not motivational-speaker energy.
- **Language rules:** Short sentences (TTS-friendly). No emojis, no hashtags, no beat labels ("Hook:", etc.), no stage directions. Clean spoken English only.

---

## Input

```
/faceless-short "topic or Thai notes here"
```

Or, for longer notes:

```
/faceless-short notes/today.md
```

Claude reads the topic/file and generates the script in one pass.

---

## Output Files

Both written to `output/<slug>/` (slug = kebab-case topic):

| File | Contents | Used by |
|------|---------|---------|
| `script.json` | Structured beats: `{ hook, explain, illustrate, teach, narration, word_count, est_duration_sec }` | Phase F (image direction, future) |
| `script.txt` | `narration` field only — 4 beats joined, clean spoken text | **Phase D (TTS)** immediately |

`narration` = the 4 beats concatenated with single newlines. This is the direct handoff to voice.

---

## How It Fits in the Pipeline

```
/faceless-short "topic"
    ↓
[Phase C] Claude writes HEIGHT script
    → output/<slug>/script.json
    → output/<slug>/script.txt
    ↓
[Phase D] TTS reads script.txt → audio.wav
    ↓
[Phase E] Whisper timestamps audio.wav → timestamps.json
    ↓
[Phase F] Gemini generates doodle images per timestamp (9:16 vertical)
    ↓
[Phase G] FFmpeg assembles → final.mp4
```

---

## File Structure Created

```
output/
  <slug>/
    script.json     ← structured beats
    script.txt      ← clean narration for TTS

notes/
  _template.md      ← blank template for writing Thai notes

skills/
  faceless-short/
    SKILL.md        ← the Claude Code skill definition (Phase C lives here)
```

---

## Skill Behaviour (SKILL.md contract)

When invoked, Claude will:
1. Accept topic string or `.md` file path as argument
2. Read the notes if a file path is given
3. Generate the HEIGHT script using the persona + rules above
4. Print the script to screen for user review
5. Ask: "Save this? [y/n/edit]" — on y, write both output files
6. Report: `✅ script.txt ready for Phase D`

No file is written without user confirmation.

---

## Sanity Checks (inline, no frameworks)

- word_count < 80 → warn "script too short, hook may be weak"
- word_count > 140 → warn "script too long, TTS will exceed 60s"
- Any beat is empty → error before writing files

---

## Out of Scope for Phase C

| Feature | Add when |
|---------|---------|
| Search grounding via Gemini | Hooks feel generic after 10+ clips |
| 3-candidate hook selection | Quality bar demands it |
| Auto image-direction hints per beat | Phase F architecture is settled |
| Batch mode (multiple topics) | Single-clip pipeline is proven end-to-end |
