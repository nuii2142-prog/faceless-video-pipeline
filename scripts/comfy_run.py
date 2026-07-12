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
# v4 (2026-07-09): BASE_STYLE says HOW to draw only. WHAT to draw — the setting, props and
# camera — lives in each beat's `visual` (menus in docs/visual-style.md + SKILL.md B3). Putting
# scene content here stamped the same road/jar/banana onto every frame, indoor scenes included.
BASE_STYLE = (
    "Cheerful minimalist hand-drawn doodle drawn with THIN, clean black pen lines — delicate but confident, a "
    "slightly firmer even outline on the main subject; NOT thick, NOT heavy, NOT marker (keep this thin line style). "
    "Palette, flat fills only: lush tropical greens from fresh yellow-green to deep forest green, dark rich "
    "soil brown, warm terracotta, straw-tan, soft cream, and a pale peach-to-blue dawn sky — warm and alive, "
    "richer than pale pastel but never neon, never harsh. "
    "Reserve ONE accent color: deep warm AMBER-GOLD, used only for the sun and the dawn glow — always the single "
    "warmest thing in the frame. "
    "Light the scene simply from ONE soft source that fits the moment (the dawn sky, a window, a lamp, a screen): "
    "gentle two-tone CEL shading — each flat colour gets one slightly darker flat shade on the side away from the "
    "light, and surfaces facing the light warm up softly; long soft simple shadows at dawn. Shading stays FLAT "
    "poster-style shapes: NO airbrush gradients, NO fuzzy soft shadows, NO 3d render look, NO paper texture. "
    "Set the scene with a FEW well-chosen supporting details that belong to THAT place — an indoor scene shows "
    "its room honestly (wooden walls, floor, simple furniture, a window); an outdoor scene shows its plants, "
    "ground and sky — then let the frame BREATHE: generous calm open areas of simple flat colour around the "
    "subject, uncluttered, quiet, never busy or dense. "
    "All background colours stay soft, muted and slightly hazy, in one warm gentle dawn family — quieter than "
    "the subject, so the clean WHITE character or the single main subject is always the clearest, brightest "
    "thing in the frame. "
    "For a plain object, icon, number or stat card, keep it clean and simple with little or no background (do NOT "
    "fill it with scenery). "
    "Compose the subject at a comfortable MEDIUM-LARGE size, well-proportioned and balanced, kept fully inside a "
    "safe area so nothing touches the edges. Clean, childlike, warm and lively yet calm, medium detail — never "
    "cluttered or messy. 16:9 landscape composition."
)

# Appended ONLY for CHARACTER scenes — keeps figures out of B-ROLL / empty-landscape shots.
# Body style PINNED for consistency (Nuay 2026-06-28): always the SAME outlined-body character,
# never a bare single line, so the character looks identical across every scene.
CHARACTER_STYLE = (
    "The person is ALWAYS the exact same character, drawn identically in every image: an adorable, cute big-head "
    "doodle. His head is a LARGE round WHITE head that is clearly his main feature, drawn with a soft, warm, "
    "slightly UNEVEN hand-drawn roundness — NOT a perfect geometric circle, gently wobbly and organic the way a "
    "person draws by hand, and that little imperfection is exactly what makes him cute. "
    "Below the big head, a SMALL soft ROUNDED body — a short compact torso with short simple arms and short "
    "simple legs, cute and a little chubby and huggable, kept small and low beneath the big head. NOT tall, NOT "
    "lanky, NOT stretched, NOT stiff, NOT a slim grown-up figure. Soft, round, and endearing. "
    "Drawn with clean smooth black pen lines of a MEDIUM even weight — a little heavier than a hairline so he has "
    "presence and reads clearly, but still soft and simple, NOT thick marker, NOT sketchy. "
    "A minimal face: two small black dot eyes, thin eyebrows, one small simple curved mouth. His face keeps the "
    "same simple parts but his EXPRESSION acts the story: eyes can close in peace, curve into a smile, or open "
    "wide; the thin eyebrows tilt with worry or lift with wonder; the small mouth can smile, fall flat, or open "
    "slightly. "
    "Always the same big round head, same small soft rounded body, same medium clean line. "
    "(The farmer hat is NOT part of the character — it is added only by scenes that ask for it, so he is "
    "bareheaded here by default.)"
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
