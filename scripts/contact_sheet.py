"""Tile a clip's frames into one contact-sheet PNG for a fast human pass.

The point: catch off-meaning or broken images BEFORE assembling the video.
Each tile is labeled with its scene number, so a bad frame maps straight to:
  python scripts/batch_zturbo.py <slug> --only <N> --seed 7   (delete the bad png first)

Usage:
  ml-env\\Scripts\\python.exe scripts\\contact_sheet.py <slug> [--cols 10] [--tag test]
Writes:
  output/<slug>/contact_sheet.png
"""
import argparse, pathlib, re, sys
from PIL import Image, ImageDraw

THUMB_W = 320


def main(slug: str, cols: int, tag: str | None):
    d = pathlib.Path("output") / slug / (f"frames_{tag}" if tag else "frames")
    pngs = sorted((p for p in d.glob("scene_*.png") if re.fullmatch(r"scene_\d+", p.stem)),
                  key=lambda p: int(p.stem.split("_")[1]))
    if not pngs:
        sys.exit(f"no scene_NN.png frames in {d}")

    with Image.open(pngs[0]) as im0:
        th = int(THUMB_W * im0.height / im0.width)
    rows = (len(pngs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * THUMB_W, rows * th), "white")
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(pngs):
        x, y = (i % cols) * THUMB_W, (i // cols) * th
        with Image.open(p) as im:
            sheet.paste(im.resize((THUMB_W, th)), (x, y))
        label = p.stem.split("_")[1]
        draw.rectangle([x, y, x + 14 + 9 * len(label), y + 20], fill="black")
        draw.text((x + 6, y + 4), label, fill="white")

    out = d.parent / "contact_sheet.png"
    sheet.save(out)
    print(f"OK -> {out}  ({len(pngs)} frames, {cols}x{rows} grid)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--cols", type=int, default=10)
    ap.add_argument("--tag", help="read frames_<tag>/ instead of frames/")
    args = ap.parse_args()
    main(args.slug, args.cols, args.tag)
