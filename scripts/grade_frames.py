"""grade_frames.py - the channel's color grade ("Soil & Signal dawn").

Applies ONE consistent grade to every frame so shots cut together as one piece
(z-turbo picks its own exposure/saturation per image — this unifies them in post,
exactly like grading rushes with a house LUT).

The look: soft warm dawn — desaturated a touch, lifted blacks (calm, filmic),
split-tone (amber highlights / slightly cool shadows), gentle warm shift.

Usage:
  ml-env\\Scripts\\python.exe scripts\\grade_frames.py <slug> [--only 1,3,10] [--tag graded]
      reads  output/<slug>/frames/scene_NN.png
      writes output/<slug>/frames_<tag>/scene_NN.png   (default tag: graded)
  ml-env\\Scripts\\python.exe scripts\\grade_frames.py <slug> --compare
      also writes compare_grade.png (before/after pairs, for the human gate)

Tune the LOOK constants below; keep them subtle — a grade should be felt, not seen.
"""
import argparse
import pathlib
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

# ---- the look (Soil & Signal dawn, v2 — Nuay 2026-07-11: "เบากว่านี้ สีเข้มขึ้น อุ่นขึ้น
# อย่าให้ครีม/จืดเหมือนมีฟิลเตอร์") ----
SATURATION   = 0.94   # barely calmed — keep the colors alive, just kill the worst neon spikes
BLACK_LIFT   = 0.03   # gentle filmic toe, not washed out
WHITE_POINT  = 0.995  # whites stay white; the character should still glow
WARM         = np.array([1.03, 1.00, 0.96])  # global warm shift (the "dawn temperature")
HI_TONE      = np.array([1.05, 1.00, 0.92])  # highlights toward warm amber
SH_TONE      = np.array([0.985, 1.00, 1.02]) # shadows barely cool — cohesion, not a filter
GAMMA        = 0.985  # slight airiness
GRAIN        = 0.025  # fine paper grain — LOCKED (Nuay 2026-07-11): kills the "clean vector
                      # clip-art" flatness, adds craft feel. Set --grain 0 to disable.


def grade(img: Image.Image, s: float = 1.0, grain: float = GRAIN) -> Image.Image:
    """s = strength: 0 = untouched, 1 = the house look, >1 = pushed harder."""
    sat = 1.0 + (SATURATION - 1.0) * s
    lift = BLACK_LIFT * s
    white = 1.0 + (WHITE_POINT - 1.0) * s
    warm = 1.0 + (WARM - 1.0) * s
    hi = 1.0 + (HI_TONE - 1.0) * s
    sh = 1.0 + (SH_TONE - 1.0) * s
    gamma = 1.0 + (GAMMA - 1.0) * s

    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(sat)
    a = np.asarray(img).astype(np.float32) / 255.0
    a = a * (white - lift) + lift                            # compress to lifted range
    luma = a.mean(axis=2, keepdims=True)                     # 0=shadow 1=highlight
    a = a * warm * (sh + (hi - sh) * luma)                   # warm shift + split-tone
    if grain:
        rng = np.random.default_rng(42)                      # fixed seed = repeatable frames
        n = rng.standard_normal(a.shape[:2])[..., None].astype(np.float32)
        a = a + n * grain * (0.35 + 0.65 * luma)             # grain mostly in mids/highs
    a = np.clip(a, 0.0, 1.0) ** gamma
    return Image.fromarray((a * 255).round().astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", help="comma list of scene numbers (default: all)")
    ap.add_argument("--tag", default="graded", help="output folder suffix (frames_<tag>)")
    ap.add_argument("--compare", action="store_true", help="write compare_grade_<tag>.png before/after sheet")
    ap.add_argument("--strength", type=float, default=1.0, help="grade intensity (1.0 = house look)")
    ap.add_argument("--src", default="frames", help="source folder name under output/<slug>/")
    ap.add_argument("--grain", type=float, default=GRAIN, help="paper-grain amount (0.02-0.03 subtle)")
    args = ap.parse_args()

    src = pathlib.Path("output") / args.slug / args.src
    dst = pathlib.Path("output") / args.slug / f"frames_{args.tag}"
    dst.mkdir(exist_ok=True)
    pngs = sorted((p for p in src.glob("scene_*.png") if re.fullmatch(r"scene_\d+", p.stem)),
                  key=lambda p: int(p.stem.split("_")[1]))
    if args.only:
        keep = {int(n) for n in args.only.split(",")}
        pngs = [p for p in pngs if int(p.stem.split("_")[1]) in keep]
    if not pngs:
        sys.exit(f"no frames matched in {src}")

    pairs = []
    for p in pngs:
        with Image.open(p) as im:
            out = grade(im, args.strength, args.grain)
            out.save(dst / p.name)
            if args.compare:
                pairs.append((p.name, im.copy(), out))
    print(f"OK -> {dst}  ({len(pngs)} frames graded, strength {args.strength})")

    if args.compare:
        tw = 300
        th = int(tw * pairs[0][1].height / pairs[0][1].width)
        sheet = Image.new("RGB", (tw * len(pairs), th * 2 + 24), "white")
        d = ImageDraw.Draw(sheet)
        for i, (name, before, after) in enumerate(pairs):
            sheet.paste(before.resize((tw, th)), (i * tw, 24))
            sheet.paste(after.resize((tw, th)), (i * tw, 24 + th))
            d.text((i * tw + 6, 5), name.replace("scene_", "").replace(".png", ""), fill="black")
        d.text((6, 8), "", fill="black")
        out = dst.parent / f"compare_grade_{args.tag}.png"
        sheet.save(out)
        print(f"OK -> {out}  (top = original, bottom = graded)")


if __name__ == "__main__":
    main()
