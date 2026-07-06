"""Generate a background music bed with the local ACE-Step workflow (ComfyUI).

Self-generated = zero Content-ID risk and it fits the clip. For narration, prefer a
MELODY-FREE ambient pad/drone (a moving melody competes with speech even when quiet;
a static pad reads as atmosphere). Mix it under the voice at ~7% (see assemble_clip.py).

Usage:
  python scripts/gen_music.py output/<slug>/audio_assets/music.mp3
  python scripts/gen_music.py out.mp3 --seconds 150 --seed 5 --bpm 60 --tags "..."

Needs ComfyUI running with the ACE-Step 1.5 turbo model. Override server/output with
env vars COMFY_URL / COMFY_OUT (see comfy_run.py / .env.example).
"""
import argparse, json, os, pathlib, shutil, time, urllib.request

COMFY = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
COMFY_OUT = pathlib.Path(os.environ.get("COMFY_OUT", r"C:\Users\Darks\ComfyUI-Shared\output"))
WF = pathlib.Path(__file__).resolve().parent.parent / "ComfyUi Api Workflow" / "audio_ace_step1_5_xl_turbo.json"

# default = warm, melody-free ambient bed that sits UNDER narration without pulling focus
DEFAULT_TAGS = ("ambient drone, soft warm synth pad, atmospheric texture, airy, spacious reverb, "
                "meditative, calm, peaceful, gentle, slow, warm, minimal, subtle background, "
                "NO melody, no lead instrument, no drums, no percussion, no beat, dawn, tranquil, healing")


def _post(path, data):
    req = urllib.request.Request(COMFY + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _get(path):
    return json.loads(urllib.request.urlopen(COMFY + path, timeout=30).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="destination .mp3 path")
    ap.add_argument("--seconds", type=int, default=150)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--bpm", type=int, default=60)
    ap.add_argument("--tags", default=DEFAULT_TAGS)
    a = ap.parse_args()

    wf = json.loads(WF.read_text(encoding="utf-8"))
    wf["94"]["inputs"].update(tags=a.tags, lyrics="", duration=a.seconds, bpm=a.bpm)
    wf["98"]["inputs"]["seconds"] = a.seconds
    wf["109"]["inputs"]["value"] = a.seed

    pid = _post("/prompt", {"prompt": wf})["prompt_id"]
    print(f"gen: seed={a.seed} dur={a.seconds}s bpm={a.bpm}  (prompt {pid})", flush=True)
    t0 = time.time()
    while True:
        time.sleep(3)
        hist = _get(f"/history/{pid}")
        if pid in hist:
            break
        if time.time() - t0 > 600:
            raise SystemExit("timeout waiting for ACE-Step")
    audios = hist[pid]["outputs"].get("107", {}).get("audio", [])
    if not audios:
        raise SystemExit("no audio produced (is the ACE-Step model loaded?)")
    src = COMFY_OUT / audios[0].get("subfolder", "") / audios[0]["filename"]
    dst = pathlib.Path(a.out); dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"OK {int(time.time() - t0)}s -> {dst}")


if __name__ == "__main__":
    main()
