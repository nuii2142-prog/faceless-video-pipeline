"""Phase D — Chatterbox TTS narration generation.

Usage:
  python scripts/phase_d_tts.py <slug>

Reads:  output/<slug>/script.txt
Writes: output/<slug>/narration.wav
Config: voice_config.py (VOICE_REF, EXAGGERATION, CFG_WEIGHT)
"""
import sys, pathlib, soundfile as sf, torch, librosa, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from voice_config import VOICE_REF, EXAGGERATION, CFG_WEIGHT
from chatterbox.tts import ChatterboxTTS

def generate(slug: str) -> pathlib.Path:
    out_dir = pathlib.Path("output") / slug
    script  = (out_dir / "script.txt").read_text(encoding="utf-8").strip()
    out_wav = out_dir / "narration.wav"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device} | exag={EXAGGERATION} cfg={CFG_WEIGHT}")
    print(f"Ref:    {VOICE_REF}")
    print(f"Words:  {len(script.split())}")

    model = ChatterboxTTS.from_pretrained(device=device)
    wav   = model.generate(script, audio_prompt_path=VOICE_REF,
                           exaggeration=EXAGGERATION, cfg_weight=CFG_WEIGHT)

    audio = wav.squeeze().cpu().numpy()
    # ponytail: stretch to target pace; 0.78 puts 99-word Titan output at ~35s
    audio = librosa.effects.time_stretch(audio, rate=0.78)
    sf.write(str(out_wav), audio, model.sr)
    print(f"OK -- {len(audio)/model.sr:.1f}s -> {out_wav}")
    return out_wav

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/phase_d_tts.py <slug>")
        sys.exit(1)
    generate(sys.argv[1])
