"""Assemble a clip: frames/ + voice audio -> final.mp4

Gapless: each frame holds from its beat's start until the next beat starts.

Visual beats: if output/<slug>/scene_prompts.json exists, each entry may carry
  "covers": [12, 13, 14]   <- one image spans these consecutive scenes.json phrases
Entries without "covers" are 1:1 (old projects keep working unchanged).
Captions stay per-phrase in scenes.json — only the IMAGE timeline groups.

Breathing room (every clip, automatic):
  - LEAD_IN  : hold frame 1 for ~1s BEFORE the voice starts (viewer settles in).
  - OUTRO    : hold a final frame for ~2.5s AFTER the voice ends (let it land).
  - FADE     : voice eases in/out (afade); video fades to black at the very end only.
The outro frame is `frames/scene_end.png` if Phase B authored one, else the last frame.

--ken-burns : instead of static holds, give every scene a slow "breathing" zoom
  (alternating in/out, camera move only so the doodle never warps). Each scene renders
  in its own ffmpeg process, several in parallel (--jobs). Zoom math runs on a 4x
  supersampled input (subpixel precision = no judder); zoompan outputs at 2x and a
  lanczos pass downscales to target — same look as the old 4x-out path, ~4x cheaper.

Usage:
  python scripts/assemble_clip.py <slug> --landscape
  python scripts/assemble_clip.py <slug> --landscape --ken-burns
  python scripts/assemble_clip.py <slug> --ken-burns --max-scenes 3 --out kb_smoke.mp4   # quick test
  python scripts/assemble_clip.py <slug> --music SFX/track.mp3 --out preview.mp4

Reads:  output/<slug>/scenes.json, scene_prompts.json (optional beats),
        frames/scene_NN.png, frames/scene_end.png (optional), *.mp3/*.wav
Writes: output/<slug>/final.mp4  (or --out name)
"""
import json, os, pathlib, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

FPS = 30
MUSIC_VOL = 0.07   # background music level under the voice (~7%) — soft bed, doesn't fight speech
LEAD_IN = 1.0      # seconds of frame-1 hold before the voice (pre-roll breath)
OUTRO = 2.5        # seconds of hold after the voice (post-roll settle)
FADE_OUT = 1.0     # video fade to black at the very end (inside the OUTRO window)
AFADE_IN = 0.35    # ease the voice in so it doesn't start abruptly
AFADE_OUT = 0.6    # ease the voice out so it doesn't cut abruptly

