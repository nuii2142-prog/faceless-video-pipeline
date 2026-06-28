"""
Cross-lingual clone: Thai reference audio -> English output.
Hypothesis: native Thai speech gives cleaner voice fingerprint than accented English.
Compares Thai-ref vs English-ref at same params (exag=0.5, cfg=0.3).
"""
import pathlib, torch, soundfile as sf

THAI_REF = r"C:\Users\Darks\Documents\2026 YT Short Project\test_output\voice_ref_prep.wav"
ENG_REF  = r"C:\Users\Darks\Documents\2026 YT Short Project\test_output\voice_ref_eng.wav"
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

configs = [
    ("thai_ref_exag5_cfg3", THAI_REF),
    ("thai_ref_exag4_cfg3", THAI_REF),
    # English ref for direct comparison
    ("eng_ref_exag5_cfg3",  ENG_REF),
]
exags = [0.5, 0.4, 0.5]

for (name, ref), exag in zip(configs, exags):
    ref_lang = "THAI" if "thai" in name else "ENG"
    print(f"Generating [{ref_lang} ref]  {name}  (exag={exag}, cfg=0.3)...")
    wav = model.generate(
        GEN_TEXT,
        audio_prompt_path=ref,
        exaggeration=exag,
        cfg_weight=0.3,
    )
    out = OUT_DIR / f"{name}.wav"
    sf.write(str(out), wav.squeeze().cpu().numpy(), model.sr)
    print(f"  -> {out.name}  ({wav.shape[-1]/model.sr:.1f}s)")

print("\nDone. Compare thai_ref vs eng_ref — which sounds more like you?")
