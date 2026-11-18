#!/usr/bin/env python3
"""news-image-20261118 entry (v2): copy the pre-rendered image to the output dir.

The image (entry.png) is a 1024x1024 newspaper front page summing up the
world news of Wednesday 18 November 2026: 44 stories, verified against
reporting from that day, with a masthead, big-numbers strip, 3 large
illustrated stories, 10 illustrated cards, a world map with numbered pins,
and a numbered list of the remaining stories.

The program writes the image to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png when set), byte for byte, so both runs
produce identical output. Standard library only, no network.

The image itself is rendered by draw.py (Pillow, build-time only), kept in
this repo for transparency and reproducibility.
"""

import os
import shutil
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    # Never remove the output directory itself: create it, then empty only
    # its contents so a stale entry.png cannot survive a re-run.
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Integrity check: the copy must be the whole image, byte for byte.
    if os.path.getsize(dst) != os.path.getsize(src):
        raise SystemExit("entry.png copy incomplete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
