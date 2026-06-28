"""Test Chatterbox voice cloning with Nuay's recorded voice."""
import os, pathlib, sys

VOICE_FILE = r"C:\Users\Darks\Documents\2026 YT Short Project\Recording Voice Training.wav"
OUT_DIR = pathlib.Path(r"C:\Users\Darks\Documents\2026 YT Short Project\test_output")
OUT_DIR.mkdir(exist_ok=True)

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Voice file: {VOICE_FILE}")

from chatterbox.tts import ChatterboxTTS

print("Loading Chatterbox model (downloads ~3GB on first run)...")
model = ChatterboxTTS.from_pretrained(device=device)
print("Model loaded.")

TEST_TEXT = "I grew up on an organic farm in Thailand. Every morning before sunrise, I work in the fields with my family."

print(f"Generating speech...")
wav = model.generate(
    TEST_TEXT,
    audio_prompt_path=VOICE_FILE,
    exaggeration=0.5,
    cfg_weight=0.5,
)

import soundfile as sf
out_path = OUT_DIR / "test_cloned_voice.wav"
sf.write(str(out_path), wav.squeeze().cpu().numpy(), model.sr)
print(f"\nSUCCESS: {out_path}")
print(f"Duration: {wav.shape[-1] / model.sr:.1f} seconds")
