// Coordinate-accurate SVG preview of the slide (rasterized via sharp) for visual QA.
// Usage: node preview.js [debug]
const sharp = require("sharp");
const { CANVAS, buildOps } = require("./slide");
const { rasterize } = require("./icons");

const DEBUG = process.argv.includes("debug");
const DPI = 150;
const PX = (inch) => inch * DPI;
const PT = (pt) => pt * DPI / 72;
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const CJK = "WenQuanYi Zen Hei, DejaVu Sans, sans-serif";

function textSvg(op) {
  const maxSize = Math.max(...op.runs.map((r) => r.size));
  const ms = PT(maxSize);
  let ax, anchor;
  if (op.align === "center") { ax = PX(op.x + op.w / 2); anchor = "middle"; }
  else if (op.align === "right") { ax = PX(op.x + op.w) - 1; anchor = "end"; }
  else { ax = PX(op.x) + 1; anchor = "start"; }
  let by;
  if (op.valign === "top") by = PX(op.y) + ms * 0.92;
  else if (op.valign === "bottom") by = PX(op.y + op.h) - ms * 0.2;
  else by = PX(op.y + op.h / 2) + ms * 0.34;
  const tspans = op.runs.map((r) => {
    const ls = r.sp ? ` letter-spacing="${PT(r.sp).toFixed(1)}"` : "";
    return `<tspan font-size="${PT(r.size).toFixed(1)}" font-weight="${r.bold ? 700 : 400}" fill="#${r.color}"${ls}>${esc(r.t)}</tspan>`;
  }).join("");
  let out = `<text x="${ax.toFixed(1)}" y="${by.toFixed(1)}" text-anchor="${anchor}" font-family="${CJK}">${tspans}</text>`;
  if (DEBUG) out = `<rect x="${PX(op.x).toFixed(1)}" y="${PX(op.y).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" fill="none" stroke="#FF5577" stroke-width="0.6" stroke-dasharray="3 3"/>` + out;
  return out;
}

function bulletsSvg(op) {
  const size = PT(op.size);
  const lh = size * 1.18 + PT(op.spaceAfter);
  let y = PX(op.y) + size * 0.95;
  const x = PX(op.x);
  let out = "";
  if (DEBUG) out += `<rect x="${PX(op.x).toFixed(1)}" y="${PX(op.y).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" fill="none" stroke="#FF5577" stroke-width="0.6" stroke-dasharray="3 3"/>`;
  for (const item of op.items) {
    out += `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-family="${CJK}" font-size="${size.toFixed(1)}" fill="#${op.color}"><tspan fill="#EC8A1C" font-weight="700">•  </tspan>${esc(item)}</text>`;
    y += lh;
  }
  return out;
}

(async () => {
  const ops = buildOps();
  // rasterize real icons so the preview matches the PPTX
  const iconCache = {};
  for (const op of ops) {
    if (op.k === "icon") {
      const id = op.key + "_" + op.color;
      if (!iconCache[id]) iconCache[id] = await rasterize(op.key, op.color);
      op._b64 = iconCache[id];
    }
  }
  const W = PX(CANVAS.w), H = PX(CANVAS.h);
  let body = `<rect x="0" y="0" width="${W}" height="${H}" fill="#FFFFFF"/>`;
  for (const op of ops) {
    if (op.k === "rect") {
      if (op.shadow) body += `<rect x="${PX(op.x).toFixed(1)}" y="${(PX(op.y) + 4).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" rx="${PX(op.r || 0).toFixed(1)}" fill="#000000" opacity="0.10"/>`;
      const stroke = op.line ? ` stroke="#${op.line.color}" stroke-width="${(op.line.width * DPI / 96).toFixed(2)}"` : "";
      body += `<rect x="${PX(op.x).toFixed(1)}" y="${PX(op.y).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" rx="${PX(op.r || 0).toFixed(1)}" fill="#${op.fill}"${stroke}/>`;
    } else if (op.k === "oval") {
      body += `<ellipse cx="${PX(op.x + op.w / 2).toFixed(1)}" cy="${PX(op.y + op.h / 2).toFixed(1)}" rx="${PX(op.w / 2).toFixed(1)}" ry="${PX(op.h / 2).toFixed(1)}" fill="#${op.fill}"/>`;
    } else if (op.k === "line") {
      const x1 = PX(op.x), y1 = PX(op.y), x2 = PX(op.x + op.w), y2 = PX(op.y + op.h);
      body += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="#${op.color}" stroke-width="${(op.width * DPI / 96).toFixed(2)}"/>`;
      if (op.arrow) { const a = 5; body += `<polygon points="${x2},${y2} ${(x2 - a).toFixed(1)},${(y2 - a).toFixed(1)} ${(x2 - a).toFixed(1)},${(y2 + a).toFixed(1)}" fill="#${op.color}"/>`; }
    } else if (op.k === "icon") {
      body += `<image x="${PX(op.x).toFixed(1)}" y="${PX(op.y).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" href="data:image/png;base64,${op._b64}"/>`;
    } else if (op.k === "text") {
      body += textSvg(op);
    } else if (op.k === "bullets") {
      body += bulletsSvg(op);
    }
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${body}</svg>`;
  const out = DEBUG ? "preview_debug.png" : "preview.png";
  await sharp(Buffer.from(svg)).png().toFile(out);
  console.log("WROTE " + out);
})();
