"""Assemble a clip: frames/ + voice audio -> final.mp4

Gapless: each frame holds from its scene start until the next scene starts.

Breathing room (every clip, automatic):
  - LEAD_IN  : hold frame 1 for ~1s BEFORE the voice starts (viewer settles in).
  - OUTRO    : hold a final frame for ~2.5s AFTER the voice ends (let it land).
  - FADE     : voice eases in/out (afade); video fades to black at the very end only.
The outro frame is `frames/scene_end.png` if Phase B authored one, else the last frame.

--ken-burns : instead of static holds, give every scene a slow "breathing" zoom
  (alternating in/out, camera move only so the doodle never warps). Renders each scene
  to a short clip (supersampled 4x then lanczos-downscaled = no judder), then concats.
  Heavier render (~8-15 min for a long clip) but far more alive. Run it in the background.

Usage:
  python scripts/assemble_clip.py <slug> --landscape
  python scripts/assemble_clip.py <slug> --landscape --ken-burns
  python scripts/assemble_clip.py <slug> --ken-burns --max-scenes 3 --out kb_smoke.mp4   # quick test
  python scripts/assemble_clip.py <slug> --music SFX/track.mp3 --out preview.mp4

Reads:  output/<slug>/scenes.json, frames/scene_NN.png, frames/scene_end.png (optional), *.mp3
Writes: output/<slug>/final.mp4  (or --out name)
"""
import json, pathlib, shutil, subprocess, sys

FPS = 30
MUSIC_VOL = 0.12   # background music level under the voice (~12%)
LEAD_IN = 1.0      # seconds of frame-1 hold before the voice (pre-roll breath)
OUTRO = 2.5        # seconds of hold after the voice (post-roll settle)
FADE_OUT = 1.0     # video fade to black at the very end (inside the OUTRO window)
AFADE_IN = 0.35    # ease the voice in so it doesn't start abruptly
AFADE_OUT = 0.6    # ease the voice out so it doesn't cut abruptly

# Ken Burns (Nuay-approved v3: very slow + supersampled = smooth)
KB_ZOOM_PER_SEC = 0.006   # ~0.6%/s "breathing" zoom
KB_SUPER = 4              # render zoom at 4x then lanczos-downscale -> kills judder
KB_MAX = 0.08            # cap total zoom on a long scene


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:\n", r.stderr[-2000:])
        sys.exit(1)
    return r


def _audio_dur(path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def _kb_clip(img, nframes, out_path, zoom_in, W, H):
    """Render one slow-zoom clip of exactly `nframes` frames from a still image."""
    sw, sh = W * KB_SUPER, H * KB_SUPER
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
        f"zoompan=z='{z}':d={nframes}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={sw}x{sh}:fps={FPS},"
        f"scale={W}:{H}:flags=lanczos,format=yuv420p"
    )
    _run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-frames:v", str(nframes),
          "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "fast", str(out_path)])


