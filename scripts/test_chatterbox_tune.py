"""
Chatterbox fine-tune test using Nuay's English voice recording.
Reference audio: '20 sec voice eng.wav' (English, matches gen_text language)
Sweeps cfg_weight at exag=0.9 (Nuay's preferred exaggeration level).
"""
import pathlib, torch, soundfile as sf, numpy as np
import scipy.signal as sig

RAW_REF  = r"C:\Users\Darks\Documents\2026 YT Short Project\20 sec voice eng.wav"
PREP_REF = r"C:\Users\Darks\Documents\2026 YT Short Project\test_output\voice_ref_eng.wav"
OUT_DIR  = pathlib.Path(r"C:\Users\Darks\Documents\2026 YT Short Project\test_output")

# Script Nuay provided — used as gen_text
GEN_TEXT = (
    "Hello everyone, and welcome back to the channel. "
    "Today, we are diving deep into the world of digital creation and artificial intelligence. "
    "Finding the perfect balance between a high-end GPU and a stable power supply "
    "is absolutely crucial for rendering photorealistic images. "
    "When you are generating high-quality prompts or optimizing your workflow, "
    "every single detail matters. "
    "Let's explore how we can push the boundaries of creative technology together."
)

# Preprocess reference: mono 24kHz 20s
audio, sr = sf.read(RAW_REF, dtype="float32", always_2d=True)
audio = audio.mean(axis=1) if audio.shape[1] > 1 else audio[:, 0]
if sr != 24000:
    audio = sig.resample(audio, int(len(audio) * 24000 / sr))
    sr = 24000
audio = audio[: 20 * sr]  # 20s ref (Chatterbox handles longer than F5-TTS)
sf.write(PREP_REF, audio, sr)
print(f"Prepared ref: {len(audio)/sr:.1f}s mono {sr}Hz")

from chatterbox.tts import ChatterboxTTS
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'cpu'})")

model = ChatterboxTTS.from_pretrained(device=device)
print("Model loaded.\n")

# Sweep: exag=0.9 fixed (Nuay liked this), vary cfg_weight
configs = [
    ("eng_exag9_cfg2", 0.9, 0.2),
    ("eng_exag9_cfg3", 0.9, 0.3),  # previous favourite
    ("eng_exag9_cfg5", 0.9, 0.5),
]

for name, exag, cfg in configs:
    print(f"Generating {name}  (exag={exag}, cfg={cfg})...")
    wav = model.generate(
        GEN_TEXT,
        audio_prompt_path=PREP_REF,
        exaggeration=exag,
        cfg_weight=cfg,
    )
    out = OUT_DIR / f"{name}.wav"
    sf.write(str(out), wav.squeeze().cpu().numpy(), model.sr)
    print(f"  -> {out.name}  ({wav.shape[-1]/model.sr:.1f}s)")

print("\nDone. Listen to eng_exag9_cfg2 / cfg3 / cfg5 and pick the best.")
