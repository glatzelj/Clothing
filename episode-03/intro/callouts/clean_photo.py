"""Remove the green annotation lines from the supplied freeze-frame mockup,
crop in tight on the car and upscale. Mockup use only (source is ~1200px).

Usage: python3 clean_photo.py src.jpg out.png   (needs opencv-python-headless)"""
import sys

import cv2
import numpy as np

src, out_path = sys.argv[1], sys.argv[2]
im = cv2.imread(src)
x0, y0, w, h = 297, 275, 520, 290            # tight crop around the car
c = im[y0:y0 + h, x0:x0 + w].copy()

# Green ink (hue band) including its JPEG-softened edges.
b, g, r = [c[..., i].astype(np.int16) for i in range(3)]
green = ((g - np.maximum(r, b)) > 6).astype(np.uint8) * 255
# the lines also carry a dark halo, so grow the mask well past the green core
mask = cv2.dilate(green, np.ones((5, 5), np.uint8), iterations=4)

clean = cv2.inpaint(c, mask, 9, cv2.INPAINT_TELEA).astype(np.float32)
# Inpainting leaves smooth patches; borrow fine texture (grain, fence mesh)
# from a horizontally offset copy so they blend with the rest of the frame.
cf = c.astype(np.float32)
detail = cf - cv2.GaussianBlur(cf, (0, 0), 2.5)
donor = np.roll(detail, 45, axis=1)
donor_ok = np.roll(mask, 45, axis=1) == 0
soft = cv2.GaussianBlur((mask > 0).astype(np.float32), (0, 0), 3)[..., None]
clean = np.clip(clean + donor * soft * donor_ok[..., None], 0, 255).astype(np.uint8)
# Clone-stamp the one patch that still reads as a smudge (old circle over the
# crowd, right of the airbox) from the crowd a little further right.
cx, cy, rad, dx = 291, 85, 40, 85
yy, xx = np.mgrid[0:h, 0:w]
feather = np.clip((rad - np.hypot(xx - cx, yy - cy)) / 12, 0, 1)[..., None]
src_patch = np.roll(c, -dx, axis=1).astype(np.float32)
clean = (clean * (1 - feather) + src_patch * feather).astype(np.uint8)

clean = cv2.resize(clean, (1100, round(1100 * h / w)), interpolation=cv2.INTER_LANCZOS4)
blur = cv2.GaussianBlur(clean, (0, 0), 2)
clean = cv2.addWeighted(clean, 1.5, blur, -0.5, 0)  # light unsharp mask
cv2.imwrite(out_path, clean)
