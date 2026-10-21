"""Turn a flat vector frame into a hand-drawn still: wobbly ink outlines,
slightly mis-registered marker fills, cross-hatching in the shadows and
paper grain.

Usage: python3 sketchify.py flat.png out.png [--seed 3] [--bw]
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


# Mockup colour -> grey tone for the black-and-white version. Plain luminance
# puts the suit, belts and seat on near-identical greys, so each part gets a
# tone of its own; anything not listed falls back to luminance.
BW_TONES = [
    ((243, 239, 230), 244),  # paper
    ((244, 242, 236), 250),  # helmet
    ((236, 235, 230), 235),  # balaclava / neck
    ((31, 79, 160), 205),    # suit
    ((23, 61, 126), 170),    # arm
    ((168, 18, 27), 120),    # belt webbing
    ((138, 13, 21), 100),
    ((44, 47, 54), 80),      # seat
    ((51, 54, 61), 85),      # HANS
    ((58, 61, 68), 90),      # wheel
    ((29, 31, 36), 35),      # visor, boots, outlines
    ((35, 38, 44), 40),
    ((14, 15, 18), 25),
    ((239, 158, 150), 196),  # ghost head (red at 50% over paper)
    ((224, 38, 47), 140),    # "without HANS" tag
    ((239, 226, 182), 236),  # tape caption
    ((184, 188, 196), 200),  # buckle
]


def to_bw(img):
    flat = img.reshape(-1, 3).astype(np.int16)
    grey = np.asarray(Image.fromarray(img).convert("L")).reshape(-1).astype(np.float32)
    best = np.full(flat.shape[0], 40.0, np.float32)  # max colour distance to snap
    for rgb, tone in BW_TONES:
        d = np.abs(flat - np.array(rgb, np.int16)).sum(axis=1).astype(np.float32)
        hit = d < best
        grey[hit] = tone
        best[hit] = d[hit]
    grey = grey.reshape(img.shape[:2]).astype(np.uint8)
    return np.repeat(grey[..., None], 3, axis=2)


def edges(img, blur):
    soft = np.asarray(Image.fromarray(img).filter(ImageFilter.GaussianBlur(blur)), dtype=np.float32) / 255
    gy, gx = np.gradient(soft, axis=(0, 1))
    return np.sqrt(gx ** 2 + gy ** 2).max(axis=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--bw", action="store_true", help="black and white (greyscale fills, neutral paper)")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    img = np.asarray(Image.open(a.src).convert("RGB"))
    h, w = img.shape[:2]
    paper = np.array([243, 239, 230], np.float32) / 255
    if a.bw:
        img = to_bw(img)
        paper = np.array([244, 244, 242], np.float32) / 255

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
    ink_col = np.array([18, 18, 18] if a.bw else [28, 26, 30], np.float32) / 255
    out = out * (1 - ink[..., None]) + ink_col * ink[..., None]

    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(a.out)


if __name__ == "__main__":
    main()
