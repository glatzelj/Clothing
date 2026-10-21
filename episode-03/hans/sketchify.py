"""Turn a flat vector frame into a hand-drawn still: wobbly ink outlines,
slightly mis-registered marker fills, cross-hatching in the shadows and
paper grain.

Usage: python3 sketchify.py flat.png out.png [--seed 3]
Source: hans-mockup.html?static&paper&t=2.0 rendered at 2x (3840x2160).
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter


def low_noise(h, w, cell, rng):
    """Smooth random field in [-1, 1], features roughly `cell` px wide."""
    small = rng.uniform(-1, 1, (max(2, h // cell), max(2, w // cell))).astype(np.float32)
    im = Image.fromarray(small, mode="F").resize((w, h), Image.BICUBIC)
    return np.asarray(im)


def warp(arr, dx, dy):
    """Sample arr at (x + dx, y + dy), nearest neighbour."""
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    sx = np.clip(np.rint(xx + dx), 0, w - 1).astype(np.int32)
    sy = np.clip(np.rint(yy + dy), 0, h - 1).astype(np.int32)
    return arr[sy, sx]


def edges(img, blur):
    soft = np.asarray(Image.fromarray(img).filter(ImageFilter.GaussianBlur(blur)), dtype=np.float32) / 255
    gy, gx = np.gradient(soft, axis=(0, 1))
    return np.sqrt(gx ** 2 + gy ** 2).max(axis=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    img = np.asarray(Image.open(a.src).convert("RGB"))
    h, w = img.shape[:2]
    paper = np.array([243, 239, 230], np.float32) / 255

    # Marker fills: pushed a few px off the lines, streaky, a touch transparent.
    fdx, fdy = low_noise(h, w, 260, rng) * 9, low_noise(h, w, 260, rng) * 9
    fill = warp(img, fdx, fdy).astype(np.float32) / 255
    # Streaks generated oversize then rotated and cropped, so no empty corners.
    S = 2 * max(h, w)
    streak = Image.fromarray(rng.uniform(0, 1, (S // 60, S // 6)).astype(np.float32), "F")
    streak = streak.resize((S, S), Image.BICUBIC).rotate(-30, resample=Image.BILINEAR)
    top, left = (S - h) // 2, (S - w) // 2
    streak = np.asarray(streak)[top:top + h, left:left + w]
    inked = (np.abs(fill - paper).sum(axis=2) > 0.06).astype(np.float32)  # only on coloured areas
    fill = fill * (1 - 0.08 * inked[..., None] * (1 - streak[..., None]))
    fill = fill * 0.88 + paper * 0.12

    # Cross-hatching where the fill is dark.
    lum = fill @ np.array([0.299, 0.587, 0.114], np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    hatch1 = (((xx + yy) % 22) < 3).astype(np.float32)
    hatch2 = (((xx - yy) % 22) < 3).astype(np.float32)
    shade = np.clip((0.42 - lum) / 0.25, 0, 1)
    hatch = np.maximum(hatch1 * (shade > 0.05), hatch2 * (shade > 0.55))
    hatch = warp(hatch, low_noise(h, w, 120, rng) * 3, low_noise(h, w, 120, rng) * 3)
    fill = fill * (1 - 0.28 * hatch[..., None])

    # Ink: two wobbly passes of the outline, the second lighter and offset.
    e = edges(img, 2.2)
    line = np.clip((e - 0.012) / 0.02, 0, 1)
    ink = np.zeros((h, w), np.float32)
    for amp, cell, weight in [(4, 180, 1.0), (7, 140, 0.45)]:
        dx, dy = low_noise(h, w, cell, rng) * amp, low_noise(h, w, cell, rng) * amp
        pressure = 0.65 + 0.35 * (low_noise(h, w, 90, rng) * 0.5 + 0.5)
        ink = np.maximum(ink, warp(line, dx, dy) * pressure * weight)
    ink = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)),
                     np.float32) / 255

    # Paper grain over everything.
    grain = np.clip(rng.normal(128, 40, (h, w)), 0, 255).astype(np.uint8)
    grain = (np.asarray(Image.fromarray(grain).filter(ImageFilter.GaussianBlur(0.7)), np.float32) - 128) / 40
    out = fill * (1 + 0.035 * grain[..., None])
    ink_col = np.array([28, 26, 30], np.float32) / 255
    out = out * (1 - ink[..., None]) + ink_col * ink[..., None]

    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(a.out)


if __name__ == "__main__":
    main()
