# Soil & Signal — Faceless Video Pipeline (working manual)

Last updated 2026-06-28. This is the full, repeatable process for turning a topic into a
finished 16:9 YouTube video in the thin-line doodle style.

---

## 0. The big picture

```
TOPIC ──(Opus)──> SCRIPT ──(you record)──> VOICE ──(Whisper)──> PHRASES (captions)
   └─(Claude)─> VISUAL BEATS + IMAGE PROMPTS ─(z-turbo)─> ~120 IMAGES ─(FFmpeg)─> VIDEO + SUBTITLES + SEO
```

Two phases, split by the audio:
- **PHASE A — write the script, then STOP.** (creative → best on Opus)
- **PHASE B — after you record the voice: timestamps → scenes → image prompts → images → assemble.** (mechanical → Sonnet is fine)

Everything heavy (images, voice) runs **locally / free**. Claude is only the orchestrator + writer.

---

## 1. Folder layout

```
2026 YT Short Project/
├─ scripts/            ← the pipeline (Python)
├─ docs/               ← visual-style.md (locked style) + this manual
├─ workflows/ , "ComfyUi Api Workflow"/   ← ComfyUI API workflow JSONs
├─ SFX/                ← background music files
├─ ml-env/             ← Python env that has faster-whisper + Pillow
└─ output/<slug>/      ← one folder per video
     ├─ script.txt / script.json     (Phase A)
     ├─ <audio>.mp3                   (you drop this in)
     ├─ words.json / scenes.json      (Whisper; phrases = caption cues)
     ├─ scene_prompts.json            (image prompts, 1 per BEAT — "covers" groups phrases)
     ├─ corrections.json              (Whisper mishears → caption fixes, per project)
     ├─ frames/scene_NN.png           (generated images)
     ├─ contact_sheet.png             (all frames tiled, for the human pass)
     ├─ <slug>.srt                    (subtitles)
     └─ final.mp4
```

---

## 2. PHASE A — write the script  (model: **Opus**)

```
/script-breakdown "your topic"  --length long --research deep
```
- Claude researches a REAL stat, writes the narration (Zen format), saves `script.txt` + `script.json`, then **stops**.
- You review, then produce the voice and drop the audio file into `output/<slug>/`. Options, best first:
  1. **ElevenLabs Professional Voice Clone of your own voice** (trial in progress 2026-07-11) — tick
     the altered-content disclosure on upload.
  2. Record it yourself on the Maono mic (free, no disclosure, strongest authenticity).
  3. **F5-TTS** local clone (`ml-env\Scripts\python.exe scripts\f5_speak.py "voice over\voice 02.wav" output\<slug>\script.txt output\<slug>\voice.wav "voice over\voice 02_transcript.txt"`,
     tuned to speed 0.84 / cfg 1.8 / nfe 85) — ⚠️ Nuay judged the delivery too flat for publishing
     (2026-07-11); emergency fallback only.

> Length control: long ≈ 1,200 words (~8 min). You can cap it — see FAQ on character count.

---

## 3. PHASE B — build the video  (model: **Sonnet** is fine)

Run from the project root. Use `ml-env\Scripts\python.exe` for steps that need Whisper/Pillow.

**3.1 Timestamps + scenes (audio-driven):**
```
ml-env\Scripts\python.exe scripts\whisper_phrases.py "output\<slug>\<audio>.mp3" <slug>
```
→ writes `words.json` + `scenes.json` (phrases come from the real audio, not a guess).

**3.2 Visual beats + image prompts:** Claude groups the phrases into visual beats (3-6s each,
~half the phrase count) and writes `output/<slug>/scene_prompts.json` — one entry per BEAT:
`{"scene": N, "covers": [N, N+1], "phrase": "...", "shot_type": "CHARACTER|B-ROLL|ATMOSPHERE", "visual": "..."}`
- The method (meaning-first devices, anti-icon-slop, motif planning, the human check before
  generating) lives in `skills/script-breakdown/SKILL.md` B2-B3b. Style rules: `docs/visual-style.md`.
