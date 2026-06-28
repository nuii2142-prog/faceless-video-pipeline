"""Assemble the test clip: frames/ + ElevenLabs audio → final.mp4

Gapless: each frame holds from its scene start until the next scene starts.
Last frame holds until audio ends (via -shortest).

Usage:
  python scripts/assemble_clip.py why-young-people-dont-want-to-farm

Reads:  output/<slug>/scenes.json           (per-phrase start/end timings)
        output/<slug>/frames/scene_NN.png   (ComfyUI images, zero-padded N)
        output/<slug>/*.mp3                 (ElevenLabs audio — first .mp3 found)
Writes: output/<slug>/concat.txt            (intermediate, safe to delete)
        output/<slug>/final.mp4
"""
import json, pathlib, subprocess, sys

FPS = 30
MUSIC_VOL = 0.12   # background music level under the voice (~12%)


def assemble(slug: str, landscape: bool = False, music: str = None):
    WIDTH, HEIGHT = (1920, 1080) if landscape else (1080, 1920)
    out_dir = pathlib.Path("output") / slug

    scenes = json.loads((out_dir / "scenes.json").read_text(encoding="utf-8"))

    mp3s = list(out_dir.glob("*.mp3"))
    if not mp3s:
        sys.exit(f"No .mp3 found in {out_dir}")
    audio = mp3s[0].resolve()
    print(f"Audio : {mp3s[0].name}")
    print(f"Scenes: {len(scenes)}")

    # Verify all frames exist before starting
    missing = [f"scene_{s['scene']:02d}.png" for s in scenes
               if not (out_dir / "frames" / f"scene_{s['scene']:02d}.png").exists()]
    if missing:
        sys.exit(f"Missing {len(missing)} frame(s): {', '.join(missing[:5])}"
                 + ("..." if len(missing) > 5 else ""))

    # Build concat.txt — gapless durations
    # Frame N holds from scenes[N].start to scenes[N+1].start.
    # Last frame: hold from its start to (last_scene.end + 1s tail); -shortest trims to audio.
    concat_file = out_dir / "concat.txt"
    lines = []
    for i, s in enumerate(scenes):
        img = (out_dir / "frames" / f"scene_{s['scene']:02d}.png").resolve()
        if i + 1 < len(scenes):
            dur = round(scenes[i + 1]["start"] - s["start"], 3)
        else:
            dur = round((s["end"] - s["start"]) + 1.5, 3)  # tail; -shortest stops at audio
        lines.append(f"file '{img.as_posix()}'\nduration {dur}")
    # Repeat last file (required by concat demuxer to flush final frame)
    last_img = (out_dir / "frames" / f"scene_{scenes[-1]['scene']:02d}.png").resolve()
    lines.append(f"file '{last_img.as_posix()}'")
    concat_file.write_text("\n".join(lines), encoding="utf-8")

    output = (out_dir / "final.mp4").resolve()
    scale_pad = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=white"
    )

    tail = [
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-shortest", str(output),
    ]
    if music:
        # voice at full + music looped under it at MUSIC_VOL; normalize=0 keeps voice loud
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio),
            "-stream_loop", "-1", "-i", str(pathlib.Path(music).resolve()),
            "-filter_complex",
            f"[0:v]{scale_pad}[v];[1:a]volume=1[a1];[2:a]volume={MUSIC_VOL}[a2];"
            f"[a1][a2]amix=inputs=2:duration=first:normalize=0[a]",
            "-map", "[v]", "-map", "[a]",
        ] + tail
        print(f"Music : {pathlib.Path(music).name} @ {int(MUSIC_VOL*100)}%")
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio),
            "-vf", scale_pad,
        ] + tail

    print("Assembling...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-2000:])
        sys.exit(1)

    size_mb = output.stat().st_size / 1_048_576
    total_s = scenes[-1]["end"]
    print(f"OK -> {output}  ({size_mb:.1f} MB, ~{total_s:.1f}s)")
    concat_file.unlink()  # clean up


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--landscape", action="store_true", help="output 1920x1080 instead of 1080x1920")
    ap.add_argument("--music", help="path to a background music file to mix under the voice")
    args = ap.parse_args()
    assemble(args.slug, landscape=args.landscape, music=args.music)
