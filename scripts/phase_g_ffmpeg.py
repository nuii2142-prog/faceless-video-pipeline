"""Phase G -- FFmpeg final video assembly.

Usage:
  python scripts/phase_g_ffmpeg.py <slug>

Reads:  output/<slug>/narration.wav
        output/<slug>/scenes.json
        output/<slug>/words.json
Writes: output/<slug>/captions.srt   (sidecar; load in player or burn in later)
        output/<slug>/final.mp4
"""
import sys, json, pathlib, subprocess

WORDS_PER_CUE = 4
WIDTH, HEIGHT  = 1080, 1920
FPS            = 30

def _ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

def _make_srt(words: list[dict], out_path: pathlib.Path):
    cues, i, idx = [], 0, 1
    while i < len(words):
        chunk = words[i : i + WORDS_PER_CUE]
        text  = " ".join(w["word"] for w in chunk)
        start, end = chunk[0]["start"], chunk[-1]["end"]
        cues.append(f"{idx}\n{_ts(start)} --> {_ts(end)}\n{text}\n")
        i += WORDS_PER_CUE
        idx += 1
    out_path.write_text("\n".join(cues), encoding="utf-8")

def assemble(slug: str):
    out_dir = pathlib.Path("output") / slug
    scenes  = json.loads((out_dir / "scenes.json").read_text(encoding="utf-8"))
    words   = json.loads((out_dir / "words.json").read_text(encoding="utf-8"))
    audio   = (out_dir / "narration.wav").resolve()
    srt     = out_dir / "captions.srt"
    output  = (out_dir / "final.mp4").resolve()

    _make_srt(words, srt)
    print(f"Captions: {srt.name}  (burning in...)")

    # run FFmpeg from out_dir so captions.srt needs no path — avoids Windows
    # space-in-path escaping issues in the subtitles filter
    cwd = out_dir.resolve()

    # inputs: one image per scene (absolute path) + audio last
    cmd = ["ffmpeg", "-y"]
    for s in scenes:
        dur = round(s["end"] - s["start"], 3)
        cmd += ["-loop", "1", "-t", str(dur), "-i",
                str(pathlib.Path(s["image"]).resolve())]
    cmd += ["-i", str(audio)]

    n         = len(scenes)
    audio_idx = n

    scale = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=white"
    )
    filter_parts = [f"[{i}:v]{scale}[v{i}]" for i in range(n)]
    concat_in    = "".join(f"[v{i}]" for i in range(n))
    filter_parts.append(f"{concat_in}concat=n={n}:v=1:a=0[vout]")
    filter_complex = ";".join(filter_parts)

    raw = output.with_name("final_raw.mp4")
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-shortest", str(raw),
    ]

    print("Pass 1: assembling slideshow...")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    if r.returncode != 0:
        print("STDERR:", r.stderr[-1500:])
        sys.exit(1)

    # Pass 2: burn captions.
    # force_style uses ASS comma-separated props; in FFmpeg filter strings
    # (even via subprocess) commas are filter-chain separators → escape as \,
    cap_style = (
        "FontSize=65\\,Bold=1"
        "\\,PrimaryColour=&H00FFFFFF"
        "\\,OutlineColour=&H00000000\\,Outline=3\\,Shadow=1"
        "\\,Alignment=2\\,MarginV=80"
    )
    cmd2 = [
        "ffmpeg", "-y",
        "-i", str(raw),
        "-vf", f"subtitles=captions.srt:force_style={cap_style}",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "copy",
        str(output),
    ]
    print("Pass 2: burning captions...")
    r2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=str(cwd))
    if r2.returncode != 0:
        print("STDERR:", r2.stderr[-1500:])
        sys.exit(1)
    raw.unlink()  # remove intermediate

    size_mb = output.stat().st_size / 1_048_576
    dur_s   = words[-1]["end"]
    print(f"OK -- {output.name}  ({size_mb:.1f} MB, {dur_s:.1f}s)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/phase_g_ffmpeg.py <slug>")
        sys.exit(1)
    assemble(sys.argv[1])
