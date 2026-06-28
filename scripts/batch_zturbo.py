"""Batch-generate a clip's frames on z-image-turbo (the locked production model).

Reads output/<slug>/scene_prompts.json, applies the SPLIT style (BASE_STYLE on every
scene, CHARACTER_STYLE only when shot_type == "CHARACTER"), drives the z-image-turbo
workflow, and saves output/<slug>/frames/scene_NN.png. Skips existing (resumable),
fixed seed for a consistent series.

Usage:
  python scripts/batch_zturbo.py <slug>                       # all scenes -> frames/
  python scripts/batch_zturbo.py <slug> --only 5,7,8          # just these scenes
  python scripts/batch_zturbo.py <slug> --only 5,7 --tag test # write to frames_test/ (style A/B test)
"""
import sys, json, time, shutil, pathlib, argparse
from comfy_run import _post, _get, COMFY_OUT, BASE_STYLE, CHARACTER_STYLE

WF = pathlib.Path("ComfyUi Api Workflow/image_z_image_turbo (2).json")
POS, SEED_REF, SAVE = "57:27.text", "57:3.seed", "9"
SEED = 42


def setval(wf, ref, value):
    node, key = ref.split(".", 1)
    wf[node]["inputs"][key] = value


def batch(slug: str, only=None, tag=None, seed=SEED):
    base = pathlib.Path("output") / slug
    prompts = json.loads((base / "scene_prompts.json").read_text(encoding="utf-8"))
    template = json.loads(WF.read_text(encoding="utf-8"))
    frames = base / (f"frames_{tag}" if tag else "frames")
    frames.mkdir(parents=True, exist_ok=True)
    if only:
        prompts = [p for p in prompts if p["scene"] in only]
    print(f"target: {frames}  | scenes: {len(prompts)}", flush=True)

    ok = skip = fail = 0
    for item in prompts:
        sc = item["scene"]
        dest = frames / f"scene_{sc:02d}.png"
        if dest.exists():
            print(f"scene {sc:02d}  skip (exists)", flush=True)
            skip += 1
            continue

        prompt = item["visual"] + "  " + BASE_STYLE
        if item.get("shot_type") == "CHARACTER":
            prompt += "  " + CHARACTER_STYLE

        wf = json.loads(json.dumps(template))
        setval(wf, POS, prompt)
        setval(wf, SEED_REF, seed)

        t0 = time.time()
        try:
            pid = _post("/prompt", {"prompt": wf})["prompt_id"]
        except Exception as e:
            print(f"scene {sc:02d}  QUEUE FAIL: {e}", flush=True)
            fail += 1
            continue

        img = None
        for _ in range(600):
            hist = _get(f"/history/{pid}")
            if pid in hist:
                imgs = hist[pid].get("outputs", {}).get(SAVE, {}).get("images", [])
                img = imgs[0] if imgs else None
                break
            time.sleep(1)
        if not img:
            print(f"scene {sc:02d}  FAIL (no image / timeout)", flush=True)
            fail += 1
            continue

        src = COMFY_OUT / (img.get("subfolder") or "") / img["filename"]
        shutil.copy(src, dest)
        print(f"scene {sc:02d}/{len(prompts)}  '{item['phrase'][:42]}'  OK {round(time.time() - t0, 1)}s", flush=True)
        ok += 1

    print(f"\nbatch done: {ok} generated, {skip} skipped, {fail} failed", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", help="comma-separated scene numbers, e.g. 5,7,8")
    ap.add_argument("--tag", help="write to frames_<tag>/ instead of frames/ (for style A/B tests)")
    ap.add_argument("--seed", type=int, default=SEED, help="override the fixed seed (for re-rolling a bad scene)")
    args = ap.parse_args()
    only = {int(x) for x in args.only.split(",")} if args.only else None
    batch(args.slug, only=only, tag=args.tag, seed=args.seed)
