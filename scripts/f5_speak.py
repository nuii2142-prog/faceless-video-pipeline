"""
f5_speak.py - generate narration in YOUR cloned voice with F5-TTS, then auto-clean it.

    ml-env\\Scripts\\python.exe scripts\\f5_speak.py <ref.wav> "<text or .txt>" [out.wav]

- <ref.wav> : a 6-12s CLEAN clip of your voice. Cleaner ref = cleaner output
              (F5 copies the room + mic of the reference, so use your best take).
- text      : a sentence in quotes, OR a path to a .txt script (e.g. script.txt).
- out.wav   : optional output path (default f5_out.wav in the current folder).

This box needs two fixes that are baked in here:
  1. torch 2.11's torchaudio uses torchcodec (needs FFmpeg<=7, box has FFmpeg 8) ->
     we shim torchaudio load/save to soundfile. (torchcodec is uninstalled.)
  2. F5 raw output can clip -> we pass it through clean_voice.py automatically.

Must run with the ml-env python (has f5-tts + torch + CUDA).
"""
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


def main():
    if len(sys.argv) < 3:
        sys.exit('usage: python scripts/f5_speak.py <ref.wav> "<text or .txt>" [out.wav]')
    ref = sys.argv[1]
    text_arg = sys.argv[2]
    p = Path(text_arg)
    text = p.read_text(encoding="utf-8") if text_arg.lower().endswith(".txt") and p.exists() else text_arg
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("f5_out.wav")
    raw = out.with_name(out.stem + "_raw.wav")

    from f5_tts.api import F5TTS

    print("loading F5TTS...")
    f5 = F5TTS()
    f5.infer(ref_file=ref, ref_text="", gen_text=text, file_wave=str(raw), nfe_step=48)

    # Auto-clean: fixes F5's hot/clipping output and evens the level for YouTube.
    cv = Path(__file__).with_name("clean_voice.py")
    subprocess.run([sys.executable, str(cv), str(raw), str(out)], check=True)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
