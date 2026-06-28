"""Phase F -- Gemini Imagen doodle images per script beat.

Usage:
  python scripts/phase_f_images.py <slug>

Reads:  output/<slug>/script.json  (beat texts)
        output/<slug>/words.json   (word timestamps)
Writes: output/<slug>/frames/scene_01..04.png
        output/<slug>/scenes.json  (scene timing for Phase G)
"""
import os, sys, json, re, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

# load .env manually (no dotenv dep needed)
env_file = pathlib.Path(__file__).parents[1] / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from google import genai
from google.genai import types

MODEL   = "models/imagen-4.0-fast-generate-001"
STYLE   = (
    "Hand-drawn doodle illustration, thick uneven black felt-tip marker outlines, "
    "flat cheerful fill colors, white background, casual sketchy look, no text, "
    "no words, vertical 9:16 composition with subject centred in frame."
)

BEATS = ["hook", "explain", "illustrate", "teach"]

VISUAL_PROMPTS = {
    "hook":       "A relaxed stickman waking up naturally in a cozy bed, sunlight streaming through the window, "
                  "an alarm clock crossed out on the bedside table, a small vegetable garden visible outside.",
    "explain":    "Split scene: left side shows a city person straining at a gym doing willpower exercises "
                  "with a motivational calendar; right side shows a cheerful farmer following a simple "
                  "plant-growth schedule on a chalkboard.",
    "illustrate": "A lone farmer stickman walking barefoot through neat vegetable rows at dawn, "
                  "feet on cool dark soil, a rising sun low on the horizon, hands already reaching "
                  "for the first plant before fully awake.",
    "teach":      "A stickman connected to a large thriving plant by a glowing thread, "
                  "the plant has a small clock face in its leaves, conveying natural accountability "
                  "rather than self-discipline.",
}

def _clean(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", "", text.lower()).split()

def _find_beat_start(beat_text: str, words: list[dict]) -> float:
    """Return timestamp of first word of beat_text found in words list."""
    needle = _clean(beat_text)[:4]          # first 4 words, punctuation stripped
    word_tokens = [_clean(w["word"])[0] if _clean(w["word"]) else "" for w in words]
    for i in range(len(word_tokens) - len(needle) + 1):
        if word_tokens[i : i + len(needle)] == needle:
            return words[i]["start"]
    # fallback: return proportional position
    return 0.0

def generate(slug: str):
    out_dir    = pathlib.Path("output") / slug
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    script = json.loads((out_dir / "script.json").read_text(encoding="utf-8"))
    words  = json.loads((out_dir / "words.json").read_text(encoding="utf-8"))
    total_dur = words[-1]["end"]

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    scenes = []
    for i, beat in enumerate(BEATS):
        beat_text    = script[beat]
        start_time   = _find_beat_start(beat_text, words)
        next_start   = _find_beat_start(script[BEATS[i + 1]], words) if i + 1 < len(BEATS) else total_dur
        prompt       = f"{VISUAL_PROMPTS[beat]} {STYLE}"
        img_path     = frames_dir / f"scene_{i+1:02d}.png"

        print(f"[{i+1}/4] {beat} ({start_time:.1f}s-{next_start:.1f}s) generating...")
        response = client.models.generate_images(
            model=MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16",
            ),
        )
        img_bytes = response.generated_images[0].image.image_bytes
        img_path.write_bytes(img_bytes)
        print(f"  -> {img_path.name}  ({len(img_bytes):,} bytes)")

        scenes.append({
            "scene": i + 1,
            "beat":  beat,
            "start": round(start_time, 3),
            "end":   round(next_start, 3),
            "image": str(img_path),
        })

    scenes_path = out_dir / "scenes.json"
    scenes_path.write_text(json.dumps(scenes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOK -- {len(scenes)} scenes -> {scenes_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/phase_f_images.py <slug>")
        sys.exit(1)
    generate(sys.argv[1])
