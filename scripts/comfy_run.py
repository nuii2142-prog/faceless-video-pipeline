"""Drive ComfyUI (local, free) via its HTTP API using an exported API workflow as template.

Template: workflows/image_krea2_turbo_t2i (2).json  (Krea2 turbo + darkbrush LoRA + LLM refiner)
Known node IDs in that template:
  30:19 = User Prompt (PrimitiveStringMultiline)   <- we inject the scene prompt here
  30:24 = Refine Prompt? (Boolean)                 <- False = bypass the LLM enhancer (keep our style)
  30:23 = Enable LoRA? (Boolean)                   <- darkbrush ink look on/off
  30:3  = KSampler (seed)                           <- fix seed for consistency
  29    = SaveImage                                 <- output we copy back

Usage:
  python scripts/comfy_run.py --test --slug why-young-people-dont-want-to-farm
  python scripts/comfy_run.py --prompt-file p.txt --out frames/scene_03.png --slug <slug> [--lora 0|1] [--refine 0|1] [--seed N]
"""
import json, urllib.request, urllib.error, time, shutil, pathlib, argparse

COMFY = "http://127.0.0.1:8188"
COMFY_OUT = pathlib.Path(r"C:\Users\Darks\ComfyUI-Shared\output")
TEMPLATE = pathlib.Path("workflows/image_krea2_turbo_t2i (2).json")

TEST_PROMPT = (
    "A minimalist hand-drawn doodle in thick even black marker outlines. A single stick figure with "
    "a large round WHITE head and a simple face -- two small black dot eyes, thin eyebrows, a small "
    "smile -- with a thin black stick body and thin single-line arms and legs. The stick figure stands "
    "and holds up one freshly pulled orange carrot with a green leafy top in both hands; a few small "
    "bits of brown soil fall from the roots. Flat solid fill colors, no shading, no gradient. Plain "
    "white background, lots of empty space, one centered subject. Childlike, clean, low-detail, like a "
    "quick marker doodle on white paper."
)

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

# Negative prompt — INERT on krea2-turbo (cfg=1) but ACTIVE on real-cfg models
# (z-image, flux 2 dev). Wire this into the new workflow's negative-text node when swapping models.
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


def run_one(wf_template: dict, prompt: str, seed: int, refine: bool, lora: bool, dest: pathlib.Path):
    wf = json.loads(json.dumps(wf_template))   # deep copy
    wf["30:19"]["inputs"]["value"] = prompt
    wf["30:24"]["inputs"]["value"] = bool(refine)
    wf["30:23"]["inputs"]["value"] = bool(lora)
    wf["30:3"]["inputs"]["seed"] = int(seed)

    try:
        pid = _post("/prompt", {"prompt": wf})["prompt_id"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"queue rejected: {e.read().decode()[:400]}")

    t0 = time.time()
    for _ in range(900):
        hist = _get(f"/history/{pid}")
        if pid in hist:
            imgs = hist[pid]["outputs"].get("29", {}).get("images", [])
            if not imgs:
                raise RuntimeError("run finished but no image in SaveImage output")
            im = imgs[0]
            src = COMFY_OUT / (im.get("subfolder") or "") / im["filename"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dest)
            return dest, round(time.time() - t0, 1), src.name
        time.sleep(1)
    raise TimeoutError("timed out waiting for ComfyUI (15 min)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--test", action="store_true", help="run carrot scene with LoRA on AND off")
    ap.add_argument("--batch", action="store_true", help="generate all scenes from scene_prompts.json (refine=OFF lora=OFF)")
    ap.add_argument("--prompt-file")
    ap.add_argument("--out", help="dest path relative to output/<slug>/")
    ap.add_argument("--lora", type=int, default=1)
    ap.add_argument("--refine", type=int, default=0)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    wf = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    base = pathlib.Path("output") / args.slug

    if args.batch:
        prompts = json.loads((base / "scene_prompts.json").read_text(encoding="utf-8"))
        ok, skipped, failed = 0, 0, 0
        for item in prompts:
            sc = item["scene"]
            dest = base / "frames" / f"scene_{sc:02d}.png"
            if dest.exists():
                print(f"scene {sc:02d}  skip (exists)")
                skipped += 1
                continue
            full_prompt = item["visual"] + "  " + BASE_STYLE
            if item.get("shot_type") == "CHARACTER":
                full_prompt += "  " + CHARACTER_STYLE
            label = item["phrase"][:48]
            print(f"scene {sc:02d}/{len(prompts)}  '{label}' ...", end=" ", flush=True)
            try:
                _, secs, _ = run_one(wf, full_prompt, args.seed, refine=False, lora=False, dest=dest)
                print(f"OK {secs}s")
                ok += 1
            except Exception as exc:
                print(f"FAIL: {exc}")
                failed += 1
        print(f"\nbatch done: {ok} generated, {skipped} skipped, {failed} failed")
        return

    if args.test:
        for lora in (0, 1):
            dest = base / "style_test" / f"krea_carrot_lora{'ON' if lora else 'OFF'}.png"
            print(f"running: refine=OFF lora={'ON' if lora else 'OFF'} seed={args.seed} ...")
            try:
                d, secs, src = run_one(wf, TEST_PROMPT, args.seed, refine=False, lora=bool(lora), dest=dest)
                print(f"  OK {secs}s -> {d}  (comfy: {src})")
            except Exception as e:
                print(f"  FAIL: {e}")
        return

    prompt = pathlib.Path(args.prompt_file).read_text(encoding="utf-8").strip()
    dest = base / args.out
    d, secs, src = run_one(wf, prompt, args.seed, refine=bool(args.refine), lora=bool(args.lora), dest=dest)
    print(f"OK {secs}s -> {d}  (comfy: {src})")


if __name__ == "__main__":
    main()
