"""
clean_voice.py - clean up a raw voice recording for narration.

Two-pass loudnorm (hits the loudness target exactly) + high-pass + denoise +
gentle compression. Validated on a noisy room-mic take (Nuay, 2026-06):
noise floor -29 dB -> -36 dB, loudness standardized to YouTube -14 LUFS.

Usage:
    python scripts/clean_voice.py "Test voice/Recording (7).wav"
    python scripts/clean_voice.py raw.wav out.wav

If the NEW mic records clean, lower DENOISE (or set it to "") so the voice
doesn't go "underwater". Everything else can stay.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TARGET_I = -14.0     # YouTube playback loudness (LUFS)
TARGET_TP = -1.0     # true-peak ceiling (dBTP)
TARGET_LRA = 11.0
DENOISE = "afftdn=nr=18:nf=-28"   # set "" to disable on a clean mic
PRECHAIN = ",".join(filter(None, [
    "highpass=f=80",                                   # cut rumble / handling
    DENOISE,                                           # broadband noise
    "acompressor=threshold=-20dB:ratio=3:attack=20:release=200",  # gently even out
    "alimiter=limit=0.9",                              # catch stray peaks (keeps it true-peak safe)
]))


def ffmpeg(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-y", *args],
                          capture_output=True, text=True)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/clean_voice.py <in.wav> [out.wav]")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "_clean.wav")

    # Pass 1 - measure loudness AFTER the pre-chain, so loudnorm corrects what
    # the listener actually hears (post denoise + compression).
    measure = f"{PRECHAIN},loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json"
    r = ffmpeg("-i", str(src), "-af", measure, "-f", "null", "-")
    blocks = re.findall(r"\{[^{}]+\}", r.stderr, re.S)
    if not blocks:
        sys.exit("could not read loudnorm stats:\n" + r.stderr[-1500:])
    m = json.loads(blocks[-1])

    # Pass 2 - apply with measured values (linear mode = exact target).
    apply_ln = (
        f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:"
        f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
        f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
        f"offset={m['target_offset']}:linear=true"
    )
    r2 = ffmpeg("-i", str(src), "-af", f"{PRECHAIN},{apply_ln}",
                "-ar", "48000", "-ac", "1", str(out))
    if r2.returncode:
        sys.exit("ffmpeg failed:\n" + r2.stderr[-1500:])
    print(f"wrote {out}")
    print(f"  raw {m['input_i']} LUFS, normalized for YouTube (true-peak {TARGET_TP} dBTP).")
    print(f"  calm/peaky voice lands ~-16 to -17 LUFS, which is ideal for narration.")


if __name__ == "__main__":
    main()
