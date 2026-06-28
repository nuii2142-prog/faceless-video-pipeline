"""Generate a YouTube-ready .srt subtitle file from scenes.json.

Sidecar file — NOT burned into the video. Upload it in YouTube Studio
(Subtitles → Add → Upload file) so viewers can toggle captions on/off.

Captions are GAP-FILLED: each cue holds until the next one begins, so there is
no on/off flicker during the small silences between phrases. A CORRECTIONS map
fixes obvious Whisper mishears (the audio actually says the corrected form).

Usage:
  python scripts/make_srt.py <slug>
Output:
  output/<slug>/<slug>.srt
"""
import json, pathlib, sys

# Whisper mishears / caption tidy-ups. Audio truly says the right-hand form.
CORRECTIONS = {
    "tie village": "Thai village",   # Whisper misheard "Thai"
    "40 %": "40%",
    "5am wakeups": "5 AM wake-ups",
}


def ts(sec: float) -> str:
    """Seconds -> SRT timestamp HH:MM:SS,mmm."""
    if sec < 0:
        sec = 0.0
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fix(text: str) -> str:
    for a, b in CORRECTIONS.items():
        text = text.replace(a, b)
    return text


def main(slug: str):
    d = pathlib.Path("output") / slug
    scenes = json.loads((d / "scenes.json").read_text(encoding="utf-8"))

    blocks = []
    for i, s in enumerate(scenes):
        start = s["start"]
        end = scenes[i + 1]["start"] if i + 1 < len(scenes) else s["end"]
        if end <= start:                       # safety: never zero/negative
            end = s["end"]
        blocks.append(f"{i + 1}\n{ts(start)} --> {ts(end)}\n{fix(s['text'])}\n")

    out = d / f"{slug}.srt"
    out.write_text("\n".join(blocks), encoding="utf-8")

    # runnable check: monotonic, no overlaps
    assert all(scenes[i]["start"] <= scenes[i + 1]["start"] for i in range(len(scenes) - 1)), \
        "scenes not in time order"
    print(f"OK -> {out}")
    print(f"   {len(scenes)} cues | runtime {ts(scenes[-1]['end'])} | corrections: {list(CORRECTIONS)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/make_srt.py <slug>")
    main(sys.argv[1])
