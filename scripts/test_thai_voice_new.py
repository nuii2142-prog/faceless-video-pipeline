"""
Preprocess new Thai voice.wav (normalize + pick best 20s) then clone to English.
gen_text = English pangram script Nuay provided.
"""
import pathlib, torch, soundfile as sf, numpy as np
import scipy.signal as sig

RAW   = r"C:\Users\Darks\Documents\2026 YT Short Project\Thai voice.wav"
OUT_DIR = pathlib.Path(r"C:\Users\Darks\Documents\2026 YT Short Project\test_output")

GEN_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "A rare, beautiful vintage zoom lens can quickly capture the magnificent glow of the setting sun. "
    "We eagerly expect the heavy thunderstorm to safely pass by the quiet village. "
    "Zebras, chimpanzees, and yellow kangaroos jump gracefully across the wide zoo enclosures. "
    "Exactly how much water flows beneath the ancient bridge?"
)

# ── Preprocess ───────────────────────────────────────────────────────────────
audio, sr = sf.read(RAW, dtype="float32", always_2d=True)
mono = audio.mean(axis=1)                         # stereo -> mono

# Resample to 24kHz
if sr != 24000:
    mono = sig.resample(mono, int(len(mono) * 24000 / sr))
    sr = 24000

# Normalize to -18 dBFS RMS (voice clone sweet spot)
rms = np.sqrt(np.mean(mono**2))
mono = mono * (10**(-18/20) / (rms + 1e-9))
mono = np.clip(mono, -1.0, 1.0)

# Find the most speech-dense 20s window (highest RMS)
win = 20 * sr
best_start, best_rms = 0, 0.0
for i in range(0, len(mono) - win, sr // 4):    # step 0.25s
    w_rms = float(np.sqrt(np.mean(mono[i:i+win]**2)))
    if w_rms > best_rms:
        best_rms, best_start = w_rms, i

ref_audio = mono[best_start : best_start + win]
ref_path  = str(OUT_DIR / "voice_ref_thai_new.wav")
sf.write(ref_path, ref_audio, sr)
print(f"Ref: {best_start/sr:.1f}s-{(best_start+win)/sr:.1f}s  RMS={20*np.log10(best_rms+1e-9):.1f}dBFS  -> {ref_path}")

# ── Clone ────────────────────────────────────────────────────────────────────
from chatterbox.tts import ChatterboxTTS
device = "cuda" if torch.cuda.is_available() else "cpu"
model  = ChatterboxTTS.from_pretrained(device=device)
print(f"Model loaded  ({device})\n")

configs = [
    ("thai_new_exag5_cfg3", 0.5, 0.3),
    ("thai_new_exag4_cfg3", 0.4, 0.3),
]

for name, exag, cfg in configs:
    print(f"Generating {name}  (exag={exag}, cfg={cfg})...")
    wav = model.generate(GEN_TEXT, audio_prompt_path=ref_path,
                         exaggeration=exag, cfg_weight=cfg)
    out = OUT_DIR / f"{name}.wav"
    sf.write(str(out), wav.squeeze().cpu().numpy(), model.sr)
    print(f"  -> {out.name}  ({wav.shape[-1]/model.sr:.1f}s)")

print("\nDone.")
