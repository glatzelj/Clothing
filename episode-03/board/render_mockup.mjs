// Export board-mockup.html to an MP4 (1920x1080, 25fps).
// Usage: node render_mockup.mjs [out.mp4]   (needs playwright + ffmpeg)
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.resolve(process.argv[2] || path.join(here, "board-mockup.mp4"));
const FPS = 25;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "board-"));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.join(here, "board-mockup.html")).href + "?static");
await page.evaluate(() => window.ready);
const frames = Math.round((await page.evaluate(() => window.DURATION)) * FPS);
for (let f = 0; f < frames; f++) {
  await page.evaluate(t => render(t), f / FPS);
  await page.screenshot({ path: path.join(tmp, `f_${String(f).padStart(4, "0")}.png`) });
}
await browser.close();
execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-framerate", String(FPS), "-i", path.join(tmp, "f_%04d.png"),
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", out], { stdio: "inherit" });
fs.rmSync(tmp, { recursive: true });
console.log(`wrote ${out} (${frames} frames)`);
