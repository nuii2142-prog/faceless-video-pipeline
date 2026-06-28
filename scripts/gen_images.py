"""Image generation — backend-agnostic (Gemini Nano Banana now, ComfyUI local later).

Reads:  output/<slug>/scene_prompts.json  -> [{scene, phrase, visual}, ...]
Writes: output/<slug>/frames/scene_<NN>.png

The "visual" is the per-phrase scene description (authored by Claude). This module just
wraps it in the LOCKED style + negatives and sends it to the chosen backend, so the same
prompts/style work whether you generate on Gemini or local ComfyUI.

Usage:
  python scripts/gen_images.py <slug> [--backend gemini|comfyui] [--aspect 9:16|16:9] [--scenes 3,13,31]

Run with the Gemini-capable interpreter (.env PYTHON): google-genai + python-dotenv required.
"""
import os, sys, json, base64, argparse, pathlib

# ---- LOCKED STYLE (source: docs/visual-style.md — keep these two in sync) ----
STYLE_POSITIVE = (
    "Hand-drawn marker doodle illustration in a minimalist stick-figure style. Bold, thick, "
    "slightly uneven black felt-tip outlines of even weight, like quick marker strokes on white "
    "paper. Simple stick figures: a large plain round or oval WHITE head with a minimal expressive "
    "face (two small round dot eyes, thin simple eyebrows, a single curved-line mouth), a thin "
    "stick or lightly-outlined body, thin single-stroke arms and legs. Flat solid fill colors with "
    "NO shading and NO gradient. Simple flat color-block background or plain white, lots of empty "
    "negative space, a single centered subject. Naive, childlike, clean, low-detail, a little comedic."
)
STYLE_NEGATIVE = (
    "photorealistic, realistic, realism, photograph, 3D render, CGI, soft shading, cell shading, "
    "gradient, ambient occlusion, lighting effects, drop shadow, texture, painterly, digital "
    "painting, oil painting, watercolor, anime, manga, comic-book inking, cross-hatching, fine "
    "detail, intricate detail, detailed background, busy background, perspective depth, volumetric, "
    "glossy, polished, professional illustration, smooth vector edges, highly detailed, 4k, 8k, "
    "realistic proportions, anatomical detail, detailed face, hair strands, muscle definition, fabric folds"
)

GEMINI_MODELS = [
    "models/gemini-3.1-flash-image",          # Nano Banana 2 — 1000 img/day, default
    "models/gemini-3.1-flash-image-preview",
    "models/gemini-3-pro-image",              # Nano Banana Pro — higher quality, 250/day
    "models/gemini-3-pro-image-preview",
]


def build_prompts(visual: str, aspect: str) -> tuple[str, str]:
    """Return (positive, negative). Positive = scene + locked style + framing."""
    framing = "vertical 9:16 portrait, tall frame" if aspect == "9:16" else "horizontal 16:9 landscape"
    positive = f"{visual}. {STYLE_POSITIVE} {framing}, subject centered, generous empty space."
    return positive, STYLE_NEGATIVE


# ---------------------------- backends ----------------------------

def gen_gemini(positive: str, negative: str, out_path: pathlib.Path, aspect: str):
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # pick first available image model
    available = {m.name for m in client.models.list() if "generateContent" in (m.supported_actions or [])}
    model = next((m for m in GEMINI_MODELS if m in available), None) or GEMINI_MODELS[0]

    # Nano Banana has no negative-prompt field -> fold negatives into the text
    prompt = f"{positive} Absolutely DO NOT include: {negative}."

    def _call(use_aspect):
        if use_aspect:
            try:
                cfg = types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    image_config=types.ImageConfig(aspect_ratio=aspect),
                )
            except Exception:
                cfg = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        else:
            cfg = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        return client.models.generate_content(model=model, contents=prompt, config=cfg)

    try:
        resp = _call(True)
    except Exception:
        resp = _call(False)   # retry without aspect config if the model rejects it

    for part in resp.candidates[0].content.parts:
        data = getattr(getattr(part, "inline_data", None), "data", None)
        if data:
            if isinstance(data, str):
                data = base64.b64decode(data)
            out_path.write_bytes(data)
            return model, len(data)
    txt = next((p.text for p in resp.candidates[0].content.parts if getattr(p, "text", None)), "")
    raise RuntimeError(f"no image returned (model={model}); text said: {txt[:120]}")


def gen_comfyui(positive: str, negative: str, out_path: pathlib.Path, aspect: str):
    # TODO: ComfyUI local backend. Interface is identical: (positive, negative, out_path, aspect).
    # Plan: POST a workflow JSON to http://127.0.0.1:8188/prompt with positive -> CLIP positive node,
    # negative -> CLIP negative node, aspect -> empty-latent W/H, then poll /history and save the PNG.
    raise NotImplementedError(
        "ComfyUI backend not wired yet. positive/negative/aspect are ready to drop into a workflow."
    )


BACKENDS = {"gemini": gen_gemini, "comfyui": gen_comfyui}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--backend", default="gemini", choices=list(BACKENDS))
    ap.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    ap.add_argument("--scenes", default="", help="comma list of scene numbers; empty = all in scene_prompts.json")
    args = ap.parse_args()

    out_dir = pathlib.Path("output") / args.slug
    frames = out_dir / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    items = json.loads((out_dir / "scene_prompts.json").read_text(encoding="utf-8"))
    if args.scenes:
        want = {int(x) for x in args.scenes.split(",")}
        items = [it for it in items if it["scene"] in want]

    backend = BACKENDS[args.backend]
    print(f"Backend: {args.backend} | aspect: {args.aspect} | scenes: {[i['scene'] for i in items]}")
    ok = 0
    for it in items:
        positive, negative = build_prompts(it["visual"], args.aspect)
        out = frames / f"scene_{it['scene']:02d}.png"
        try:
            info, size = backend(positive, negative, out, args.aspect)
            print(f"  #{it['scene']:>2} OK -> {out.name} ({size:,} bytes) [{info}]")
            ok += 1
        except Exception as e:
            print(f"  #{it['scene']:>2} FAIL: {str(e)[:160]}")
    print(f"\n{ok}/{len(items)} images -> {frames}")
    if args.backend == "gemini" and ok:
        print(f"Cost note: {ok} images via Gemini Nano Banana (tier-1 limit 1000 img/day). "
              f"Check Google Cloud billing for exact spend.")


if __name__ == "__main__":
    main()
