// Single source of truth for the slide: palette, fonts, canvas, and a
// renderer-agnostic op list consumed by both build.js (PPTX) and preview.js (SVG).
const CANVAS = { w: 13.333, h: 7.5 };
const C = {
  INK: "0F2138", NAVY: "0B2545", BLUE: "1565C0", BLUE_LT: "E9F1FB",
  TEAL: "0E8C8C", TEAL_LT: "E1F2F1", ORANGE: "EC8A1C", ORANGE_LT: "FDF0DC",
  GRAY: "566374", GRAY_LT: "93A0AE", LINE: "DBE3EE", PANEL: "F5F8FC", WHITE: "FFFFFF",
};
const FONT = "Microsoft YaHei";
const FONT_EN = "Arial";

function buildOps() {
  const ops = [];
  const rect = (o) => ops.push({ k: "rect", r: 0, ...o });
  const oval = (o) => ops.push({ k: "oval", ...o });
  const line = (o) => ops.push({ k: "line", ...o });
  const icon = (o) => ops.push({ k: "icon", ...o });
  const text = (o) => ops.push({ k: "text", align: "left", valign: "middle", margin: 0, ...o });
  const bullets = (o) => ops.push({ k: "bullets", ...o });

  // ---------- HEADER ----------
  rect({ x: 0.5, y: 0.5, w: 0.64, h: 0.64, r: 0.1, fill: C.NAVY });
  icon({ key: "logo", color: "FFFFFF", x: 0.66, y: 0.66, w: 0.32, h: 0.32 });
  text({ x: 1.3, y: 0.5, w: 9.2, h: 0.26, runs: [{ t: "海柔创新  HAI ROBOTICS    |    智能仓储解决方案", font: FONT, size: 11, bold: true, color: C.BLUE, sp: 1 }] });
  text({ x: 1.27, y: 0.76, w: 9.2, h: 0.5, runs: [{ t: "武汉 FC 料箱到人系统方案", font: FONT, size: 29, bold: true, color: C.NAVY }] });
  rect({ x: 10.86, y: 0.6, w: 1.97, h: 0.5, r: 0.1, fill: C.BLUE_LT });
  text({ x: 10.86, y: 0.6, w: 1.97, h: 0.5, align: "center", runs: [{ t: "方案总览 · OVERVIEW", font: FONT, size: 10.5, bold: true, color: C.BLUE }] });
  text({ x: 0.5, y: 1.32, w: 12.33, h: 0.32, runs: [{ t: "箱式机器人（ACR）存拣系统　—　储存料箱入库 · 智能存储搬运 · 订单拣选出库，实现入库到出库全流程自动化", font: FONT, size: 12.5, color: C.GRAY }] });

  const sectionLabel = (y, zh, en) => {
    rect({ x: 0.5, y: y + 0.05, w: 0.14, h: 0.14, r: 0.03, fill: C.ORANGE });
    text({ x: 0.72, y, w: 11.5, h: 0.26, runs: [
      { t: zh + "  ", font: FONT, size: 12.5, bold: true, color: C.INK },
      { t: en, font: FONT_EN, size: 9.5, bold: true, color: C.GRAY_LT, sp: 1 },
    ] });
  };

  // ---------- SECTION 1: WORKFLOW ----------
  sectionLabel(1.78, "端到端作业流程", "END-TO-END WORKFLOW");
  const steps = [
    { n: "01", key: "w1", c: C.BLUE,   lt: C.BLUE_LT,   t: "上游接单", d: "WHC·WMS 接口对接" },
    { n: "02", key: "w2", c: C.TEAL,   lt: C.TEAL_LT,   t: "收货入库", d: "入库工作站 In_01~06" },
    { n: "03", key: "w3", c: C.ORANGE, lt: C.ORANGE_LT, t: "智能存储", d: "货架存储 · ACR 搬运" },
    { n: "04", key: "w4", c: C.BLUE,   lt: C.BLUE_LT,   t: "人机直拣", d: "直拣工作站 out_01~22" },
    { n: "05", key: "w5", c: C.TEAL,   lt: C.TEAL_LT,   t: "订单出库", d: "打包复核 · 30 打包台" },
  ];
  const wCardW = 2.15, wGap = 0.395, wTop = 2.12, wH = 1.32;
  steps.forEach((st, i) => {
    const x = 0.5 + i * (wCardW + wGap);
    const cx = x + wCardW / 2;
    rect({ x, y: wTop, w: wCardW, h: wH, r: 0.09, fill: C.WHITE, line: { color: C.LINE, width: 0.75 }, shadow: true });
    oval({ x: cx - 0.31, y: wTop + 0.16, w: 0.62, h: 0.62, fill: st.lt });
    icon({ key: st.key, color: st.c, x: cx - 0.17, y: wTop + 0.30, w: 0.34, h: 0.34 });
    text({ x: x + 0.12, y: wTop + 0.1, w: 0.6, h: 0.24, valign: "top", runs: [{ t: st.n, font: FONT_EN, size: 11, bold: true, color: C.GRAY_LT }] });
    text({ x, y: wTop + 0.86, w: wCardW, h: 0.26, align: "center", runs: [{ t: st.t, font: FONT, size: 13, bold: true, color: C.NAVY }] });
    text({ x, y: wTop + 1.11, w: wCardW, h: 0.2, align: "center", runs: [{ t: st.d, font: FONT, size: 9, color: C.GRAY }] });
    if (i < steps.length - 1) line({ x: x + wCardW + 0.05, y: wTop + 0.47, w: wGap - 0.1, h: 0, color: C.ORANGE, width: 1.75, arrow: true });
  });

  // ---------- SECTION 2: COMPOSITION ----------
  sectionLabel(3.66, "系统组成", "SYSTEM COMPOSITION");
  const comp = [
    { key: "cA", c: C.BLUE, lt: C.BLUE_LT, t: "软件系统层 · 海柔 HAIQ", en: "SOFTWARE PLATFORM",
      rows: ["WES 仓库执行系统：业务 / 库存 / 订单", "ESS 设备调度系统：机器人 / 路径 / 充电", "DP 数据平台：报表 / 预警 / 分析", "业务模块：入库 · 出库 · 库内 · 基础资料"] },
    { key: "cB", c: C.TEAL, lt: C.TEAL_LT, t: "设备资源层", en: "EQUIPMENT & ROBOTS",
      rows: ["箱式机器人 A71-L-E1-H-CN ×150", "导航方式：惯性 + 二维码", "HRC-3000-E4-CN 智能充电桩 ×25", "德玛输送线（Modbus）· 安全门"] },
    { key: "cC", c: C.ORANGE, lt: C.ORANGE_LT, t: "工作站层", en: "WORKSTATIONS",
      rows: ["入库工作站 In_01~06（+异常 In_11）", "入库取箱口 ×5 · 人机直拣站 ×22", "订单打包台 5组×6 = 30 个", "异常打包口 101 / 102"] },
  ];
  const cCardW = 3.91, cGap = 0.3, cTop = 3.98, cH = 1.95;
  comp.forEach((cd, i) => {
    const x = 0.5 + i * (cCardW + cGap);
    rect({ x, y: cTop, w: cCardW, h: cH, r: 0.08, fill: C.WHITE, line: { color: C.LINE, width: 0.75 }, shadow: true });
    oval({ x: x + 0.24, y: cTop + 0.22, w: 0.52, h: 0.52, fill: cd.lt });
    icon({ key: cd.key, color: cd.c, x: x + 0.37, y: cTop + 0.35, w: 0.26, h: 0.26 });
    text({ x: x + 0.88, y: cTop + 0.22, w: cCardW - 1.05, h: 0.28, runs: [{ t: cd.t, font: FONT, size: 12.5, bold: true, color: cd.c }] });
    text({ x: x + 0.88, y: cTop + 0.5, w: cCardW - 1.05, h: 0.2, runs: [{ t: cd.en, font: FONT_EN, size: 8, bold: true, color: C.GRAY_LT, sp: 1 }] });
    bullets({ x: x + 0.3, y: cTop + 0.86, w: cCardW - 0.55, h: cH - 0.98, font: FONT, size: 9.3, color: C.INK, spaceAfter: 5, items: cd.rows });
  });

  // ---------- SECTION 3: METRICS ----------
  const mTop = 6.06, mH = 0.88, seg = 12.33 / 5;
  rect({ x: 0.5, y: mTop, w: 12.33, h: mH, r: 0.08, fill: C.PANEL, line: { color: C.LINE, width: 0.75 } });
  const metrics = [
    { num: "150", unit: " 台", c: C.NAVY, lab: "箱式机器人 ACR" },
    { num: "420", unit: " 箱/h", c: C.BLUE, lab: "峰值出库能力*" },
    { num: "99", unit: "%+", c: C.TEAL, lab: "拣选准确率*" },
    { num: "70–80", unit: "%", c: C.ORANGE, lab: "人工效率提升*" },
    { num: "17", unit: " 个", c: C.BLUE, lab: "上游系统接口" },
  ];
  metrics.forEach((m, i) => {
    const x = 0.5 + i * seg;
    if (i > 0) line({ x, y: mTop + 0.18, w: 0, h: mH - 0.36, color: C.LINE, width: 1 });
    text({ x, y: mTop + 0.12, w: seg, h: 0.44, align: "center", runs: [
      { t: m.num, font: FONT_EN, size: 24, bold: true, color: m.c },
      { t: m.unit, font: FONT, size: 13, bold: true, color: m.c },
    ] });
    text({ x, y: mTop + 0.56, w: seg, h: 0.24, align: "center", runs: [{ t: m.lab, font: FONT, size: 9.5, color: C.GRAY }] });
  });

  // ---------- FOOTER ----------
  text({ x: 0.5, y: 7.04, w: 9, h: 0.26, runs: [{ t: "* 效能指标参考海柔 HaiPick / 闪攀系统典型表现，最终以现场实测为准。", font: FONT, size: 8, color: C.GRAY_LT }] });
  text({ x: 7.83, y: 7.04, w: 5, h: 0.26, align: "right", runs: [{ t: "武汉 FC 自动化仓储项目  ·  HAI ROBOTICS 海柔创新", font: FONT, size: 8.5, bold: true, color: C.GRAY }] });

  return ops;
}

module.exports = { CANVAS, C, FONT, FONT_EN, buildOps };
