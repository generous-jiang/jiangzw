// 武汉 FC 仓 · 海柔自动化系统落地方案
// 三层：① FC WMS（业务）② 自研 WCS（统一调度·重点·详细）③ 海柔 HAIQ 系统（按原始架构图分层）
const CANVAS = { w: 13.333, h: 7.5 };
const C = {
  INK: "262626", RED: "D7382E", STEEL: "27628D", STEEL_D: "1E4E73",
  NAVY: "1F4E79", CARDT: "2F4458", SUB: "98A2AC", LBL: "8A929B",
  BORD: "D7DDE4", DASH: "AAC2D6", CARDF: "FBFCFD", CHIP: "EDF1F5",
  SECT: "33475A", ENGSUB: "CFE0EC", REDF: "FCF3F2", HAIQF: "F3F7FB", BG: "FFFFFF", WHITE: "FFFFFF",
};
const FONT = "Microsoft YaHei";
const FONT_EN = "Arial";

function buildOps() {
  const ops = [];
  const rect = (o) => ops.push({ k: "rect", r: 0, ...o });
  const line = (o) => ops.push({ k: "line", ...o });
  const text = (o) => ops.push({ k: "text", align: "left", valign: "middle", margin: 0, ...o });
  const bullets = (o) => ops.push({ k: "bullets", ...o });

  const X0 = 0.34, XR = 12.99, CW = XR - X0;      // 12.65
  const inX = 0.50, inW = 12.33, inR = inX + inW; // 12.83

  // section label (square marker + zh [+tag] / right en)
  const sect = (y, zh, en, tag, mk) => {
    rect({ x: X0, y: y + 0.03, w: 0.13, h: 0.13, r: 0.03, fill: mk || C.STEEL });
    const runs = [{ t: zh, font: FONT, size: 9.5, bold: true, color: C.SECT }];
    if (tag) runs.push({ t: "   " + tag, font: FONT, size: 8.5, bold: true, color: C.RED });
    text({ x: X0 + 0.22, y, w: 9.5, h: 0.18, runs });
    if (en) text({ x: inR - 3.4, y, w: 3.4, h: 0.18, align: "right", runs: [{ t: en, font: FONT_EN, size: 8, italic: true, color: C.LBL }] });
  };
  // small inner sub-layer label (within 海柔 block)
  const subLayer = (x, y, w, zh, en) => {
    text({ x, y, w, h: 0.16, runs: [{ t: zh, font: FONT, size: 8.5, bold: true, color: C.STEEL }, { t: "   " + en, font: FONT_EN, size: 7, color: C.LBL }] });
  };
  // card grid
  const cardGrid = (items, x0, y, h, n, totW, ts) => {
    const g = 0.10, cw = (totW - (n - 1) * g) / n;
    items.forEach((it, i) => {
      const x = x0 + i * (cw + g);
      rect({ x, y, w: cw, h, r: 0.03, fill: it.hi ? C.REDF : C.CARDF, line: { color: it.hi ? C.RED : C.BORD, width: it.hi ? 1.0 : 0.6 } });
      text({ x, y: y + 0.045, w: cw, h: 0.155, align: "center", runs: [{ t: it.t, font: FONT, size: ts || 9, bold: true, color: it.hi ? C.RED : (it.dim ? C.SUB : C.CARDT) }] });
      if (it.s) text({ x, y: y + h - 0.165, w: cw, h: 0.13, align: "center", runs: [{ t: it.s, font: FONT, size: 7, color: it.hi ? C.RED : C.SUB }] });
    });
  };

  // ===== TITLE =====
  rect({ x: 0.34, y: 0.24, w: 0.09, h: 0.38, fill: C.RED });
  text({ x: 0.52, y: 0.20, w: 11.6, h: 0.44, runs: [{ t: "武汉 FC 仓 · 海柔自动化系统落地方案", font: FONT, size: 21, bold: true, color: C.INK }] });
  text({ x: 0.52, y: 0.63, w: 12.4, h: 0.20, runs: [{ t: "业务 FC WMS  →  自研 WCS 统一调度（重点）  →  海柔 HAIQ 料箱到人系统执行　·　总体框架在武汉 FC 仓的一次落地", font: FONT, size: 9, color: C.LBL }] });

  // ===== ① FC WMS =====
  sect(0.90, "① 业务系统层 · FC WMS", "BUSINESS · WMS");
  const t1 = [
    { t: "FC Flux WMS", s: "沃尔玛 FC 仓库管理系统" },
    { t: "WHC · 自动化任务编排", s: "任务下发 / 状态回传" },
    { t: "业务数据", s: "订单 · 库存 · 商品 · 波次" },
  ];
  const g1 = 0.20, w1 = (CW - 2 * g1) / 3, c1c = (i) => X0 + i * (w1 + g1) + w1 / 2;
  t1.forEach((b, i) => {
    const x = X0 + i * (w1 + g1);
    rect({ x, y: 1.06, w: w1, h: 0.40, r: 0.04, fill: C.WHITE, line: { color: C.BORD, width: 0.75 } });
    text({ x, y: 1.09, w: w1, h: 0.19, align: "center", runs: [{ t: b.t, font: FONT, size: 10.5, bold: true, color: C.NAVY }] });
    text({ x, y: 1.27, w: w1, h: 0.16, align: "center", runs: [{ t: b.s, font: FONT, size: 7.8, color: C.SUB }] });
  });
  text({ x: 3.0, y: 1.50, w: 7.3, h: 0.13, align: "center", runs: [{ t: "标准指令双向交互：下行指令 / 上行状态", font: FONT, size: 7.8, color: C.LBL }] });
  for (let i = 0; i < 3; i++) line({ x: c1c(i), y: 1.63, w: 0, h: 0.10, color: C.STEEL, width: 1, beginArrow: true, endArrow: true });

  // ===== ② WCS（重点）=====
  rect({ x: X0, y: 1.74, w: CW, h: 2.46, r: 0.06, fill: C.WHITE, line: { color: C.DASH, width: 1.25, dash: true } });
  rect({ x: inX, y: 1.82, w: inW, h: 0.44, r: 0.05, fill: C.STEEL });
  text({ x: inX, y: 1.86, w: inW, h: 0.22, align: "center", runs: [{ t: "WCS · 仓储自动化统一调度引擎（重点）", font: FONT, size: 14, bold: true, color: C.WHITE }] });
  text({ x: inX, y: 2.07, w: inW, h: 0.16, align: "center", runs: [{ t: "标准指令协议 · 版本化管理 · 幂等重试 · 灰度发布 · 限流降级", font: FONT, size: 8.5, color: C.ENGSUB }] });
  text({ x: inX, y: 2.30, w: inW, h: 0.15, align: "center", runs: [{ t: "FC WMS 与海柔系统不直连：统一经 WCS 以标准指令集下发任务 / 回传状态，按设备能力分层调度，供应商可插拔扩展", font: FONT, size: 7.8, color: C.LBL }] });

  sect2(ops, 2.50, "①", "统一调度层", "Scheduling", inX, inR, C);
  cardGrid([
    { t: "任务编排", s: "多任务并行" }, { t: "优先级调度", s: "SLA 分级" }, { t: "路由分配", s: "最优匹配" },
    { t: "限流降级", s: "峰值保护" }, { t: "异常熔断", s: "失败重试" }, { t: "执行监控", s: "时效预警" },
  ], inX, 2.66, 0.34, 6, inW);

  sect2(ops, 3.04, "②", "标准指令集（本仓启用）", "Standard Instruction Set", inX, inR, C);
  cardGrid([
    { t: "收货指令", s: "DWS 称重" }, { t: "上架指令", s: "返回库位" }, { t: "拣货指令", s: "货箱到人" }, { t: "分播指令", s: "格口/门店" },
    { t: "盘点指令", s: "RFID·物理盘" }, { t: "移库指令", s: "库位调整" }, { t: "波次指令", s: "锁号·产能" }, { t: "对账指令", s: "库存核对" },
  ], inX, 3.20, 0.34, 8, inW);

  sect2(ops, 3.58, "③", "设备能力适配层", "Capability Adapter", inX, inR, C);
  cardGrid([
    { t: "货架到人适配", s: "PopPick 类", dim: true },
    { t: "料箱到人适配", s: "Shuttle 类 · 闪攀", hi: true },
    { t: "托盘到人适配", s: "高位密存类", dim: true },
    { t: "分拣机器人适配", s: "柔性分拣类", dim: true },
    { t: "通用设备适配", s: "AGV/RGV/输送线", dim: true },
  ], inX, 3.74, 0.34, 5, inW);

  // connector 2 (WCS -> 海柔 HAIQ)
  text({ x: 2.6, y: 4.26, w: 8.1, h: 0.14, align: "center", runs: [{ t: "经『料箱到人适配』对接海柔 HAIQ · HTTP REST API（JSON/UTF-8 · 17 个接口）", font: FONT, size: 7.8, color: C.LBL }] });
  const haX = (i) => inX + i * ((inW - 0.6) / 3 + 0.30) + (inW - 0.6) / 6;
  for (let i = 0; i < 3; i++) line({ x: haX(i), y: 4.40, w: 0, h: 0.08, color: C.RED, width: 1, beginArrow: true, endArrow: true });

  // ===== ③ 海柔 HAIQ 系统（分层，按原始架构图）=====
  rect({ x: X0, y: 4.50, w: CW, h: 2.52, r: 0.06, fill: C.WHITE, line: { color: C.DASH, width: 1, dash: true } });
  rect({ x: X0 + 0.16, y: 4.56, w: 0.13, h: 0.13, r: 0.03, fill: C.RED });
  text({ x: X0 + 0.38, y: 4.53, w: 9.5, h: 0.18, runs: [
    { t: "③ 执行系统层 · 海柔 HAIQ 智能仓储系统", font: FONT, size: 9.5, bold: true, color: C.SECT },
    { t: "   WCS3 · 料箱到人 / 闪攀", font: FONT, size: 8.5, bold: true, color: C.RED } ] });
  text({ x: inR - 3.4, y: 4.53, w: 3.4, h: 0.18, align: "right", runs: [{ t: "HAI ROBOTICS · EXECUTION", font: FONT_EN, size: 8, italic: true, color: C.LBL }] });

  // 软件系统层：WES（宽）/ ESS / DP
  subLayer(inX, 4.76, 6, "软件系统层 · 海柔 HAIQ", "SOFTWARE");
  const sw = [
    { t: "WES 仓库执行系统", s: "业务逻辑 / 库存 / 订单 / 工作站", w: 4.91 },
    { t: "ESS 设备调度系统", s: "机器人 / 路径 / 充电调度", w: 3.51 },
    { t: "DP 数据平台", s: "报表 / 预警 / 分析", w: 3.51 },
  ];
  let sx = inX;
  sw.forEach((b) => {
    rect({ x: sx, y: 4.94, w: b.w, h: 0.42, r: 0.04, fill: C.HAIQF, line: { color: C.STEEL, width: 0.8 } });
    text({ x: sx, y: 4.97, w: b.w, h: 0.20, align: "center", runs: [{ t: b.t, font: FONT, size: 10.5, bold: true, color: C.NAVY }] });
    text({ x: sx, y: 5.17, w: b.w, h: 0.16, align: "center", runs: [{ t: b.s, font: FONT, size: 7.8, color: C.SUB }] });
    sx += b.w + 0.20;
  });
  // 业务功能模块 chips
  text({ x: inX, y: 5.42, w: 1.7, h: 0.20, runs: [{ t: "业务功能模块", font: FONT, size: 8.2, bold: true, color: C.STEEL }] });
  const mods = ["基础资料", "入库模块", "出库模块", "库内模块", "系统管理"];
  const mx0 = inX + 1.75, mtot = inR - mx0, mg = 0.12, mw = (mtot - (mods.length - 1) * mg) / mods.length;
  mods.forEach((m, i) => {
    const x = mx0 + i * (mw + mg);
    rect({ x, y: 5.40, w: mw, h: 0.26, r: 0.05, fill: C.CHIP });
    text({ x, y: 5.40, w: mw, h: 0.26, align: "center", runs: [{ t: m, font: FONT, size: 8.2, color: C.INK }] });
  });
  // connector software -> physical
  text({ x: inX, y: 5.72, w: inW, h: 0.13, align: "center", runs: [{ t: "ESS 任务下发 / 设备状态回传", font: FONT, size: 7.6, color: C.LBL }] });
  for (const cx of [3.5, 6.66, 9.8]) line({ x: cx, y: 5.86, w: 0, h: 0.10, color: C.STEEL, width: 1, beginArrow: true, endArrow: true });

  // 物理层：设备资源层 | 工作站层
  const pg = 0.30, pw = (inW - pg) / 2, pL = inX, pR = inX + pw + pg;
  rect({ x: pL, y: 5.98, w: pw, h: 0.96, r: 0.04, fill: C.CARDF, line: { color: C.BORD, width: 0.6 } });
  rect({ x: pR, y: 5.98, w: pw, h: 0.96, r: 0.04, fill: C.CARDF, line: { color: C.BORD, width: 0.6 } });
  subLayer(pL + 0.16, 6.04, pw - 0.3, "设备资源层", "EQUIPMENT");
  subLayer(pR + 0.16, 6.04, pw - 0.3, "工作站层", "WORKSTATIONS");
  bullets({ x: pL + 0.18, y: 6.24, w: pw - 0.34, h: 0.66, font: FONT, size: 8.4, color: C.CARDT, spaceAfter: 3, items: [
    "箱式机器人 A71-L-E1-H-CN ×150（惯性 + 二维码导航）", "HRC-3000-E4-CN 智能充电桩 ×25",
    "德玛输送线（Modbus 协议）· 安全门 / 安全围栏" ] });
  bullets({ x: pR + 0.18, y: 6.20, w: pw - 0.34, h: 0.74, font: FONT, size: 8.4, color: C.CARDT, spaceAfter: 2, items: [
    "入库工作站 In_01~06（+异常 In_11）", "入库取箱口 ×5（In_101/102/103/105/111）",
    "人机直拣工作站 out_01~22 · 异常打包口 101/102", "订单打包台 5 组×6 = 30 个" ] });

  // ===== NOTE =====
  text({ x: X0, y: 7.08, w: CW, h: 0.3, valign: "top", runs: [{ t: "说明：FC WMS 不直连自动化设备；统一经自研 WCS 以标准指令集下发、按『料箱到人』能力适配调度海柔 HAIQ 系统（WES/ESS/DP），由 ESS 驱动箱式机器人与各工作站完成入库到出库全流程。", font: FONT, size: 7.8, color: C.LBL }] });

  return ops;
}

function sect2(ops, y, num, zh, en, inX, inR, C) {
  ops.push({ k: "text", align: "left", valign: "middle", margin: 0, x: inX, y, w: 6, h: 0.18, runs: [
    { t: num + "  ", font: FONT, size: 10, bold: true, color: C.STEEL }, { t: zh, font: FONT, size: 10, bold: true, color: C.SECT }] });
  ops.push({ k: "text", align: "right", valign: "middle", margin: 0, x: inR - 3.2, y, w: 3.2, h: 0.18, runs: [
    { t: en, font: FONT_EN, size: 8, italic: true, color: C.LBL }] });
}

module.exports = { CANVAS, C, FONT, FONT_EN, buildOps };
