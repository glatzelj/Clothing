// Render SVG files to transparent PNGs with headless Chromium.
// Usage: node render_svg.mjs <out_width_px> file1.svg [file2.svg ...]
// Writes file.png next to each file.svg.
import { createRequire } from "node:module";
import fs from "node:fs";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const [width, ...files] = process.argv.slice(2);
const browser = await chromium.launch();
for (const file of files) {
  const svg = fs.readFileSync(file, "utf8");
  const [, , vw, vh] = svg.match(/viewBox="([^"]+)"/)[1].split(/[\s,]+/).map(Number);
  const page = await browser.newPage({
    viewport: { width: vw, height: vh },
    deviceScaleFactor: Number(width) / vw,
  });
  await page.setContent(
    `<style>html,body{margin:0;background:transparent}svg{display:block;width:${vw}px;height:${vh}px}</style>${svg}`
  );
  const out = file.replace(/\.svg$/, ".png");
  await page.screenshot({ path: out, omitBackground: true });
  console.log("wrote", out);
  await page.close();
}
await browser.close();
