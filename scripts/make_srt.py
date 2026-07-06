"""Generate a YouTube-ready .srt by aligning the TRUE script text to accurate
large-v3 WORD timestamps from the recorded audio.

Sidecar file — NOT burned into the video. Upload it in YouTube Studio
(Subtitles -> Add -> Upload file) so viewers can toggle captions on/off.

Why this method (2026-07-06): the older make_srt read phrase timings straight
from scenes.json, which came from whisper_phrases' small "base" model — its
phrase-START timestamps lag ~0.3-0.7s behind the real word onsets, so captions
drifted LATE. Here we take timings from large-v3 WORD timestamps (accurate) and
the TEXT from script.txt (correct — no whisper mishears, no TTS glitches), then
align the two. Works for both TTS and a real accented voice (difflib aligns fuzzily).

Usage:  ml-env\\Scripts\\python.exe scripts\\make_srt.py <slug>
        (needs faster-whisper + CUDA — run with the ml-env python, not the general one)
Reads:  output/<slug>/script.txt , output/<slug>/voice.wav
Writes: output/<slug>/<slug>.srt
"""
import re, sys, difflib, pathlib
from faster_whisper import WhisperModel

MODEL = "large-v3"          # word-timestamp accuracy matters here; base drifts
MAX_WORDS = 12              # hard cap per cue when no punctuation break
MAX_SECS = 5.5
LEAD_IN = 1.0               # MUST equal assemble_clip.py LEAD_IN — the video holds frame 1
                           # this long BEFORE the voice, so every cue shifts later by it.
                           # (voice.wav has no lead-in; the final .mp4 does.)


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
    if ms == 1000: s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main(slug):
    base = pathlib.Path("output") / slug
    script = (base / "script.txt").read_text(encoding="utf-8")
    stoks = script.split()
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    snorm = [norm(t) for t in stoks]

    model = WhisperModel(MODEL, device="cuda", compute_type="float16")
    segs, _ = model.transcribe(str(base / "voice.wav"), language="en", vad_filter=True,
                               condition_on_previous_text=False, word_timestamps=True)
    aw = [(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or []) if w.word.strip()]
    anorm = [norm(w) for w, _, _ in aw]

    # align script tokens -> audio word times
    st = [None] * len(stoks)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, snorm, anorm, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                _, ss, ee = aw[j1 + k]; st[i1 + k] = (ss, ee)
    known = [i for i, v in enumerate(st) if v]
    for idx in range(len(st)):
        if st[idx] is None:
            prev = max([k for k in known if k < idx], default=None)
            nxt = min([k for k in known if k > idx], default=None)
            if prev is not None and nxt is not None:
                a, b = st[prev][1], st[nxt][0]; t = a + (b - a) * ((idx - prev) / (nxt - prev)); st[idx] = (t, t + 0.2)
            elif prev is not None: st[idx] = (st[prev][1], st[prev][1] + 0.2)
            elif nxt is not None: st[idx] = (max(0, st[nxt][0] - 0.2), st[nxt][0])
            else: st[idx] = (0.0, 0.2)

    # group into cues on punctuation / caps
    cues, cur, cstart = [], [], None
    for i, tok in enumerate(stoks):
        if cstart is None: cstart = st[i][0]
        cur.append(tok)
        if re.search(r"[.!?]$", tok) or tok.endswith(",") or len(cur) >= MAX_WORDS or (st[i][1] - cstart) >= MAX_SECS:
            cues.append([cstart, st[i][1], " ".join(cur)]); cur, cstart = [], None
    if cur: cues.append([cstart, st[-1][1], " ".join(cur)])

    # merge a <=2-word tail into the previous cue only if that cue is mid-sentence
    merged = []
    for c in cues:
        if merged and len(c[2].split()) <= 2 and not re.search(r"[.!?]$", merged[-1][2]):
            merged[-1][1] = c[1]; merged[-1][2] += " " + c[2]
        else:
            merged.append(c)

    for i in range(len(merged)):
        if merged[i][1] <= merged[i][0]: merged[i][1] = merged[i][0] + 0.4
        if i + 1 < len(merged) and merged[i][1] > merged[i + 1][0]: merged[i][1] = merged[i + 1][0] - 0.01

    out = base / f"{slug}.srt"
    with open(out, "w", encoding="utf-8") as f:
        for i, (s, e, txt) in enumerate(merged, 1):
            f.write(f"{i}\n{ts(s + LEAD_IN)} --> {ts(e + LEAD_IN)}\n{txt}\n\n")
    print(f"OK -> {out}\n   {len(merged)} cues | runtime {ts(merged[-1][1])} | script-aligned to {MODEL} word timings")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: ml-env\\Scripts\\python.exe scripts\\make_srt.py <slug>")
    main(sys.argv[1])
