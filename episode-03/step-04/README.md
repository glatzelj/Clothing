# Ep.3 – Step 4: kit flat-lay, flames, FIA "Approved" stamp

| Folder | What | Status |
|---|---|---|
| `flames/png/` | 50-frame seamless flame loop (1200×600, 25fps, transparent PNG) | Ready |
| `flames/*.webm` | Same loop, VP9 with alpha | Ready |
| `stamp/` | "FIA Approved / Standard 8856-2018" stamp, worn + clean, SVG + 2000px PNG (text only, no FIA logo) | Ready |
| `kit/` | Illustrated kit items | Placeholder only – final kit must be photoreal |
| `preview/` | Timing animatic (HTML + MP4) using the placeholder kit | Reference |

ProRes 4444 version of the flames (git-ignored, regenerate):

    ffmpeg -framerate 25 -i flames/png/flame_%04d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le flames/flame-loop_1200x600_25fps_prores4444.mov

Regenerate assets: `python3 tools/make_flames.py flames/png`, `python3 tools/make_kit.py kit`,
`node tools/render_svg.mjs 2000 stamp/*.svg`, `node tools/render_preview.mjs`.
