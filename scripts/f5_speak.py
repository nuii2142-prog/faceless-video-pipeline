"""
f5_speak.py - generate narration in YOUR cloned voice with F5-TTS, then auto-clean it.

    ml-env\\Scripts\\python.exe scripts\\f5_speak.py <ref.wav> "<text or .txt>" [out.wav] [ref_text or .txt] [--speed 0.85]

- <ref.wav>  : a 6-12s CLEAN clip of your voice (F5 hard-caps the ref at ~12s; it copies
               the room + mic of the reference, so use your best take).
- text       : a sentence in quotes, OR a path to a .txt script (e.g. script.txt).
- out.wav    : optional output path (default f5_out.wav in the current folder).
- ref_text   : optional transcript of the reference clip (text or .txt). Matching it to the
               ref EXACTLY improves cloning a lot; omit to let Whisper auto-transcribe.
- --speed    : speaking pace multiplier (default 0.85 — Nuay's calm narration pace).

Settings per F5 TTS/f5_tts_install_instructions.md: nfe_step=85 (clarity saturation),
cfg_strength=2.0, sway off (bfloat16 bug at high NFE), remove_silence off, cross_fade 0.15.

Baked-in Windows fixes:
  1. import datasets BEFORE torch (pyarrow/torch C++ DLL clash -> silent segfault).
  2. torch 2.x torchaudio uses torchcodec (needs FFmpeg<=7, box has FFmpeg 8) ->
     we shim torchaudio load/save to soundfile. (torchcodec is uninstalled.)
  3. F5 raw output can clip -> we pass it through clean_voice.py automatically.

Must run with the ml-env python (has f5-tts + torch + CUDA).
"""
import datasets  # noqa: F401  MUST be first — avoids pyarrow/torch DLL crash on Windows
import sys
import subprocess
from pathlib import Path

import numpy as np
import torch
import soundfile as sf
import torchaudio


def _sf_load(path, *a, **k):
    d, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return torch.from_numpy(d.T), sr


def _sf_save(path, wav, sr, *a, **k):
    arr = wav.detach().cpu().numpy() if hasattr(wav, "detach") else np.asarray(wav)
    if arr.ndim == 2:
        arr = arr.T
    sf.write(str(path), arr, sr)


torchaudio.load = _sf_load
torchaudio.save = _sf_save


def _read_text_arg(arg):
    p = Path(arg)
    return p.read_text(encoding="utf-8").strip() if arg.lower().endswith(".txt") and p.exists() else arg


def main():
    args = list(sys.argv[1:])
    speed = 0.85
    if "--speed" in args:
        i = args.index("--speed")
        speed = float(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit('usage: python scripts/f5_speak.py <ref.wav> "<text or .txt>" [out.wav] [ref_text or .txt] [--speed 0.85]')
    ref = args[0]
    text = _read_text_arg(args[1])
    out = Path(args[2]) if len(args) > 2 else Path("f5_out.wav")
    ref_text = _read_text_arg(args[3]) if len(args) > 3 else ""
    raw = out.with_name(out.stem + "_raw.wav")

    from f5_tts.api import F5TTS

    print(f"loading F5TTS...  (speed {speed}, nfe 85)")
    f5 = F5TTS()
    f5.infer(
        ref_file=ref,
        ref_text=ref_text,               # "" -> F5 auto-transcribes the ref with Whisper
        gen_text=text,
        file_wave=str(raw),
        nfe_step=85,                     # clarity saturation point
        speed=speed,
        cfg_strength=2.0,
        sway_sampling_coef=None,         # off: bfloat16 bug at high NFE
        remove_silence=False,            # keep natural gaps; trimming makes pacing jumpy
        cross_fade_duration=0.15,
    )

    # Auto-clean: fixes F5's hot/clipping output and evens the level for YouTube.
    cv = Path(__file__).with_name("clean_voice.py")
    subprocess.run([sys.executable, str(cv), str(raw), str(out)], check=True)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
