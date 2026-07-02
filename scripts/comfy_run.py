"""Shared ComfyUI plumbing + the LOCKED split visual style (a module, not a CLI).

Drivers that import from here:
  batch_zturbo.py  — production batch on z-image-turbo (the one you actually run)
  model_test.py    — A/B/C model comparison harness

BASE_STYLE / CHARACTER_STYLE are the single source of truth for the house style;
docs/visual-style.md documents the reasoning. Override server/output locations with
env vars COMFY_URL / COMFY_OUT when ComfyUI lives elsewhere (see .env.example).
"""
import json, os, pathlib, urllib.request

COMFY = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
COMFY_OUT = pathlib.Path(os.environ.get("COMFY_OUT", r"C:\Users\Darks\ComfyUI-Shared\output"))

# Style is SPLIT so non-character scenes don't get a stick figure injected.
#   BASE_STYLE      -> appended to EVERY scene (no mention of a person).
#   CHARACTER_STYLE -> appended ONLY when shot_type == "CHARACTER".
# Thin-line, flat, white, balanced medium-large subject inside a safe area (Nuay 2026-06-28).
BASE_STYLE = (
    "Minimalist hand-drawn doodle drawn with THIN, fine, clean black pen lines — light and delicate, even "
    "single-stroke weight, NOT thick, NOT heavy, NOT marker (keep this exact line style). "
    "Use a FEW soft, gentle, muted flat colors as light accents (soft green, warm tan, gentle sky-blue, soft yellow) "
    "— calm and subtle, never saturated, never busy; keep the image mostly white and airy. "
    "Flat fills only — absolutely NO shading, NO gradient, NO drop shadow, NO paper texture. "
    "When the scene shows a place or a person, add a FEW small, light supporting details that hint at the "
    "surroundings and help tell the story (a couple of small plants, a little sun, a few soft ground or horizon "
    "lines) — gentle, sparse, uncluttered. For a plain object, icon, or number, keep it clean and simple with "
    "little or no background. Compose the subject at a comfortable MEDIUM-LARGE size, well-proportioned and "
    "balanced, kept fully inside a safe area so nothing touches the edges. Clean, childlike, calm, low-to-medium "
    "detail. 16:9 landscape composition."
)

# Appended ONLY for CHARACTER scenes — keeps figures out of B-ROLL / empty-landscape shots.
# Body style PINNED for consistency (Nuay 2026-06-28): always the SAME outlined-body character,
# never a bare single line, so the character looks identical across every scene.
CHARACTER_STYLE = (
    "The person is ALWAYS the exact same character, drawn identically in every image: a round WHITE head with a "
    "minimal face (two small black dot eyes, thin eyebrows, one small curved mouth), and a simple slim body with a "
    "clean thin OUTLINE — a narrow rounded torso with thin outlined arms and thin outlined legs (a soft cartoon "
    "stick figure with a lightly outlined body, NOT a single bare line, NOT a filled silhouette). "
    "Always the same head, same body shape, same thin even line weight."
)

# Negative prompt — INERT on cfg-1 turbo models (z-turbo) but ACTIVE on real-cfg models
# (z-image base, flux2 dev). Wire into the workflow's negative-text node when swapping models.
NEGATIVE = (
    "thick heavy outlines, bold marker strokes, shading, gradients, drop shadows, paper texture, "
    "realistic, 3d render, photo, painterly, cluttered, busy, crowded, "
    "subject touching the edge, cropped at the frame edge, text, words, letters, captions, "
    "watermark, signature, blurry, low quality"
)


def _post(path, data):
    req = urllib.request.Request(COMFY + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _get(path):
    return json.loads(urllib.request.urlopen(COMFY + path, timeout=30).read())
