"""Generate a YouTube-ready .srt subtitle file from scenes.json.

Sidecar file — NOT burned into the video. Upload it in YouTube Studio
(Subtitles → Add → Upload file) so viewers can toggle captions on/off.

Captions are GAP-FILLED: each cue holds until the next one begins, so there is
no on/off flicker during the small silences between phrases.

Whisper mishears are fixed per project: Phase B writes the pairs it spots into
output/<slug>/corrections.json ({"heard": "actually said", ...}). Only universal
spacing tidy-ups live in the global map below — project-specific fixes must never
leak into other videos' captions.

Usage:
  python scripts/make_srt.py <slug>
Output:
  output/<slug>/<slug>.srt
"""
import json, pathlib, re, sys

# Universal spacing tidy-ups Whisper injects around digits (apply to EVERY project via regex,
# so no video has to list "82 %", "46 .9 %", "10 ,000" by hand).
SPACING_FIXES = [
    (re.compile(r"(\d)\s+\.\s*(\d)"), r"\1.\2"),   # 46 .9 -> 46.9
    (re.compile(r"(\d)\s+,\s*(\d)"), r"\1,\2"),    # 10 ,000 -> 10,000
    (re.compile(r"(\d)\s+%"), r"\1%"),             # 82 % -> 82%
    (re.compile(r"(\w)\s+-(\w)"), r"\1-\2"),       # to -do -> to-do, great -grandparents
]


def load_corrections(d: pathlib.Path) -> dict:
    """Project-specific Whisper mishears (names, Pali terms, wrong stats)."""
    f = d / "corrections.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def ts(sec: float) -> str:
    """Seconds -> SRT timestamp HH:MM:SS,mmm."""
    if sec < 0:
        sec = 0.0
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fix(text: str, corr: dict) -> str:
    for a, b in corr.items():          # project mishears first (may contain the raw spaced form)
        text = text.replace(a, b)
    for pat, repl in SPACING_FIXES:    # then universal digit-spacing cleanup
        text = pat.sub(repl, text)
    return text


def main(slug: str):
    d = pathlib.Path("output") / slug
    scenes = json.loads((d / "scenes.json").read_text(encoding="utf-8"))
    corr = load_corrections(d)

    blocks = []
    for i, s in enumerate(scenes):
        start = s["start"]
        end = scenes[i + 1]["start"] if i + 1 < len(scenes) else s["end"]
        if end <= start:                       # safety: never zero/negative
            end = s["end"]
        blocks.append(f"{i + 1}\n{ts(start)} --> {ts(end)}\n{fix(s['text'], corr)}\n")

    out = d / f"{slug}.srt"
    out.write_text("\n".join(blocks), encoding="utf-8")

    # runnable check: monotonic, no overlaps
    assert all(scenes[i]["start"] <= scenes[i + 1]["start"] for i in range(len(scenes) - 1)), \
        "scenes not in time order"
    print(f"OK -> {out}")
    print(f"   {len(scenes)} cues | runtime {ts(scenes[-1]['end'])} | "
          f"{len(corr)} project fixes + {len(SPACING_FIXES)} spacing rules")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/make_srt.py <slug>")
    main(sys.argv[1])
