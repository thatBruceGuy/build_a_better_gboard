#!/usr/bin/env python3
"""
Measure the on-screen geometry of a keyboard from a screenshot.

This is the tool the compact layout's numbers came from, and it is how changes
to that layout get checked: build, screenshot, re-measure, compare against the
targets in README.md. It reports pixel numbers rather than impressions.

Usage:
    python3 tools/measure_keyboard.py shot.png [--density 3.5]

The screenshot should be cropped so the bottom of the image is the bottom of
the screen. Cropping into the keyboard hides the bottom padding and makes the
total meaningless.

Method
------
For every scanline, classify each pixel as keycap or panel background by
comparing it against a reference column taken from the far left edge of the
screen, which is always panel background (every layout has side padding). Then
read the run boundaries off the resulting coverage profile.

Sampling the reference per scanline rather than once is what makes this work on
translucent themes, where the background is a vertical gradient and a single
global background colour would be wrong everywhere but one row.

Keys whose fill is very close to the panel colour need --threshold lowered;
the script warns when it finds suspiciously few rows.
"""

import argparse
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("needs pillow and numpy: pip install pillow numpy")


def coverage_profile(img, threshold, ref_width=9):
    """Fraction of each scanline that differs from that line's background."""
    h, w, _ = img.shape
    cov = np.zeros(h)
    for y in range(h):
        ref = np.median(img[y, 0:ref_width], axis=0)
        cov[y] = (np.abs(img[y] - ref).sum(axis=1) > threshold).mean()
    return cov


def runs(mask):
    """[(start, end, value)] for each constant run in a boolean array."""
    out, start = [], 0
    for i in range(1, len(mask)):
        if mask[i] != mask[i - 1]:
            out.append((start, i - 1, bool(mask[i - 1])))
            start = i
    out.append((start, len(mask) - 1, bool(mask[-1])))
    return out


def key_spans(img, y0, y1, threshold, min_width=8):
    """Horizontal extents of the keys in a row band."""
    band = img[y0:y1 + 1]
    bg = np.median(band[:, 0:6].reshape(-1, 3), axis=0)
    prof = (np.abs(band - bg).sum(axis=2) > threshold).mean(axis=0)
    spans, start = [], None
    for x, on in enumerate(prof > 0.5):
        if on and start is None:
            start = x
        elif not on and start is not None:
            if x - start > min_width:
                spans.append((start, x - 1))
            start = None
    if start is not None and len(prof) - start > min_width:
        spans.append((start, len(prof) - 1))
    return spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--density", type=float, default=3.5,
                    help="display density, for the dp column (default 3.5)")
    ap.add_argument("--threshold", type=int, default=18,
                    help="colour distance for keycap vs background (default 18)")
    ap.add_argument("--min-rows", type=int, default=12,
                    help="ignore runs shorter than this many pixels")
    ap.add_argument("--first-key-row", type=int, default=1, metavar="N",
                    help="which detected band is the first real key row "
                         "(default 1). A toolbar or suggestion strip of icons "
                         "looks like a key row to the detector; the 'keys' "
                         "column tells them apart, since letter rows have 9-10 "
                         "and an icon strip usually has fewer. Set this to "
                         "exclude leading strips from the key rows and count "
                         "them as chrome instead.")
    args = ap.parse_args()

    img = np.asarray(Image.open(args.image).convert("RGB")).astype(int)
    h, w, _ = img.shape
    d = args.density

    cov = coverage_profile(img, args.threshold)
    bands = [(s, e) for s, e, on in runs(cov > 0.30)
             if on and e - s + 1 >= args.min_rows]

    print(f"{args.image}: {w} x {h} px, density {d}x ({w / d:.0f}dp wide)\n")

    if not bands:
        sys.exit("no key rows found -- try a lower --threshold")
    if len(bands) < 3:
        print(f"warning: only {len(bands)} row(s) found. If the keycaps are "
              f"low contrast against the panel, lower --threshold.\n")

    print(f"{'band':>4}  {'top':>5} {'bot':>5} {'keycap':>7} {'pitch':>6}"
          f"  {'keycap':>8} {'pitch':>7}  keys")
    print(f"{'':>4}  {'':>5} {'':>5} {'(px)':>7} {'(px)':>6}"
          f"  {'(dp)':>8} {'(dp)':>7}")

    all_spans = [key_spans(img, s, e, args.threshold) for s, e in bands]
    first = max(1, min(args.first_key_row, len(bands))) - 1

    prev_top = None
    for i, (s, e) in enumerate(bands):
        keycap = e - s + 1
        # Pitch is only meaningful between consecutive key rows.
        pitch = s - prev_top if (prev_top is not None and i > first) else None
        pitch_px = f"{pitch:>6}" if pitch else f"{'-':>6}"
        pitch_dp = f"{pitch / d:>7.1f}" if pitch else f"{'-':>7}"
        mark = " " if i >= first else "*"
        print(f"{i + 1:>3}{mark}  {s:>5} {e:>5} {keycap:>7} {pitch_px}"
              f"  {keycap / d:>8.1f} {pitch_dp}  {len(all_spans[i])}")
        prev_top = s

    if first > 0:
        print("\n  * counted as chrome, not as a key row (--first-key-row)")

    first_row_top = bands[first][0]
    bottom_pad = h - 1 - bands[-1][1]

    # Panel top: the FIRST background-colour change down the far-left column.
    # That is the app/keyboard boundary. Taking the last change instead finds
    # dividers inside the keyboard's own chrome, which understates the total.
    left = img[:, 5]
    panel_top = 0
    for y in range(1, first_row_top):
        if np.abs(left[y] - left[y - 1]).sum() > 12:
            panel_top = y
            break

    print()
    print(f"panel top            y={panel_top}")
    print(f"chrome above keys    {first_row_top - panel_top:>5} px"
          f"  {(first_row_top - panel_top) / d:>7.1f} dp")
    print(f"bottom padding       {bottom_pad:>5} px  {bottom_pad / d:>7.1f} dp")
    print(f"total panel height   {h - panel_top:>5} px"
          f"  {(h - panel_top) / d:>7.1f} dp")

    # Side padding from the row with the most keys: a full letter row runs edge
    # to edge, while the bottom row and any icon strip do not.
    widest = max(all_spans[first:], key=len, default=[])
    if widest:
        print(f"side padding         {widest[0][0]:>5} px left, "
              f"{w - 1 - widest[-1][1]} px right")

    if bottom_pad == 0:
        print("\nwarning: the last key row touches the bottom of the image, so "
              "the screenshot is\ncropped. Bottom padding and the total are "
              "wrong. Re-crop to the screen bottom.")


if __name__ == "__main__":
    main()