def assemble(slug, landscape=False, music=None, out=None,
             lead_in=LEAD_IN, outro=OUTRO, ken_burns=False, max_scenes=None):
    W, H = (1920, 1080) if landscape else (1080, 1920)
    out_dir = pathlib.Path("output") / slug

    scenes = json.loads((out_dir / "scenes.json").read_text(encoding="utf-8"))
    if max_scenes:
        scenes = scenes[:max_scenes]

    mp3s = list(out_dir.glob("*.mp3"))
    if not mp3s:
        sys.exit(f"No .mp3 found in {out_dir}")
    audio = mp3s[0].resolve()
    audio_dur = _audio_dur(audio)
    print(f"Audio : {mp3s[0].name} ({audio_dur:.1f}s)")
    print(f"Scenes: {len(scenes)}  | lead-in {lead_in}s, outro {outro}s"
          + ("  | KEN BURNS" if ken_burns else ""))

    missing = [f"scene_{s['scene']:02d}.png" for s in scenes
               if not (out_dir / "frames" / f"scene_{s['scene']:02d}.png").exists()]
    if missing:
        sys.exit(f"Missing {len(missing)} frame(s): {', '.join(missing[:5])}"
                 + ("..." if len(missing) > 5 else ""))

    last_img = (out_dir / "frames" / f"scene_{scenes[-1]['scene']:02d}.png").resolve()
    end_png = out_dir / "frames" / "scene_end.png"
    outro_img = end_png.resolve() if end_png.exists() else last_img
    print(f"Outro : {'scene_end.png' if end_png.exists() else 'hold last frame'}")

    # Segments: (image, n_frames, zoom_in). Alternate zoom direction for variety.
    segs = []
    for i, s in enumerate(scenes):
        img = (out_dir / "frames" / f"scene_{s['scene']:02d}.png").resolve()
        if i + 1 < len(scenes):
            dur = scenes[i + 1]["start"] - s["start"]
        else:
            dur = audio_dur - s["start"]
        if i == 0:
            dur += lead_in
        segs.append((img, max(1, round(dur * FPS)), i % 2 == 0))
    segs.append((outro_img, max(1, round(outro * FPS)), len(scenes) % 2 == 0))

    total_frames = sum(nf for _, nf, _ in segs)
    total = round(total_frames / FPS, 3)
    lead_ms = int(round(lead_in * 1000))
    output = (out_dir / (out or "final.mp4")).resolve()
    concat_file = out_dir / "concat.txt"
    kb_dir = out_dir / "_kb"

    if ken_burns:
        kb_dir.mkdir(exist_ok=True)
        lines = []
        print(f"Ken Burns: rendering {len(segs)} clips (supersample {KB_SUPER}x)...")
        for idx, (img, nf, zin) in enumerate(segs):
            clip = (kb_dir / f"kb_{idx:03d}.mp4").resolve()
            _kb_clip(img, nf, clip, zin, W, H)
            lines.append(f"file '{clip.as_posix()}'")
            print(f"  [{idx + 1}/{len(segs)}] {'zoom-in ' if zin else 'zoom-out'} {nf/FPS:.2f}s")
        concat_file.write_text("\n".join(lines), encoding="utf-8")
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
                f"[1:a]{voice}[a1];[2:a]volume={MUSIC_VOL}[a2];"
                f"[a1][a2]amix=inputs=2:duration=first:normalize=0,apad,atrim=0:{total}[a]")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
               "-i", str(audio), "-stream_loop", "-1", "-i", str(pathlib.Path(music).resolve()),
               "-filter_complex", filt, "-map", "[v]", "-map", "[a]"] + tail
        print(f"Music : {pathlib.Path(music).name} @ {int(MUSIC_VOL*100)}%")
    else:
        filt = f"{vid};[1:a]{voice},apad,atrim=0:{total}[a]"
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
               "-i", str(audio), "-filter_complex", filt, "-map", "[v]", "-map", "[a]"] + tail

    print("Muxing...")
    _run(cmd)

    size_mb = output.stat().st_size / 1_048_576
    print(f"OK -> {output}  ({size_mb:.1f} MB, ~{total:.1f}s)")
    concat_file.unlink()
    if ken_burns:
        shutil.rmtree(kb_dir, ignore_errors=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--landscape", action="store_true", help="output 1920x1080 instead of 1080x1920")
    ap.add_argument("--music", help="path to a background music file to mix under the voice")
    ap.add_argument("--out", help="output filename (default final.mp4)")
    ap.add_argument("--ken-burns", action="store_true", dest="ken_burns", help="slow zoom on every scene")
    ap.add_argument("--lead-in", type=float, default=LEAD_IN, dest="lead_in")
    ap.add_argument("--outro", type=float, default=OUTRO)
    ap.add_argument("--max-scenes", type=int, default=None, dest="max_scenes", help="debug: only first N scenes")
    args = ap.parse_args()
    assemble(args.slug, landscape=args.landscape, music=args.music, out=args.out,
             lead_in=args.lead_in, outro=args.outro, ken_burns=args.ken_burns, max_scenes=args.max_scenes)
