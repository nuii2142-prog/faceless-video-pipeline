"""
Test F5-TTS voice cloning with Nuay's English voice recording.
- Patches torchaudio.load to use soundfile (avoids torchcodec DLL issue)
- Uses manually-verified ref_text (Whisper hallucinated garbage on Thai audio)
"""
import pathlib, torch, soundfile as sf, numpy as np

RAW_REF  = r"C:\Users\Darks\Documents\2026 YT Short Project\20 sec voice eng.wav"
PREP_REF = r"C:\Users\Darks\Documents\2026 YT Short Project\test_output\voice_ref_prep_eng.wav"
OUT_DIR  = pathlib.Path(r"C:\Users\Darks\Documents\2026 YT Short Project\test_output")

# Exact text Nuay spoke in the reference recording
REF_TEXT = (
    "Hello everyone, and welcome back to the channel. Today, we are diving deep into "
    "the world of digital creation and artificial intelligence. Finding the perfect balance "
    "between a high-end GPU and a stable power supply is absolutely crucial for rendering "
    "photorealistic images. When you are generating high-quality prompts or optimizing your "
    "workflow, every single detail matters. Let's explore how we can push the boundaries of "
    "creative technology together"
)

TEST_TEXT = (
    "I grew up on an organic farm in Thailand. "
    "Every morning before sunrise, I walk through the rice fields with my family. "
    "The air smells like rain and jasmine, and I remember thinking — this is real life."
)

# Preprocess: resample to mono 24kHz, trim to 12s (F5-TTS clips at 12s anyway)
# sf.read always_2d=True returns shape (frames, channels)
audio, sr = sf.read(RAW_REF, dtype="float32", always_2d=True)
audio = audio.mean(axis=1) if audio.shape[1] > 1 else audio[:, 0]  # -> (frames,)
if sr != 24000:
    import scipy.signal as sig
    audio = sig.resample(audio, int(len(audio) * 24000 / sr))
    sr = 24000
audio = audio[: 12 * sr]
sf.write(PREP_REF, audio, sr)
print(f"Prepared ref: {len(audio)/sr:.1f}s mono {sr}Hz -> {PREP_REF}")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

# Patch torchaudio.load to use soundfile (bypasses torchcodec DLL)
import torchaudio as _ta
def _sf_load(path, *args, **kwargs):
    a, s = sf.read(str(path), dtype="float32", always_2d=True)
    return torch.from_numpy(a.T), s
_ta.load = _sf_load
print("torchaudio.load patched -> soundfile backend")

from f5_tts.api import F5TTS
print("\nLoading F5-TTS model...")
tts = F5TTS(device=device)
print("Model loaded.")

print("Generating cloned voice...")
wav, sr_out, _ = tts.infer(
    ref_file=PREP_REF,
    ref_text=REF_TEXT,
    gen_text=TEST_TEXT,
    file_wave=str(OUT_DIR / "f5tts_output.wav"),
    show_info=print,
)

print(f"\nSUCCESS: {OUT_DIR / 'f5tts_output.wav'}")
print(f"Duration: {len(wav)/sr_out:.1f}s")
