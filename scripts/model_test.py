"""A/B/C test: run the SAME diverse prompts across multiple ComfyUI model workflows.

Same diverse scenes + same split style (BASE_STYLE everywhere, CHARACTER_STYLE only on
character scenes) + same NEGATIVE + same seed, so we can compare which model stays
on-concept and keeps the thin-line doodle style best.

Output: output/_model_test/<TAG>/<model>/NN_name.png  (skips existing, resumable)

Usage:
  python scripts/model_test.py                              # all models in MODELS
  python scripts/model_test.py z_image_turbo flux2_turbo    # only these
"""
import sys, json, time, shutil, pathlib, urllib.error
from comfy_run import _post, _get, COMFY_OUT, BASE_STYLE, CHARACTER_STYLE, NEGATIVE

WF_DIR = pathlib.Path("ComfyUi Api Workflow")
TAG = "v4_char"                           # bump when STYLE/prompts change → fresh folder
OUT = pathlib.Path("output/_model_test") / TAG
SEED = 42

# Per-model node map. pos/neg/seed = "node.inputkey"; save = output node id; neg=None if unused.
# "set" = extra node.key -> value overrides (e.g. flip a turbo boolean).
MODELS = {
    "flux2_dev":     {"file": "image_flux2_text_to_image.json", "pos": "98:6.text",  "neg": None,         "seed": "98:25.noise_seed", "save": "9"},
    "flux2_turbo":   {"file": "image_flux2_text_to_image.json", "pos": "98:6.text",  "neg": None,         "seed": "98:25.noise_seed", "save": "9", "set": {"98:104.value": True}},
    "z_image":       {"file": "image_z_image.json",             "pos": "76:67.text", "neg": "76:71.text", "seed": "76:69.seed",       "save": "9"},
    "z_image_turbo": {"file": "image_z_image_turbo (2).json",   "pos": "57:27.text", "neg": None,         "seed": "57:3.seed",        "save": "9"},
}

# (name, is_character, visual) — consistency check: 4 different poses, must look like the SAME character.
PROMPTS = [
    ("01_standing",  True, "the character standing still and calm, arms relaxed at its sides, facing forward"),
    ("02_walking",   True, "the character walking to the right with a simple stride"),
    ("03_pointing",  True, "the character raising one arm to point up at a small question mark above it"),
    ("04_reaching",  True, "the character bending slightly forward, one arm reaching down toward the ground"),
]


def setval(wf, ref, value):
    node, key = ref.split(".", 1)
    wf[node]["inputs"][key] = value


def run_model(model, cfg):
    wf_template = json.loads((WF_DIR / cfg["file"]).read_text(encoding="utf-8"))
    dest_dir = OUT / model
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {model}  ({cfg['file']}) ===", flush=True)
    ok = 0
    for name, is_char, visual in PROMPTS:
        dest = dest_dir / f"{name}.png"
        if dest.exists():
            print(f"  {name}  skip (exists)", flush=True)
            ok += 1
            continue
        prompt = visual + "  " + BASE_STYLE + (("  " + CHARACTER_STYLE) if is_char else "")
        wf = json.loads(json.dumps(wf_template))
        setval(wf, cfg["pos"], prompt)
        if cfg["neg"]:
            setval(wf, cfg["neg"], NEGATIVE)
        setval(wf, cfg["seed"], SEED)
        for ref, val in cfg.get("set", {}).items():
            setval(wf, ref, val)

        t0 = time.time()
        try:
            pid = _post("/prompt", {"prompt": wf})["prompt_id"]
        except urllib.error.HTTPError as e:
            print(f"  {name}  QUEUE REJECTED: {e.read().decode()[:200]}", flush=True)
            continue
        except Exception as e:
            print(f"  {name}  QUEUE FAIL: {e}", flush=True)
            continue

        img, err = None, None
        for _ in range(600):
            hist = _get(f"/history/{pid}")
            if pid in hist:
                imgs = hist[pid].get("outputs", {}).get(cfg["save"], {}).get("images", [])
                if imgs:
                    img = imgs[0]
                else:
                    err = (hist[pid].get("status", {}) or {}).get("status_str", "no image in output")
                break
            time.sleep(1)

        if not img:
            print(f"  {name}  FAIL: {err or 'timeout (10 min)'}", flush=True)
            continue
        src = COMFY_OUT / (img.get("subfolder") or "") / img["filename"]
        shutil.copy(src, dest)
        print(f"  {name}  OK {round(time.time() - t0, 1)}s", flush=True)
        ok += 1
    print(f"  --> {ok}/{len(PROMPTS)} done for {model}", flush=True)


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(MODELS)
    print(f"TAG={TAG}", flush=True)
    for m in wanted:
        if m not in MODELS:
            print(f"unknown model '{m}' (have: {', '.join(MODELS)})")
            continue
        run_model(m, MODELS[m])
    print(f"\nDONE -> {OUT.resolve()}", flush=True)