# Ken Burns (Nuay-approved v3 motion: very slow + supersampled = smooth)
KB_ZOOM_PER_SEC = 0.006   # ~0.6%/s "breathing" zoom
KB_SUPER = 4              # zoom math on a 4x input -> subpixel precision, kills judder
KB_OUT_SUPER = 2          # zoompan emits 2x, lanczos downscales to target
KB_MAX = 0.08             # cap total zoom on a long scene
# ponytail: libx264 ultrafast for intermediates (they're re-encoded at the final mux);
# h264_nvenc is the upgrade path if the filter stage ever stops being the bottleneck.
KB_JOBS = max(2, min(6, (os.cpu_count() or 8) // 2))


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("FFMPEG ERROR:\n" + r.stderr[-2000:])
    return r


def _audio_dur(path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def _kb_clip(img, nframes, out_path, zoom_in, W, H):
    """Render one slow-zoom clip of exactly `nframes` frames from a still image."""
    sw, sh = W * KB_SUPER, H * KB_SUPER
    ow, oh = W * KB_OUT_SUPER, H * KB_OUT_SUPER
    denom = max(1, nframes - 1)
    dur = nframes / FPS
    maxz = min(KB_MAX, KB_ZOOM_PER_SEC * dur)
    if zoom_in:
        z = f"1+{maxz:.5f}*on/{denom}"
    else:
        z = f"1+{maxz:.5f}-{maxz:.5f}*on/{denom}"
    vf = (
        f"scale={sw}:{sh}:force_original_aspect_ratio=decrease,"
        f"pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color=white,"
        f"zoompan=z='{z}':d={nframes}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={ow}x{oh}:fps={FPS},"
        f"scale={W}:{H}:flags=lanczos,format=yuv420p"
    )
    _run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-frames:v", str(nframes),
          "-r", str(FPS), "-c:v", "libx264", "-crf", "15", "-preset", "ultrafast", str(out_path)])


def _image_timeline(out_dir, scenes):
    """[(scene_no, start), ...] — one entry per IMAGE (beat), from scene_prompts.json
    when present (covers-aware, validated), else 1:1 with scenes.json."""
    pf = out_dir / "scene_prompts.json"
    if not pf.exists():
        return [(s["scene"], s["start"]) for s in scenes]

    entries = sorted(json.loads(pf.read_text(encoding="utf-8")), key=lambda e: e["scene"])
    starts = {s["scene"]: s["start"] for s in scenes}
    timeline, covered = [], set()
    for e in entries:
        covers = sorted(e.get("covers") or [e["scene"]])
        unknown = [c for c in covers if c not in starts]
        if unknown:
            sys.exit(f"scene_prompts: entry {e['scene']} covers unknown scenes {unknown}")
        if e["scene"] != covers[0]:
            sys.exit(f"scene_prompts: entry {e['scene']} must be the FIRST scene it covers ({covers})")
        dup = covered & set(covers)
        if dup:
            sys.exit(f"scene_prompts: scenes covered twice: {sorted(dup)[:8]}")
        covered.update(covers)
        timeline.append((e["scene"], starts[covers[0]]))
    missing = [s["scene"] for s in scenes if s["scene"] not in covered]
    if missing:
        sys.exit(f"scene_prompts: scenes not covered by any beat: {missing[:8]}"
                 + ("..." if len(missing) > 8 else ""))
    return timeline


def assemble(slug, landscape=False, music=None, out=None, lead_in=LEAD_IN, outro=OUTRO,
             ken_burns=False, max_scenes=None, jobs=KB_JOBS, music_vol=MUSIC_VOL):
    t_start = time.time()
    W, H = (1920, 1080) if landscape else (1080, 1920)
    out_dir = pathlib.Path("output") / slug

    scenes = json.loads((out_dir / "scenes.json").read_text(encoding="utf-8"))
    full = _image_timeline(out_dir, scenes)
    timeline = full[:max_scenes] if max_scenes else full

    mp3s = list(out_dir.glob("*.mp3")) + list(out_dir.glob("*.wav"))
    if not mp3s:
        sys.exit(f"No .mp3/.wav found in {out_dir}")
    audio = mp3s[0].resolve()
    audio_dur = _audio_dur(audio)
    print(f"Audio : {mp3s[0].name} ({audio_dur:.1f}s)")
    print(f"Images: {len(timeline)} beats over {len(scenes)} phrases | lead-in {lead_in}s, outro {outro}s"
          + (f"  | KEN BURNS x{jobs}" if ken_burns else ""))

    missing = [f"scene_{n:02d}.png" for n, _ in timeline
               if not (out_dir / "frames" / f"scene_{n:02d}.png").exists()]
    if missing:
        sys.exit(f"Missing {len(missing)} frame(s): {', '.join(missing[:5])}"
                 + ("..." if len(missing) > 5 else ""))

    last_img = (out_dir / "frames" / f"scene_{timeline[-1][0]:02d}.png").resolve()
    end_png = out_dir / "frames" / "scene_end.png"
    outro_img = end_png.resolve() if end_png.exists() else last_img
    print(f"Outro : {'scene_end.png' if end_png.exists() else 'hold last frame'}")

    # Segments: (image, n_frames, zoom_in). Alternate zoom direction for variety.
    segs = []
    for i, (n, start) in enumerate(timeline):
        img = (out_dir / "frames" / f"scene_{n:02d}.png").resolve()
        # duration runs to the next image in the FULL timeline — so --max-scenes stays a
        # quick test instead of the last image silently spanning the rest of the audio
        if i + 1 < len(full):
            dur = full[i + 1][1] - start
        else:
            dur = audio_dur - start
        if i == 0:
            dur += lead_in
        segs.append((img, max(1, round(dur * FPS)), i % 2 == 0))
    segs.append((outro_img, max(1, round(outro * FPS)), len(timeline) % 2 == 0))

    total_frames = sum(nf for _, nf, _ in segs)
    total = round(total_frames / FPS, 3)
    lead_ms = int(round(lead_in * 1000))
    output = (out_dir / (out or "final.mp4")).resolve()
    concat_file = out_dir / "concat.txt"
    kb_dir = out_dir / "_kb"

    if ken_burns:
        kb_dir.mkdir(exist_ok=True)
        print(f"Ken Burns: rendering {len(segs)} clips, {jobs} in parallel "
              f"(zoom math {KB_SUPER}x, output {KB_OUT_SUPER}x + lanczos)...")
        t0 = time.time()

        def render(idx):
            img, nf, zin = segs[idx]
            clip = (kb_dir / f"kb_{idx:03d}.mp4").resolve()
            _kb_clip(img, nf, clip, zin, W, H)
            return idx, clip

        clips = [None] * len(segs)
        done = 0
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = [ex.submit(render, i) for i in range(len(segs))]
            for f in as_completed(futs):
                try:
                    idx, clip = f.result()
                except RuntimeError as e:
                    print(e)
                    ex.shutdown(cancel_futures=True)
                    sys.exit(1)
                clips[idx] = clip
                done += 1
                if done % 10 == 0 or done == len(segs):
                    el = time.time() - t0
                    eta = el / done * (len(segs) - done)
                    print(f"  {done}/{len(segs)}  elapsed {el/60:.1f}m  eta {eta/60:.1f}m", flush=True)
        concat_file.write_text(
            "\n".join(f"file '{c.as_posix()}'" for c in clips), encoding="utf-8")
        vid = f"[0:v]fade=t=out:st={round(total - FADE_OUT, 3)}:d={FADE_OUT}[v]"
    else:
        lines = []
        for img, nf, _ in segs:
            lines.append(f"file '{img.as_posix()}'\nduration {round(nf / FPS, 3)}")
        lines.append(f"file '{segs[-1][0].as_posix()}'")  # flush final frame
        concat_file.write_text("\n".join(lines), encoding="utf-8")
        vid = (
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,"
            f"fade=t=out:st={round(total - FADE_OUT, 3)}:d={FADE_OUT}[v]"
        )

    aout = round(lead_in + audio_dur - AFADE_OUT, 3)
    voice = (f"adelay={lead_ms}|{lead_ms},"
             f"afade=t=in:st={lead_in}:d={AFADE_IN},"
             f"afade=t=out:st={aout}:d={AFADE_OUT}")
    tail = [
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-t", str(total), str(output),
    ]

    if music:
        filt = (f"{vid};"
                f"[1:a]{voice}[a1];[2:a]volume={music_vol}[a2];"
                f"[a1][a2]amix=inputs=2:duration=first:normalize=0,apad,atrim=0:{total}[a]")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
               "-i", str(audio), "-stream_loop", "-1", "-i", str(pathlib.Path(music).resolve()),
               "-filter_complex", filt, "-map", "[v]", "-map", "[a]"] + tail
        print(f"Music : {pathlib.Path(music).name} @ {int(music_vol*100)}%")
    else:
        filt = f"{vid};[1:a]{voice},apad,atrim=0:{total}[a]"
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
               "-i", str(audio), "-filter_complex", filt, "-map", "[v]", "-map", "[a]"] + tail

    print("Muxing...")
    try:
        _run(cmd)
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    size_mb = output.stat().st_size / 1_048_576
    mins = (time.time() - t_start) / 60
    print(f"OK -> {output}  ({size_mb:.1f} MB, ~{total:.1f}s video, built in {mins:.1f}m)")
    concat_file.unlink()
    if ken_burns:
        shutil.rmtree(kb_dir, ignore_errors=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--landscape", action="store_true", help="output 1920x1080 instead of 1080x1920")
    ap.add_argument("--music", help="path to a background music file to mix under the voice")
    ap.add_argument("--music-vol", type=float, default=MUSIC_VOL, dest="music_vol",
                    help=f"music level under the voice (default {MUSIC_VOL})")
    ap.add_argument("--out", help="output filename (default final.mp4)")
    ap.add_argument("--ken-burns", action="store_true", dest="ken_burns", help="slow zoom on every scene")
    ap.add_argument("--jobs", type=int, default=KB_JOBS, help=f"parallel Ken Burns renders (default {KB_JOBS})")
    ap.add_argument("--lead-in", type=float, default=LEAD_IN, dest="lead_in")
    ap.add_argument("--outro", type=float, default=OUTRO)
    ap.add_argument("--max-scenes", type=int, default=None, dest="max_scenes", help="debug: only first N beats")
    args = ap.parse_args()
    assemble(args.slug, landscape=args.landscape, music=args.music, out=args.out,
             lead_in=args.lead_in, outro=args.outro, ken_burns=args.ken_burns,
             max_scenes=args.max_scenes, jobs=args.jobs, music_vol=args.music_vol)
