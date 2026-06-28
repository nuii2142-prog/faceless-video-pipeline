"""
Chatterbox clarity sweep — keep cfg=0.3, lower exaggeration for slower/clearer speech.
Also time-stretch eng_exag9_cfg3 as a reference comparison.
"""
import pathlib, torch, soundfile as sf, numpy as np
import librosa

PREP_REF = r"C:\Users\Darks\Documents\2026 YT Short Project\test_output\voice_ref_eng.wav"
OUT_DIR  = pathlib.Path(r"C:\Users\Darks\Documents\2026 YT Short Project\test_output")

GEN_TEXT = (
    "Hello everyone, and welcome back to the channel. "
    "Today, we are diving deep into the world of digital creation and artificial intelligence. "
    "Finding the perfect balance between a high-end GPU and a stable power supply "
    "is absolutely crucial for rendering photorealistic images. "
    "When you are generating high-quality prompts or optimizing your workflow, "
    "every single detail matters. "
    "Let's explore how we can push the boundaries of creative technology together."
)

from chatterbox.tts import ChatterboxTTS
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChatterboxTTS.from_pretrained(device=device)
print("Model loaded.\n")

# Lower exaggeration = slower, more measured, clearer articulation
configs = [
    ("clear_exag7_cfg3", 0.7, 0.3),
    ("clear_exag5_cfg3", 0.5, 0.3),
    ("clear_exag4_cfg3", 0.4, 0.3),
]

for name, exag, cfg in configs:
    print(f"Generating {name}  (exag={exag}, cfg={cfg})...")
    wav = model.generate(
        GEN_TEXT,
        audio_prompt_path=PREP_REF,
        exaggeration=exag,
        cfg_weight=cfg,
    )
    audio = wav.squeeze().cpu().numpy()
    out = OUT_DIR / f"{name}.wav"
    sf.write(str(out), audio, model.sr)
    print(f"  -> {out.name}  ({len(audio)/model.sr:.1f}s)")

# Also time-stretch the existing exag9_cfg3 to 85% speed (no pitch change)
src = OUT_DIR / "eng_exag9_cfg3.wav"
if src.exists():
    print(f"\nTime-stretching {src.name} to 85% speed...")
    audio, sr = sf.read(str(src), dtype="float32")
    stretched = librosa.effects.time_stretch(audio, rate=0.85)
    out = OUT_DIR / "eng_exag9_cfg3_slow85.wav"
    sf.write(str(out), stretched, sr)
    print(f"  -> {out.name}  ({len(stretched)/sr:.1f}s)")

print("\nDone. Compare clear_exag7/5/4 vs slow85 — pick the clearest voice.")