- Style is auto-appended; don't put style in `visual`. Whisper mishears go into `corrections.json`.

**3.3 Generate images (z-image-turbo, ~26 s/img → ~1h for a long clip):**
```
python scripts\batch_zturbo.py <slug>
```
- Skips existing frames (resumable), prints a running ETA. Fixed seed 42 for consistency.
- 9:16 Short: add `--portrait` (flips the latent AND the style aspect line together).
- Re-roll one bad scene: `python scripts\batch_zturbo.py <slug> --only 43 --seed 7`
  (delete `frames\scene_43.png` first, or it skips it).
- A/B a style change without touching the real frames: `--tag test` → writes to `frames_test/`.

**3.35 Human pass (cheap insurance before assembly):**
```
ml-env\Scripts\python.exe scripts\contact_sheet.py <slug>
```
→ `output/<slug>/contact_sheet.png` — every frame tiled with its scene number. Eyeball it,
re-roll the misses with `--only`.

**3.4 Subtitles:**
```
python scripts\make_srt.py <slug>
```
→ `output/<slug>/<slug>.srt` (upload separately to YouTube; not burned in). Applies
`corrections.json` (per-project Whisper fixes) + a few generic spacing tidy-ups.

**3.5 Assemble:**
```
python scripts\assemble_clip.py <slug> --landscape --ken-burns --music "SFX\<track>.mp3"
```
- `--landscape` = 1920×1080 (drop it for 9:16 Shorts).
- `--ken-burns` = slow breathing zoom on every beat; renders in parallel (`--jobs`, default ~6),
  a long clip finishes in minutes.
- `--music` = optional; loops + mixes under the voice (`--music-vol`, default 12%).

---

## 4. Models (decided 2026-06-28)

| Job | Model | Why |
|-----|-------|-----|
| Images (production) | **z-image-turbo** | thin lines, clean white, ~26 s/img → 27 min/clip |
| Thumbnails / hero stills | flux2-dev or flux2-turbo | prettier but ~2–3 min/img (too slow for full clips) |
| Voice | your own TTS | free |
| Whisper / FFmpeg / prompts | local + Sonnet | free / cheap |

Workflow files + node maps are in `scripts/model_test.py`. To compare models again: `python scripts\model_test.py`.

---

## 5. Style (locked) — see `docs/visual-style.md`
- THIN black pen lines (never thick/marker). Subtle muted flat colors. Mostly white, airy.
- Character = always the same plain WHITE outlined-body figure (consistency pinned). Color goes in environments/objects, not the character.
- Split prompt: `BASE_STYLE` on every scene + `CHARACTER_STYLE` only on CHARACTER scenes (keeps figures out of B-ROLL/landscapes).
- B-ROLL with a number is OK; never ask the model to render words/sentences (it garbles them).

---

## 6. Upload (per video)
1. `output/<slug>/UPLOAD.md` has the paste-ready Title / Description / Tags / settings.
2. Upload `final.mp4`, then upload the `.srt` under Subtitles.
3. Thumbnail: z-turbo base (`thumbnail_prompt.txt`) → add big text in Canva.

---

## 7. Quick command cheat-sheet
```
# Phase A
/script-breakdown "topic" --length long --research deep

# Phase B (after you drop the audio in output/<slug>/)
ml-env\Scripts\python.exe scripts\whisper_phrases.py "output\<slug>\<audio>.mp3" <slug>
#   (Claude groups beats + writes scene_prompts.json + corrections.json, shows you the plan)
python scripts\batch_zturbo.py <slug>
ml-env\Scripts\python.exe scripts\contact_sheet.py <slug>    # eyeball all frames
python scripts\make_srt.py <slug>
python scripts\assemble_clip.py <slug> --landscape --ken-burns --music "SFX\<track>.mp3"

# Re-roll one scene
python scripts\batch_zturbo.py <slug> --only <N> --seed <new>
```
