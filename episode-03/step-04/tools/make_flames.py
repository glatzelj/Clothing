"""Render a seamlessly looping flame strip as a transparent PNG sequence.

The noise field is tileable in Y and scrolls exactly one tile per loop, so
frame N+1 == frame 0. Output: flames/png/flame_0000.png ... (RGBA).

Usage: python3 make_flames.py [out_dir] [--width 1200 --height 600 --frames 50 --seed 7]
"""
import argparse
import os

import numpy as np
from PIL import Image


def tileable_noise(h, w, sx, sy, rng):
    """Band-limited random field that tiles in both axes (FFT filtered).

    sx/sy are rough feature sizes in px; sy > sx gives tall flame tongues.
    """
    white = rng.standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    spectrum = np.exp(-((fx * sx) ** 2 + (fy * sy) ** 2))  # gaussian low-pass
    field = np.real(np.fft.ifft2(np.fft.fft2(white) * spectrum))
    return (field - field.mean()) / field.std()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out_dir", nargs="?", default="flames/png")
    p.add_argument("--width", type=int, default=1200)
    p.add_argument("--height", type=int, default=600)
    p.add_argument("--frames", type=int, default=50)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    W, H, N = a.width, a.height, a.frames
    rng = np.random.default_rng(a.seed)
    # Two octaves of noise, tile height == H so one full scroll == one loop.
    n1 = tileable_noise(H, W, 70, 160, rng)
    n2 = tileable_noise(H, W, 25, 55, rng)

    y = np.linspace(0, 1, H)[:, None]          # 0 top .. 1 bottom
    x = np.linspace(-1, 1, W)[None, :]
    # Fade the strip out at the left/right edges so it sits under an item.
    side = np.clip(1 - np.abs(x) ** 3, 0, 1)
    base = y ** 1.6                              # hotter toward the bottom
    edge = np.clip((1 - np.abs(x)) * 5, 0, 1)

    # Colour ramp: transparent -> deep red -> orange -> yellow -> near white
    stops = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    cols = np.array([
        [120, 10, 0], [200, 40, 0], [255, 110, 0], [255, 200, 40], [255, 250, 210],
    ], dtype=float)

    for i in range(N):
        t = i / N
        s1 = int(round(t * H)) % H               # scroll speed 1x
        s2 = int(round(2 * t * H)) % H           # detail scrolls 2x (still loops)
        noise = 0.8 * np.roll(n1, -s1, axis=0) + 0.2 * np.roll(n2, -s2, axis=0)
        heat = base * side * 1.5 + noise * 0.42 * (1.1 - 0.5 * y) - 0.42
        # no stray embers at the top edge, soft fade at the left/right edges
        heat = np.clip(heat * np.clip(y * 3.5, 0, 1) * edge, 0, 1)

        rgb = np.stack([np.interp(heat, stops, cols[:, c]) for c in range(3)], -1)
        alpha = np.clip(heat * 3.2, 0, 1) ** 1.2
        img = np.dstack([rgb, alpha * 255]).astype(np.uint8)
        Image.fromarray(img, "RGBA").save(os.path.join(a.out_dir, f"flame_{i:04d}.png"))


if __name__ == "__main__":
    main()
