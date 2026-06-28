"""Phase E — Whisper word-level timestamps.

Usage:
  python scripts/phase_e_whisper.py <audio.wav> <slug>

Outputs:
  output/<slug>/words.json  — [{word, start, end}, ...]
"""
import sys, json, pathlib
from faster_whisper import WhisperModel

MODEL_SIZE = "base"  # ponytail: tiny works too, base for cleaner timestamps on TTS audio

def transcribe(audio_path: str, slug: str) -> list[dict]:
    out_dir = pathlib.Path("output") / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "words.json"

    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, word_timestamps=True, language="en")

    words = []
    for seg in segments:
        for w in (seg.words or []):
            words.append({"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)})

    out_file.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -- {len(words)} words -> {out_file}")
    print(f"   duration: {info.duration:.1f}s | lang: {info.language} ({info.language_probability:.2f})")
    return words

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/phase_e_whisper.py <audio.wav> <slug>")
        sys.exit(1)
    transcribe(sys.argv[1], sys.argv[2])
