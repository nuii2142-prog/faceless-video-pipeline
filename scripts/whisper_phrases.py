"""Whisper timestamps + AUDIO-DRIVEN per-phrase segmentation.

The phrase boundaries come from the AUDIO ITSELF — Whisper's transcription
punctuation plus the real pauses between words — NOT from any pre-split phrase
list. One phrase = one scene = one future image.

This is the correct order: write script -> record voice -> THEN let the audio
define the scenes. (The old approach force-aligned a guessed phrase list and
drifted; that is gone.)

Usage:
  python scripts/whisper_phrases.py "<audio path>" <slug>

Outputs:
  output/<slug>/words.json   - [{word,start,end}, ...]            (word level, reference)
  output/<slug>/scenes.json  - [{scene,text,start,end,dur}, ...]  (per-phrase, for images)
"""
import sys, json, pathlib
from faster_whisper import WhisperModel

MODEL_SIZE = "base"     # base = clean timestamps on clean TTS audio; cpu/int8 is plenty

# Segmentation knobs (ponytail: sensible defaults, tune here if pacing feels off).
# Target ~1.5-3s per scene = Zen-style rapid one-image-per-phrase cutting.
STRONG = (".", "?", "!", ":", "—", "–")   # sentence / strong-clause enders -> always cut
SOFT = (",", ";")                          # soft clause enders -> cut only if long enough
SOFT_MIN = 1.0          # only honor a soft-punctuation cut once the phrase is >= this long
PAUSE_CUT = 0.60        # a silent gap >= this between words forces a cut (real breath/pause)
MIN_DUR = 0.70          # phrases shorter than this get merged into the previous one
MAX_DUR = 3.20          # phrases longer than this get split at their largest internal pause


def segment(words: list[dict]) -> list[list[dict]]:
    """Group word dicts into phrase groups using punctuation + pauses, then guard durations."""
    # 1) primary cut: punctuation + big pauses
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        tok = w["word"]
        dur = w["end"] - cur[0]["start"]
        gap = (words[i + 1]["start"] - w["end"]) if i + 1 < len(words) else 99.0
        if tok.endswith(STRONG) or (tok.endswith(SOFT) and dur >= SOFT_MIN) or gap >= PAUSE_CUT:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    # 2) merge too-short groups into the previous (no flash frames)
    merged = []
    for g in groups:
        d = g[-1]["end"] - g[0]["start"]
        if merged and d < MIN_DUR:
            merged[-1].extend(g)
        else:
            merged.append(g)

    # 3) split too-long groups, RECURSIVELY, until every piece fits MAX_DUR.
    # A single split pass left long continuous-speech runs (no internal pause >0.6s
    # to trigger a primary cut, and only one split allowed) still oversized — e.g. a
    # 16.8s "phrase" on real audio (the-wandering-mind, 2026-07-17). Split_long()
    # recurses, and falls back to a time-midpoint cut when no natural gap exists,
    # so continuous delivery still gets capped instead of passing through untouched.
    final = []
    for g in merged:
        final.extend(split_long(g))
    return final


def split_long(g: list[dict]) -> list[dict]:
    d = g[-1]["end"] - g[0]["start"]
    if d <= MAX_DUR or len(g) <= 1:
        return [g]
    k_best, gap_best = None, 0.0
    for k in range(len(g) - 1):
        gp = g[k + 1]["start"] - g[k]["end"]
        if gp > gap_best:
            gap_best, k_best = gp, k
    if k_best is None or gap_best <= 0.12:
        # no natural pause big enough -> cut nearest the time midpoint instead of
        # leaving the whole run unsplit
        target = (g[0]["start"] + g[-1]["end"]) / 2
        k_best = min(range(len(g) - 1), key=lambda k: abs(g[k]["end"] - target))
    left, right = g[:k_best + 1], g[k_best + 1:]
    if not left or not right:
        return [g]
    return split_long(left) + split_long(right)


def transcribe(audio_path: str, slug: str):
    out_dir = pathlib.Path("output") / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, word_timestamps=True, language="en")

    words = []
    for seg in segments:
        for w in (seg.words or []):
            tok = w.word.strip()
            if tok:
                words.append({"word": tok, "start": round(w.start, 3), "end": round(w.end, 3)})

    (out_dir / "words.json").write_text(
        json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")

    if not words:
        (out_dir / "scenes.json").write_text("[]", encoding="utf-8")
        print("ERROR: Whisper transcribed 0 words — check the audio file.")
        return

    groups = segment(words)
    scenes = []
    for i, g in enumerate(groups):
        scenes.append({
            "scene": i + 1,
            "text": " ".join(w["word"] for w in g),
            "start": round(g[0]["start"], 3),
            "end": round(g[-1]["end"], 3),
        })
    # clamp final scene to true audio end, then compute durations
    scenes[-1]["end"] = round(info.duration, 3)
    for sc in scenes:
        sc["dur"] = round(sc["end"] - sc["start"], 3)

    (out_dir / "scenes.json").write_text(
        json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- runnable check / report ----
    bad = [s["scene"] for s in scenes if s["dur"] <= 0]
    durs = [s["dur"] for s in scenes]
    assert not bad, f"zero/neg-duration scenes: {bad}"
    print(f"OK -- audio {info.duration:.1f}s | lang {info.language} ({info.language_probability:.2f})")
    print(f"   words: {len(words)} | scenes: {len(scenes)} | "
          f"dur min/avg/max: {min(durs):.2f}/{sum(durs)/len(durs):.2f}/{max(durs):.2f}s")
    print(f"   coverage: scene1 start={scenes[0]['start']}s  lastEnd={scenes[-1]['end']}s")
    print("   first 5:")
    for s in scenes[:5]:
        print(f"     #{s['scene']:>3} {s['start']:>6.2f}-{s['end']:>6.2f}  {s['text']}")
    print("   last 5:")
    for s in scenes[-5:]:
        print(f"     #{s['scene']:>3} {s['start']:>6.2f}-{s['end']:>6.2f}  {s['text']}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python scripts/whisper_phrases.py "<audio>" <slug>')
        sys.exit(1)
    transcribe(sys.argv[1], sys.argv[2])
