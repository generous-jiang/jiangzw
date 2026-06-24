// 武汉 FC 仓 · 海柔自动化系统方案 — FC WMS → WCS → 海柔(闪攀) 三层落地
// 总体框架（全渠道 WCS 产品方案）在武汉 FC 仓的一次落地实例。风格与总框架一致。
const CANVAS = { w: 13.333, h: 7.5 };
const C = {
  INK: "262626", RED: "D7382E", STEEL: "27628D", STEEL_D: "1E4E73",
  NAVY: "1F4E79", CARDT: "2F4458", SUB: "98A2AC", LBL: "8A929B",
  BORD: "D7DDE4", DASH: "AAC2D6", CARDF: "FBFCFD", CHIP: "EDF1F5",
  SECT: "33475A", ENGSUB: "CFE0EC", REDF: "FCF3F2", BG: "FFFFFF", WHITE: "FFFFFF",
};
const FONT = "Microsoft YaHei";
const FONT_EN = "Arial";

function buildOps() {
  const ops = [];
  const rect = (o) => ops.push({ k: "rect", r: 0, ...o });
  const line = (o) => ops.push({ k: "line", ...o });
  const text = (o) => ops.push({ k: "text", align: "left", valign: "middle", margin: 0, ...o });
  const bullets = (o) => ops.push({ k: "bullets", ...o });

  const X0 = 0.34, XR = 12.99, CW = XR - X0;     // 12.65
  const inX = 0.50, inW = 12.33, inR = inX + inW; // WCS/Tier3 inner

  // ===== TITLE =====
  rect({ x: 0.34, y: 0.30, w: 0.09, h: 0.40, fill: C.RED });
  text({ x: 0.52, y: 0.26, w: 11.5, h: 0.46, runs: [{ t: "武汉 FC 仓 · 海柔自动化系统方案", font: FONT, size: 22, bold: true, color: C.INK }] });
  text({ x: 0.52, y: 0.74, w: 12.4, h: 0.22, runs: [{ t: "FC WMS → 自研 WCS → 海柔闪攀（料箱到人）　·　全渠道仓库自动化总体框架在武汉 FC 仓的一次落地", font: FONT, size: 9.5, color: C.LBL }] });

  // section label helper (left zh [+tag] / right en)
  const sect = (y, zh, en, tag) => {
    rect({ x: X0, y: y + 0.03, w: 0.13, h: 0.13, r: 0.03, fill: C.STEEL });
    const runs = [{ t: zh, font: FONT, size: 9.5, bold: true, color: C.SECT }];
    if (tag) runs.push({ t: "    " + tag, font: FONT, size: 8.5, bold: true, color: C.RED });
    text({ x: X0 + 0.22, y, w: 9, h: 0.18, runs });
    if (en) text({ x: inR - 3.4, y, w: 3.4, h: 0.18, align: "right", runs: [{ t: en, font: FONT_EN, size: 8, italic: true, color: C.LBL }] });
  };
  // card grid helper
  const cardGrid = (items, x0, y, h, n, totW, big) => {
    const g = 0.10, cw = (totW - (n - 1) * g) / n;
    items.forEach((it, i) => {
      const x = x0 + i * (cw + g);
      rect({ x, y, w: cw, h, r: 0.03, fill: it.hi ? C.REDF : C.CARDF, line: { color: it.hi ? C.RED : C.BORD, width: it.hi ? 1.0 : 0.6 } });
      text({ x, y: y + 0.05, w: cw, h: 0.20, align: "center", runs: [{ t: it.t, font: FONT, size: big ? 9.5 : 9, bold: true, color: it.hi ? C.RED : (it.dim ? C.SUB : C.CARDT) }] });
      text({ x, y: y + h - 0.21, w: cw, h: 0.17, align: "center", runs: [{ t: it.s, font: FONT, size: 7.3, color: it.hi ? C.RED : C.SUB }] });
    });
  };

  // ===== TIER 1 — 上游业务系统 / FC WMS =====
  sect(0.98, "上游业务系统 · FC WMS", "BUSINESS · WMS");
  const t1 = [
    { t: "FC Flux WMS", s: "沃尔玛 FC 仓库管理系统" },
    { t: "WHC · 自动化任务编排", s: "上游任务统一编排 · 下发 / 回传" },
    { t: "对接接口", s: "HTTP REST API · JSON/UTF-8 · 17 个接口" },
  ];
  const g1 = 0.20, w1 = (CW - 2 * g1) / 3;
  const c1ctr = (i) => X0 + i * (w1 + g1) + w1 / 2;
  t1.forEach((b, i) => {
    const x = X0 + i * (w1 + g1);
    rect({ x, y: 1.16, w: w1, h: 0.46, r: 0.04, fill: C.WHITE, line: { color: C.BORD, width: 0.75 } });
    text({ x, y: 1.20, w: w1, h: 0.20, align: "center", runs: [{ t: b.t, font: FONT, size: 11, bold: true, color: C.NAVY }] });
    text({ x, y: 1.40, w: w1, h: 0.17, align: "center", runs: [{ t: b.s, font: FONT, size: 8, color: C.SUB }] });
  });
  // connector 1
  text({ x: 2.6, y: 1.66, w: 8.1, h: 0.14, align: "center", runs: [{ t: "标准指令双向交互：下行指令 / 上行状态，统一经 WCS", font: FONT, size: 8, color: C.LBL }] });
  for (let i = 0; i < 3; i++) line({ x: c1ctr(i), y: 1.80, w: 0, h: 0.11, color: C.STEEL, width: 1, beginArrow: true, endArrow: true });

  // ===== TIER 2 — WCS 统一调度引擎 =====
  rect({ x: X0, y: 1.94, w: CW, h: 2.46, r: 0.06, fill: C.WHITE, line: { color: C.DASH, width: 1, dash: true } });
  rect({ x: inX, y: 2.02, w: inW, h: 0.44, r: 0.05, fill: C.STEEL });
  text({ x: inX, y: 2.06, w: inW, h: 0.22, align: "center", runs: [{ t: "WCS · 仓储自动化统一调度引擎", font: FONT, size: 14, bold: true, color: C.WHITE }] });
  text({ x: inX, y: 2.27, w: inW, h: 0.16, align: "center", runs: [{ t: "标准指令协议 · 版本化管理 · 幂等重试 · 灰度发布 · 限流降级", font: FONT, size: 8.5, color: C.ENGSUB }] });

  sect2(ops, 2.52, "①", "统一调度层", "Scheduling", inX, inR, C);
  cardGrid([
    { t: "任务编排", s: "多任务并行" }, { t: "优先级调度", s: "SLA 分级" }, { t: "路由分配", s: "最优匹配" },
    { t: "限流降级", s: "峰值保护" }, { t: "异常熔断", s: "失败重试" }, { t: "执行监控", s: "时效预警" },
  ], inX, 2.70, 0.34, 6, inW);

  sect2(ops, 3.10, "②", "标准指令集（本仓启用）", "Standard Instruction Set", inX, inR, C);
  cardGrid([
    { t: "收货指令", s: "DWS 称重" }, { t: "上架指令", s: "返回库位" }, { t: "拣货指令", s: "货箱到人" }, { t: "分播指令", s: "格口/门店" },
    { t: "盘点指令", s: "RFID·物理盘" }, { t: "移库指令", s: "库位调整" }, { t: "波次指令", s: "锁号·产能" }, { t: "对账指令", s: "库存核对" },
  ], inX, 3.28, 0.34, 8, inW);

  sect2(ops, 3.68, "③", "设备能力适配层", "Capability Adapter", inX, inR, C);
  cardGrid([
    { t: "货架到人适配", s: "PopPick 类", dim: true },
    { t: "料箱到人适配", s: "Shuttle 类 · 闪攀", hi: true },
    { t: "托盘到人适配", s: "高位密存类", dim: true },
    { t: "分拣机器人适配", s: "柔性分拣类", dim: true },
    { t: "通用设备适配", s: "AGV/RGV/输送线", dim: true },
  ], inX, 3.86, 0.40, 5, inW, true);

  // connector 2
  text({ x: 3.0, y: 4.46, w: 7.3, h: 0.14, align: "center", runs: [{ t: "经『料箱到人适配』下发标准指令 / 回传执行状态", font: FONT, size: 8, color: C.LBL }] });
  const t3col = (i) => inX + i * ((inW - 0.6) / 3 + 0.30) + (inW - 0.6) / 6;
  for (let i = 0; i < 3; i++) line({ x: t3col(i), y: 4.58, w: 0, h: 0.11, color: C.RED, width: 1, beginArrow: true, endArrow: true });

  // ===== TIER 3 — 海柔闪攀 料箱到人执行系统 =====
  rect({ x: X0, y: 4.72, w: CW, h: 2.02, r: 0.06, fill: C.WHITE, line: { color: C.DASH, width: 1, dash: true } });
  rect({ x: X0 + 0.16, y: 4.80, w: 0.13, h: 0.13, r: 0.03, fill: C.RED });
  text({ x: X0 + 0.38, y: 4.77, w: 9, h: 0.18, runs: [
    { t: "下游执行系统 · 海柔 闪攀", font: FONT, size: 9.5, bold: true, color: C.SECT },
    { t: "    WCS3 · 料箱到人", font: FONT, size: 8.5, bold: true, color: C.RED },
  ] });
  text({ x: inR - 3.4, y: 4.77, w: 3.4, h: 0.18, align: "right", runs: [{ t: "HAI ROBOTICS · EXECUTION", font: FONT_EN, size: 8, italic: true, color: C.LBL }] });

  const colW = (inW - 0.6) / 3;
  const t3 = [
    { t: "海柔 HAIQ · 软件平台", en: "SOFTWARE / HAIQ", rows: [
      "WES 仓库执行系统：业务 / 库存 / 订单 / 工作站", "ESS 设备调度系统：机器人 / 路径 / 充电调度",
      "DP 数据平台：报表 / 预警 / 分析", "可视化：全仓任务 · 指令执行 · 异常工单 · 数字孪生"] },
    { t: "设备资源 · ACR & 充电", en: "EQUIPMENT", rows: [
      "箱式机器人 A71-L-E1-H-CN ×150", "导航方式：惯性 + 二维码",
      "HRC-3000-E4-CN 智能充电桩 ×25", "德玛输送线（Modbus）· 安全门"] },
    { t: "工作站 · 出入库作业", en: "WORKSTATIONS", rows: [
      "入库工作站 In_01~06（+异常 In_11）", "入库取箱口 ×5（In_101/102/103/105/111）",
      "人机直拣工作站 out_01~22", "订单打包台 5 组×6 = 30 个 · 异常打包口 101/102"] },
  ];
  t3.forEach((col, i) => {
    const x = inX + i * (colW + 0.30);
    rect({ x, y: 4.98, w: colW, h: 1.62, r: 0.04, fill: C.CARDF, line: { color: C.BORD, width: 0.6 } });
    text({ x: x + 0.16, y: 5.04, w: colW - 0.3, h: 0.22, runs: [{ t: col.t, font: FONT, size: 11, bold: true, color: C.NAVY }] });
    text({ x: x + 0.16, y: 5.26, w: colW - 0.3, h: 0.14, runs: [{ t: col.en, font: FONT_EN, size: 7.5, bold: true, color: C.LBL, sp: 1 }] });
    bullets({ x: x + 0.18, y: 5.46, w: colW - 0.34, h: 1.05, font: FONT, size: 8.6, color: C.CARDT, spaceAfter: 4, items: col.rows });
  });

  // ===== NOTE =====
  text({ x: X0, y: 6.82, w: CW, h: 0.4, valign: "top", runs: [{ t: "说明：FC WMS 不直连自动化设备，统一经自研 WCS 以标准指令集下发、按『料箱到人』能力适配调度海柔闪攀系统；本页为全渠道仓库自动化总体框架在武汉 FC 仓的一次落地实例。", font: FONT, size: 8, color: C.LBL }] });

  return ops;
}

// WCS sublayer label (①②③ + english) — kept separate to reuse exact framework style
function sect2(ops, y, num, zh, en, inX, inR, C) {
  ops.push({ k: "text", align: "left", valign: "middle", margin: 0, x: inX, y, w: 6, h: 0.18, runs: [
    { t: num + "  ", font: FONT, size: 10, bold: true, color: C.STEEL }, { t: zh, font: FONT, size: 10, bold: true, color: C.SECT }] });
  ops.push({ k: "text", align: "right", valign: "middle", margin: 0, x: inR - 3.2, y, w: 3.2, h: 0.18, runs: [
    { t: en, font: FONT_EN, size: 8, italic: true, color: C.LBL }] });
}

module.exports = { CANVAS, C, FONT, FONT_EN, buildOps };
