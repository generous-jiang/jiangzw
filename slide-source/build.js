// Build the PPTX from the shared op list. Every element is a native, editable PPTX object.
const pptxgen = require("pptxgenjs");
const { CANVAS, C, buildOps } = require("./slide");

(async () => {
  const ops = buildOps();
  const pres = new pptxgen();
  pres.defineLayout({ name: "W", width: CANVAS.w, height: CANVAS.h });
  pres.layout = "W";
  pres.author = "WCS";
  pres.title = "武汉 FC 仓 · 海柔自动化系统方案";
  const s = pres.addSlide();
  s.background = { color: C.BG };

  for (const op of ops) {
    if (op.k === "rect") {
      const o = { x: op.x, y: op.y, w: op.w, h: op.h, fill: { color: op.fill } };
      if (op.line) { o.line = { color: op.line.color, width: op.line.width }; if (op.line.dash) o.line.dashType = "dash"; }
      if (op.r) { o.rectRadius = op.r; s.addShape(pres.shapes.ROUNDED_RECTANGLE, o); }
      else s.addShape(pres.shapes.RECTANGLE, o);
    } else if (op.k === "line") {
      const ln = { color: op.color, width: op.width };
      if (op.endArrow) ln.endArrowType = "triangle";
      if (op.beginArrow) ln.beginArrowType = "triangle";
      s.addShape(pres.shapes.LINE, { x: op.x, y: op.y, w: op.w, h: op.h, line: ln });
    } else if (op.k === "text") {
      const runs = op.runs.map((r) => ({ text: r.t, options: { fontFace: r.font, fontSize: r.size, bold: !!r.bold, italic: !!r.italic, color: r.color, charSpacing: r.sp || 0, breakLine: false } }));
      s.addText(runs, { x: op.x, y: op.y, w: op.w, h: op.h, align: op.align, valign: op.valign, margin: op.margin });
    } else if (op.k === "bullets") {
      const items = op.items.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 12 }, breakLine: true, color: op.color, fontSize: op.size, fontFace: op.font, paraSpaceAfter: op.spaceAfter } }));
      s.addText(items, { x: op.x, y: op.y, w: op.w, h: op.h, margin: 0, valign: "top" });
    }
  }

  await pres.writeFile({ fileName: "武汉FC仓海柔自动化系统方案.pptx" });
  console.log("WROTE 武汉FC仓海柔自动化系统方案.pptx");
})();
