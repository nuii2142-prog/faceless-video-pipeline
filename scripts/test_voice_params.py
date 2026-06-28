"""
Test Chatterbox with preprocessed audio + parameter sweep.
Converts voice file to mono 24kHz and tries exaggeration 0.5 / 0.7 / 0.9.
"""
import os, pathlib
import numpy as np
import soundfile as sf
import librosa
import torch
from chatterbox.tts import ChatterboxTTS

VOICE_FILE = r"C:\Users\Darks\Documents\2026 YT Short Project\Recording Voice Training.wav"
OUT_DIR = pathlib.Path(r"C:\Users\Darks\Documents\2026 YT Short Project\test_output")
OUT_DIR.mkdir(exist_ok=True)
PREP_FILE = str(OUT_DIR / "voice_ref_prep.wav")

TARGET_SR = 24000  # 24kHz mono — best for Chatterbox
CLIP_SEC = 20      # first 20 clean seconds of speech

TEST_TEXT = (
    "I grew up on an organic farm in Thailand. "
    "Every morning before sunrise, I walk through the rice fields with my family."
)

# ── Step 1: Preprocess reference audio ──────────────────────────────────────
print("Preprocessing voice reference...")
audio, sr = librosa.load(VOICE_FILE, sr=TARGET_SR, mono=True)

# Trim leading/trailing silence
audio, _ = librosa.effects.trim(audio, top_db=30)

# Keep first CLIP_SEC seconds
clip = audio[: TARGET_SR * CLIP_SEC]
sf.write(PREP_FILE, clip, TARGET_SR)
print(f"  Saved {len(clip)/TARGET_SR:.1f}s mono {TARGET_SR}Hz -> {PREP_FILE}")

# ── Step 2: Load model ───────────────────────────────────────────────────────
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\nDevice: {device} ({torch.cuda.get_device_name(0) if device=='cuda' else 'cpu'})")
model = ChatterboxTTS.from_pretrained(device=device)
print("Model loaded.\n")

# ── Step 3: Parameter sweep ──────────────────────────────────────────────────
# exaggeration: voice similarity strength (higher = closer to reference voice)
# cfg_weight:   guidance strength (lower = more natural-sounding)
PARAMS = [
    (0.5, 0.5),   # default
    (0.7, 0.4),   # more voice similarity
    (0.9, 0.3),   # strongest clone, most natural guidance
]

for exag, cfg in PARAMS:
    tag = f"exag{int(exag*10)}_cfg{int(cfg*10)}"
    out = OUT_DIR / f"voice_{tag}.wav"
    print(f"Generating exaggeration={exag}, cfg_weight={cfg}...")
    wav = model.generate(
        TEST_TEXT,
        audio_prompt_path=PREP_FILE,
        exaggeration=exag,
        cfg_weight=cfg,
    )
    sf.write(str(out), wav.squeeze().cpu().numpy(), model.sr)
    print(f"  -> {out.name}  ({wav.shape[-1]/model.sr:.1f}s)\n")

print("Done. Listen to voice_exag5_cfg5.wav / voice_exag7_cfg4.wav / voice_exag9_cfg3.wav")
print("and tell me which sounds most like you.")
