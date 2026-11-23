// Rasterizes assets/svg/*.svg to assets/*.png. Run: node render_assets.js
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const svgDir = path.join(__dirname, "..", "assets", "svg");
const outDir = path.join(__dirname, "..", "assets");

(async () => {
  for (const f of fs.readdirSync(svgDir).filter((n) => n.endsWith(".svg"))) {
    const out = path.join(outDir, f.replace(/\.svg$/, ".png"));
    await sharp(fs.readFileSync(path.join(svgDir, f)), { density: 72 }).png().toFile(out);
    const m = await sharp(out).metadata();
    console.log(f, "->", m.width + "x" + m.height);
  }
})();
