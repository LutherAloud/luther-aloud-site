#!/usr/bin/env python3
"""Convert an episode cover PNG to a color-faithful 1280x720 JPEG.

Usage:
    scripts/convert-cover.py SRC.png DST.jpg

Encodes sRGB at JPEG quality 92 with 4:4:4 chroma (no subsampling) and no
embedded ICC profile. Then samples four points inside the oxblood field and
fails if any is more than one step per channel off #3E1014 — the published
oxblood used by the site, the pipeline's cover template and the playlist
covers.

Pillow is the reference encoder. If Pillow is not importable (a broken
system install, or an offline container that cannot reach PyPI), the script
shells out to ImageMagick's `convert` with the equivalent flags
(-colorspace sRGB -sampling-factor 4:4:4 -quality 92 -strip). Same color
math for the same source PNG.
"""
from __future__ import annotations

import shutil
import struct
import subprocess
import sys
from pathlib import Path

TARGET = (0x3E, 0x10, 0x14)  # oxblood
TOL = 1                       # per-channel tolerance after JPEG encoding
SAMPLE_POINTS = [(15, 15), (640, 80), (100, 400), (1200, 700)]


def convert_with_pillow(src: Path, dst: Path) -> bool:
    try:
        from PIL import Image  # noqa: PLC0415
    except Exception:
        return False
    im = Image.open(src).convert("RGB")
    if im.size != (1280, 720):
        im = im.resize((1280, 720), Image.LANCZOS)
    im.save(
        dst,
        format="JPEG",
        quality=92,
        subsampling=0,
        optimize=True,
        progressive=False,
        icc_profile=None,
    )
    return True


def convert_with_imagemagick(src: Path, dst: Path) -> None:
    if not shutil.which("convert"):
        raise SystemExit(
            "Neither Pillow nor ImageMagick is available. Install one:\n"
            "  pip install Pillow\n"
            "  apt-get install imagemagick"
        )
    subprocess.run(
        [
            "convert",
            str(src),
            "-filter", "Lanczos",
            "-resize", "1280x720",
            "-colorspace", "sRGB",
            "-sampling-factor", "4:4:4",
            "-quality", "92",
            "-interlace", "none",
            "-strip",
            str(dst),
        ],
        check=True,
    )


def sample_bg(path: Path) -> list[tuple[int, int, int]]:
    """Return RGB tuples sampled at SAMPLE_POINTS. Uses Pillow if importable, else ImageMagick."""
    try:
        from PIL import Image  # noqa: PLC0415
        im = Image.open(path).convert("RGB")
        return [im.getpixel(xy) for xy in SAMPLE_POINTS]
    except Exception:
        out = []
        for x, y in SAMPLE_POINTS:
            r = subprocess.run(
                ["convert", f"{path}[1x1+{x}+{y}]", "-format", "%[hex:p{0,0}]", "info:"],
                check=True, capture_output=True, text=True,
            )
            hx = r.stdout.strip()
            out.append((int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)))
        return out


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    if not src.is_file():
        print(f"source not found: {src}", file=sys.stderr)
        return 1

    if not convert_with_pillow(src, dst):
        print("Pillow unavailable; using ImageMagick fallback.", file=sys.stderr)
        convert_with_imagemagick(src, dst)

    samples = sample_bg(dst)
    failures = []
    for (x, y), rgb in zip(SAMPLE_POINTS, samples):
        if any(abs(c - t) > TOL for c, t in zip(rgb, TARGET)):
            failures.append((x, y, rgb))
        print(f"  ({x:>4},{y:>3}) = #{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}")

    if failures:
        print(
            f"\nFAIL: {len(failures)} of {len(SAMPLE_POINTS)} sample points "
            f"are more than {TOL} step(s) per channel from #3E1014 oxblood.",
            file=sys.stderr,
        )
        return 1

    print(f"\nOK: all {len(SAMPLE_POINTS)} samples within {TOL} step of #3E1014.")
    print(f"wrote {dst}  ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
