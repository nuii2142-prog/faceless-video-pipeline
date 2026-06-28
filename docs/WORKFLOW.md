# Soil & Signal — Faceless Video Pipeline (working manual)

Last updated 2026-06-28. This is the full, repeatable process for turning a topic into a
finished 16:9 YouTube video in the thin-line doodle style.

---

## 0. The big picture

```
TOPIC ──(Opus)──> SCRIPT ──(you record)──> VOICE ──(Whisper)──> SCENES
   └─(Claude)─> IMAGE PROMPTS ─(z-turbo)─> 62 IMAGES ─(FFmpeg)─> VIDEO + SUBTITLES + SEO
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
     ├─ words.json / scenes.json      (Whisper)
     ├─ scene_prompts.json            (image prompts, 1 per scene)
     ├─ frames/scene_NN.png           (generated images)
     ├─ <slug>.srt                    (subtitles)
     └─ final.mp4
```

---

## 2. PHASE A — write the script  (model: **Opus**)

```
/script-breakdown "your topic"  --length long --research deep
```
- Claude researches a REAL stat, writes the narration (Zen format), saves `script.txt` + `script.json`, then **stops**.
- You review, then **record the voice** (VoiceBox / Google AI Studio / ElevenLabs) and drop the audio file into `output/<slug>/`.

> Length control: long ≈ 1,200 words (~8 min). You can cap it — see FAQ on character count.

---

## 3. PHASE B — build the video  (model: **Sonnet** is fine)

Run from the project root. Use `ml-env\Scripts\python.exe` for steps that need Whisper/Pillow.

**3.1 Timestamps + scenes (audio-driven):**
```
ml-env\Scripts\python.exe scripts\whisper_phrases.py "output\<slug>\<audio>.mp3" <slug>
```
→ writes `words.json` + `scenes.json` (phrases come from the real audio, not a guess).

**3.2 Image prompts:** Claude writes `output/<slug>/scene_prompts.json` — one entry per scene:
`{"scene": N, "phrase": "...", "shot_type": "CHARACTER|B-ROLL|ATMOSPHERE", "visual": "..."}`
(See `docs/visual-style.md` for the rules. Style is auto-appended; don't put style in `visual`.)

**3.3 Generate images (z-image-turbo, ~27 min for 62):**
```
python scripts\batch_zturbo.py <slug>
```
- Skips existing frames (resumable). Fixed seed 42 for consistency.
- Re-roll one bad scene: `python scripts\batch_zturbo.py <slug> --only 43 --seed 7`
  (delete `frames\scene_43.png` first, or it skips it).
- A/B a style change without touching the real frames: `--tag test` → writes to `frames_test/`.

**3.4 Subtitles:**
```
python scripts\make_srt.py <slug>
```
→ `output/<slug>/<slug>.srt` (upload separately to YouTube; not burned in).

**3.5 Assemble:**
```
ml-env\Scripts\python.exe scripts\assemble_clip.py <slug> --landscape --music "SFX\<track>.mp3"
```
- `--landscape` = 1920×1080 (drop it for 9:16 Shorts).
- `--music` = optional; loops + mixes under the voice at 12% (edit `MUSIC_VOL` in the script to change).

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
#   (Claude writes scene_prompts.json)
python scripts\batch_zturbo.py <slug>
python scripts\make_srt.py <slug>
ml-env\Scripts\python.exe scripts\assemble_clip.py <slug> --landscape --music "SFX\<track>.mp3"

# Re-roll one scene
python scripts\batch_zturbo.py <slug> --only <N> --seed <new>
```
