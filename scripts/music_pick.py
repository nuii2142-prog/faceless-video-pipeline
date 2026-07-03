"""Rank SFX/ tracks by how well they fit CALM, contemplative narration.

Honesty note: this does NOT "listen" the way a human does — it measures objective
audio features (tempo, energy, brightness) and scores them against a calm target.
Treat the top 2-3 as a shortlist to ear-check, not a final verdict. librosa's tempo
estimate can halve/double on ambient tracks, so the printed BPM is a hint.

Target for this channel: slow, warm, low-energy, unobtrusive under a spoken voice.

Usage:
  ml-env\\Scripts\\python.exe scripts\\music_pick.py            # rank SFX/
  ml-env\\Scripts\\python.exe scripts\\music_pick.py --dir SFX --secs 90
"""
import argparse, pathlib, warnings
warnings.filterwarnings("ignore")
import librosa
import numpy as np

# Calm target: ~75 BPM, low RMS, mellow (low spectral centroid ~1800 Hz).
BPM_IDEAL, BPM_TOL = 78.0, 34.0
CENTROID_IDEAL = 1800.0   # Hz; lower = warmer/darker, higher = brighter/harsher


def analyze(path, secs):
    y, sr = librosa.load(path, mono=True, duration=secs)
    tempo = float(np.atleast_1d(librosa.beat.beat_track(y=y, sr=sr)[0])[0])
    rms = float(np.mean(librosa.feature.rms(y=y)))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    return tempo, rms, centroid


def score(tempo, rms, centroid, rms_max):
    # each term in [0,1], higher = calmer/warmer/better fit
    tempo_fit = max(0.0, 1 - abs(tempo - BPM_IDEAL) / BPM_TOL)      # near ideal BPM
    energy_fit = 1 - min(1.0, rms / rms_max)                        # quieter is calmer
    warmth_fit = max(0.0, 1 - abs(centroid - CENTROID_IDEAL) / 2200)  # mellow, not harsh
    return 0.35 * tempo_fit + 0.30 * energy_fit + 0.35 * warmth_fit


def main(d, secs):
    tracks = sorted(pathlib.Path(d).glob("*.mp3"))
    if not tracks:
        raise SystemExit(f"no .mp3 in {d}")
    rows = []
    for t in tracks:
        tempo, rms, centroid = analyze(str(t), secs)
        rows.append([t.name, tempo, rms, centroid])
    rms_max = max(r[2] for r in rows) or 1.0
    for r in rows:
        r.append(score(r[1], r[2], r[3], rms_max))
    rows.sort(key=lambda r: -r[-1])

    print(f"{'#':>2}  {'fit':>4}  {'BPM':>5}  {'energy':>6}  {'warmth':>6}  track")
    for i, (name, tempo, rms, centroid, sc) in enumerate(rows, 1):
        warm = "warm" if centroid < 2000 else ("mid" if centroid < 3000 else "bright")
        print(f"{i:>2}  {sc:>4.2f}  {tempo:>5.0f}  {rms:>6.3f}  {warm:>6}  {name}")
    print("\ntop pick(s) are a shortlist to ear-check, not a verdict — BPM is a hint.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="SFX")
    ap.add_argument("--secs", type=int, default=90, help="seconds to sample per track")
    args = ap.parse_args()
    main(args.dir, args.secs)
