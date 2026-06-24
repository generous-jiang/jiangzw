// Coordinate-accurate SVG preview (rasterized via sharp) for visual QA.
// Usage: node preview.js [debug]
const sharp = require("sharp");
const { CANVAS, buildOps } = require("./slide");

const DEBUG = process.argv.includes("debug");
const DPI = 150;
const PX = (i) => i * DPI;
const PT = (p) => p * DPI / 72;
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const CJK = "WenQuanYi Zen Hei, DejaVu Sans, sans-serif";

function textSvg(op) {
  const ms = PT(Math.max(...op.runs.map((r) => r.size)));
  let ax, anchor;
  if (op.align === "center") { ax = PX(op.x + op.w / 2); anchor = "middle"; }
  else if (op.align === "right") { ax = PX(op.x + op.w) - 1; anchor = "end"; }
  else { ax = PX(op.x) + 1; anchor = "start"; }
  let by;
  if (op.valign === "top") by = PX(op.y) + ms * 0.92;
  else if (op.valign === "bottom") by = PX(op.y + op.h) - ms * 0.2;
  else by = PX(op.y + op.h / 2) + ms * 0.34;
  const tspans = op.runs.map((r) => {
    const it = r.italic ? ` font-style="italic"` : "";
    const ls = r.sp ? ` letter-spacing="${PT(r.sp).toFixed(1)}"` : "";
    return `<tspan font-size="${PT(r.size).toFixed(1)}" font-weight="${r.bold ? 700 : 400}" fill="#${r.color}"${it}${ls}>${esc(r.t)}</tspan>`;
  }).join("");
  let out = `<text x="${ax.toFixed(1)}" y="${by.toFixed(1)}" text-anchor="${anchor}" font-family="${CJK}">${tspans}</text>`;
  if (DEBUG) out = `<rect x="${PX(op.x).toFixed(1)}" y="${PX(op.y).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" fill="none" stroke="#FF5577" stroke-width="0.6" stroke-dasharray="3 3"/>` + out;
  return out;
}

(async () => {
  const ops = buildOps();
  const W = PX(CANVAS.w), H = PX(CANVAS.h);
  let body = `<rect x="0" y="0" width="${W}" height="${H}" fill="#FFFFFF"/>`;
  for (const op of ops) {
    if (op.k === "rect") {
      const dash = op.line && op.line.dash ? ` stroke-dasharray="6 4"` : "";
      const stroke = op.line ? ` stroke="#${op.line.color}" stroke-width="${(op.line.width * DPI / 96).toFixed(2)}"${dash}` : "";
      body += `<rect x="${PX(op.x).toFixed(1)}" y="${PX(op.y).toFixed(1)}" width="${PX(op.w).toFixed(1)}" height="${PX(op.h).toFixed(1)}" rx="${PX(op.r || 0).toFixed(1)}" fill="#${op.fill}"${stroke}/>`;
    } else if (op.k === "line") {
      const x1 = PX(op.x), y1 = PX(op.y), x2 = PX(op.x + op.w), y2 = PX(op.y + op.h);
      body += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="#${op.color}" stroke-width="${(op.width * DPI / 96).toFixed(2)}"/>`;
      const a = 4;
      if (op.endArrow) body += `<polygon points="${x2},${y2} ${(x2 - a).toFixed(1)},${(y2 - a).toFixed(1)} ${(x2 + a).toFixed(1)},${(y2 - a).toFixed(1)}" fill="#${op.color}"/>`;
      if (op.beginArrow) body += `<polygon points="${x1},${y1} ${(x1 - a).toFixed(1)},${(y1 + a).toFixed(1)} ${(x1 + a).toFixed(1)},${(y1 + a).toFixed(1)}" fill="#${op.color}"/>`;
    } else if (op.k === "text") {
      body += textSvg(op);
    }
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${body}</svg>`;
  const out = DEBUG ? "preview_debug.png" : "preview.png";
  await sharp(Buffer.from(svg)).png().toFile(out);
  console.log("WROTE " + out);
})();
