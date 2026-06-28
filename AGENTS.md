# AGENTS.md — instructions for any AI coding agent working in this repo

This file is the universal entry point. Claude Code, Cursor, Cline, Codex, Gemini/Antigravity,
and other agents read a root `AGENTS.md` (or you can point them here). Start by reading:

1. `docs/WORKFLOW.md` — the full pipeline (how to build a video end to end).
2. `docs/visual-style.md` — the locked image style + prompt rules.
3. `skills/script-breakdown/SKILL.md` — how to write a script from a topic.

## What this project is
A faceless YouTube video pipeline ("Soil & Signal"): a topic becomes a thin-line stickman
doodle explainer video. Heavy work runs locally/free (ComfyUI for images, Whisper for
timing, FFmpeg for assembly, your own TTS for voice). An LLM is only needed for two steps:
writing the narration, and writing one image prompt per scene.

## The two LLM jobs (this is what an agent does here)
- **Write the script** (Phase A): follow `skills/script-breakdown/SKILL.md`. Output a flowing
  English narration in the Zen format with ONE real, verified statistic. Then STOP — the human
  records the voice.
- **Write image prompts** (Phase B): after Whisper produces `scenes.json`, write
  `output/<slug>/scene_prompts.json` — one `{scene, phrase, shot_type, visual}` per scene,
  following `docs/visual-style.md`. Do NOT bake style into `visual`; the scripts append it.

## How to run the pipeline (commands)
See `docs/WORKFLOW.md` §7 for the cheat-sheet. Key scripts in `scripts/`:
`whisper_phrases.py`, `batch_zturbo.py`, `make_srt.py`, `assemble_clip.py`.

## Rules
- Image model = **z-image-turbo** (workflow in `ComfyUi Api Workflow/`). Node map in `scripts/model_test.py`.
- Style = thin black pen lines, subtle muted color, one consistent WHITE outlined-body character.
  Split prompt: `BASE_STYLE` on every scene + `CHARACTER_STYLE` only on `shot_type=="CHARACTER"`.
- Never commit secrets. `.env` holds the API key and is gitignored. Use `.env.example` as the template.
- Never make the image model render words/sentences (it garbles them); short standalone numbers are OK.
