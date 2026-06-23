// Build the PPTX from the shared op list.
const pptxgen = require("pptxgenjs");
const { CANVAS, C, buildOps } = require("./slide");
const { rasterize } = require("./icons");

(async () => {
  const ops = buildOps();
  // pre-render icons
  const cache = {};
  for (const op of ops) {
    if (op.k === "icon") {
      const id = op.key + "_" + op.color;
      if (!cache[id]) cache[id] = "image/png;base64," + (await rasterize(op.key, op.color));
      op._data = cache[id];
    }
  }

  const pres = new pptxgen();
  pres.defineLayout({ name: "W", width: CANVAS.w, height: CANVAS.h });
  pres.layout = "W";
  pres.author = "HAI ROBOTICS";
  pres.title = "武汉FC 料箱到人系统方案";
  const s = pres.addSlide();
  s.background = { color: C.WHITE };

  const mkShadow = () => ({ type: "outer", color: "8AA0BC", blur: 7, offset: 3, angle: 90, opacity: 0.22 });

  for (const op of ops) {
    if (op.k === "rect") {
      const o = { x: op.x, y: op.y, w: op.w, h: op.h, fill: { color: op.fill } };
      if (op.line) o.line = { color: op.line.color, width: op.line.width };
      if (op.shadow) o.shadow = mkShadow();
      if (op.r) { o.rectRadius = op.r; s.addShape(pres.shapes.ROUNDED_RECTANGLE, o); }
      else s.addShape(pres.shapes.RECTANGLE, o);
    } else if (op.k === "oval") {
      s.addShape(pres.shapes.OVAL, { x: op.x, y: op.y, w: op.w, h: op.h, fill: { color: op.fill } });
    } else if (op.k === "line") {
      const ln = { color: op.color, width: op.width };
      if (op.arrow) ln.endArrowType = "triangle";
      s.addShape(pres.shapes.LINE, { x: op.x, y: op.y, w: op.w, h: op.h, line: ln });
    } else if (op.k === "icon") {
      s.addImage({ data: op._data, x: op.x, y: op.y, w: op.w, h: op.h });
    } else if (op.k === "text") {
      const runs = op.runs.map((r, i) => ({ text: r.t, options: { fontFace: r.font, fontSize: r.size, bold: !!r.bold, color: r.color, charSpacing: r.sp || 0, breakLine: i === op.runs.length - 1 ? false : false } }));
      s.addText(runs, { x: op.x, y: op.y, w: op.w, h: op.h, align: op.align, valign: op.valign, margin: op.margin });
    } else if (op.k === "bullets") {
      const items = op.items.map((t, i) => ({ text: t, options: { bullet: { code: "2022", indent: 12 }, breakLine: true, color: op.color, fontSize: op.size, fontFace: op.font, paraSpaceAfter: op.spaceAfter } }));
      s.addText(items, { x: op.x, y: op.y, w: op.w, h: op.h, margin: 0, valign: "top" });
    }
  }

  await pres.writeFile({ fileName: "武汉FC料箱到人系统方案.pptx" });
  console.log("WROTE 武汉FC料箱到人系统方案.pptx");
})();
