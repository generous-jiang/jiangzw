// Single source of truth: 全渠道仓库自动化接入 WCS · 产品方案 (faithful editable reproduction)
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

  // ---- geometry ----
  const X0 = 0.34, XR = 12.99, CW = XR - X0;            // 12.65
  const upN = 5, upGap = 0.18, upW = (CW - (upN - 1) * upGap) / upN; // 2.386
  const colX = (i) => X0 + i * (upW + upGap);
  const ctr = (i) => colX(i) + upW / 2;

  // ===== TITLE =====
  rect({ x: 0.34, y: 0.30, w: 0.09, h: 0.40, fill: C.RED });
  text({ x: 0.52, y: 0.26, w: 11.5, h: 0.46, runs: [{ t: "全渠道仓库自动化接入 WCS · 产品方案", font: FONT, size: 22, bold: true, color: C.INK }] });
  text({ x: 0.52, y: 0.74, w: 12.4, h: 0.22, runs: [{ t: "Flux WMS 与 WHC 自动化任务编排在上，自研 WCS 以标准指令集统一下发、按能力分层调度自动化设备；上下行交互均经 WCS 贯通衔接", font: FONT, size: 9.5, color: C.LBL }] });

  // ===== UPSTREAM =====
  text({ x: X0, y: 1.02, w: 6, h: 0.18, runs: [{ t: "上游 · 多 WMS / WHC 系统", font: FONT, size: 9, bold: true, color: C.SECT }] });
  const upNames = ["DC Flux WMS", "FC Flux WMS", "City DC WMS", "门店 WMS", "云仓 WMS"];
  upNames.forEach((nm, i) => {
    rect({ x: colX(i), y: 1.20, w: upW, h: 0.46, r: 0.04, fill: C.WHITE, line: { color: C.BORD, width: 0.75 } });
    text({ x: colX(i), y: 1.20, w: upW, h: 0.46, align: "center", runs: [{ t: nm, font: FONT, size: 11, bold: true, color: C.NAVY }] });
  });
  // gap-1 labels + connector arrows
  text({ x: X0, y: 1.70, w: 1.4, h: 0.14, runs: [{ t: "WCS 平台", font: FONT, size: 8, color: C.LBL }] });
  text({ x: 1.8, y: 1.70, w: 5.4, h: 0.14, align: "center", runs: [{ t: "标准指令双向交互：下行指令 / 上行状态，统一经 WCS", font: FONT, size: 8, color: C.LBL }] });
  text({ x: 9.00, y: 1.70, w: 3.2, h: 0.14, runs: [{ t: "看板平台", font: FONT, size: 8, color: C.LBL }] });
  for (let i = 0; i < upN; i++) line({ x: ctr(i), y: 1.86, w: 0, h: 0.11, color: C.STEEL, width: 1, beginArrow: true, endArrow: true });

  // ===== WCS PLATFORM container + VIZ container =====
  const wcsX = X0, wcsW = 8.30, wcsY = 1.98, wcsH = 3.14;     // -> bottom 5.12
  const vizX = 8.82, vizW = XR - vizX;                         // 4.17
  rect({ x: wcsX, y: wcsY, w: wcsW, h: wcsH, r: 0.06, fill: C.WHITE, line: { color: C.DASH, width: 1, dash: true } });
  rect({ x: vizX, y: wcsY, w: vizW, h: wcsH, r: 0.06, fill: C.WHITE, line: { color: C.DASH, width: 1, dash: true } });

  // engine bar
  const inX = 0.50, inW = 7.98, inR = inX + inW; // 8.48
  rect({ x: inX, y: 2.06, w: inW, h: 0.48, r: 0.05, fill: C.STEEL });
  text({ x: inX, y: 2.12, w: inW, h: 0.24, align: "center", runs: [{ t: "WCS · 仓储自动化统一调度引擎", font: FONT, size: 14, bold: true, color: C.WHITE }] });
  text({ x: inX, y: 2.36, w: inW, h: 0.16, align: "center", runs: [{ t: "标准指令协议 · 版本化管理 · 幂等重试 · 灰度发布 · 限流降级", font: FONT, size: 8.5, color: C.ENGSUB }] });

  // helper: section label row (left zh + right english)
  const sect = (y, num, zh, en) => {
    text({ x: inX, y, w: 5.5, h: 0.18, runs: [{ t: num + "  ", font: FONT, size: 10, bold: true, color: C.STEEL }, { t: zh, font: FONT, size: 10, bold: true, color: C.SECT }] });
    text({ x: inR - 3.0, y, w: 3.0, h: 0.18, align: "right", runs: [{ t: en, font: FONT_EN, size: 8, italic: true, color: C.LBL }] });
  };
  // helper: card grid row
  const cards = (items, y, h, n) => {
    const g = 0.10, cw = (inW - (n - 1) * g) / n;
    items.forEach((it, i) => {
      const x = inX + i * (cw + g);
      rect({ x, y, w: cw, h, r: 0.03, fill: C.CARDF, line: { color: C.BORD, width: 0.6 } });
      text({ x, y: y + 0.05, w: cw, h: 0.20, align: "center", runs: [{ t: it.t, font: FONT, size: 9, bold: true, color: C.CARDT }] });
      text({ x, y: y + h - 0.22, w: cw, h: 0.18, align: "center", runs: [{ t: it.s, font: FONT, size: 7.3, color: C.SUB }] });
    });
  };

  // ① 统一调度层
  sect(2.62, "①", "统一调度层", "Scheduling");
  cards([
    { t: "任务编排", s: "多任务并行" }, { t: "优先级调度", s: "SLA 分级" }, { t: "路由分配", s: "最优匹配" },
    { t: "限流降级", s: "峰值保护" }, { t: "异常熔断", s: "失败重试" }, { t: "执行监控", s: "时效预警" },
  ], 2.82, 0.42, 6);

  // ② 标准指令集（核心）
  sect(3.30, "②", "标准指令集（核心）", "Standard Instruction Set");
  cards([
    { t: "商品信息指令", s: "创建 · 修改" }, { t: "收货指令", s: "DWS 称重 · 提码" }, { t: "上架指令", s: "存储 · 返回库位" },
    { t: "盘点指令", s: "RFID · 物理盘" }, { t: "移库指令", s: "存储 · 返回库位" }, { t: "监控预警指令", s: "过程跟踪" },
  ], 3.50, 0.38, 6);
  cards([
    { t: "容器信息指令", s: "容器绑定 · 解绑" }, { t: "波次指令", s: "波次锁号 · 产能" }, { t: "拣货指令", s: "货架/货位/托盘到人" },
    { t: "分播指令", s: "格口/订单/门店" }, { t: "对账指令", s: "存储 · 返回库位" }, { t: "任务单看板指令", s: "数据回传" },
  ], 3.90, 0.38, 6);

  // ③ 设备能力适配层
  sect(4.36, "③", "设备能力适配层", "Capability Adapter");
  cards([
    { t: "货架到人适配", s: "PopPick 类" }, { t: "料箱到人适配", s: "Shuttle 类" }, { t: "托盘到人适配", s: "高位密存类" },
    { t: "分拣机器人适配", s: "柔性分拣类" }, { t: "通用设备适配", s: "AGV/RGV/输送线·机器人" },
  ], 4.56, 0.42, 5);

  // ===== VISUALIZATION panel =====
  const vinX = vizX + 0.20, vinW = vizW - 0.40;
  text({ x: vinX, y: 2.12, w: vinW, h: 0.30, runs: [{ t: "可视化平台", font: FONT, size: 13, bold: true, color: C.NAVY }] });
  const viz = [
    { t: "全仓任务看板", s: "全仓任务 · 看板" }, { t: "自动化区域监控", s: "自动化区任务监控" },
    { t: "指令执行看板", s: "指令时效 · 成功率" }, { t: "异常工单看板", s: "异常 / 重试 / 告警" },
    { t: "数字孪生", s: "仓内全要素映射" },
  ];
  viz.forEach((v, i) => {
    const y = 2.58 + i * 0.50;
    text({ x: vinX, y, w: vinW, h: 0.20, runs: [{ t: v.t, font: FONT, size: 10.5, bold: true, color: C.CARDT }] });
    text({ x: vinX, y: y + 0.20, w: vinW, h: 0.16, runs: [{ t: v.s, font: FONT, size: 8, color: C.SUB }] });
  });

  // ===== DOWNSTREAM =====
  text({ x: X0, y: 5.18, w: 7.2, h: 0.16, runs: [{ t: "下游 · 自动化供应商系统（按能力适配接入，可扩展）", font: FONT, size: 9, bold: true, color: C.SECT }] });
  text({ x: 7.0, y: 5.18, w: 5.99, h: 0.16, align: "right", runs: [{ t: "标准指令下发 · 执行状态上报，统一经 WCS 适配对接", font: FONT, size: 8, color: C.LBL }] });
  for (let i = 0; i < upN; i++) line({ x: ctr(i), y: 5.36, w: 0, h: 0.12, color: C.STEEL, width: 1, beginArrow: true, endArrow: true });

  const ds = [
    { t: "WCS1 · 货架到人", s: "PopPick · 全品类订单行", hi: false },
    { t: "WCS2 · 料箱到人", s: "RoboShuttle · 高密度垂直存储", hi: false },
    { t: "WCS3 · 料箱到人", s: "闪攀（海柔）· 高效拣选", hi: true },
    { t: "WCS4 · 托盘到人", s: "上架/下架 · 高密度存储", hi: false },
    { t: "WCS N · 分拣机器人", s: "柔性分拣 · 可横向扩展", hi: false },
  ];
  ds.forEach((d, i) => {
    rect({ x: colX(i), y: 5.52, w: upW, h: 0.56, r: 0.04, fill: d.hi ? C.REDF : C.WHITE, line: { color: d.hi ? C.RED : C.BORD, width: d.hi ? 1.1 : 0.75 } });
    text({ x: colX(i), y: 5.60, w: upW, h: 0.22, align: "center", runs: [{ t: d.t, font: FONT, size: 10.5, bold: true, color: C.NAVY }] });
    text({ x: colX(i), y: 5.83, w: upW, h: 0.18, align: "center", runs: [{ t: d.s, font: FONT, size: 8, color: d.hi ? C.RED : C.SUB }] });
  });

  // ===== EQUIPMENT CHIPS =====
  const chips = ["输送机", "外形检测机", "缠膜机", "堆垛机", "四向车", "AGV", "机器人", "工作站", "提升机", "无人叉车", "贴标机"];
  const cn = chips.length, cg = 0.10, chW = (CW - (cn - 1) * cg) / cn;
  chips.forEach((cText, i) => {
    const x = X0 + i * (chW + cg);
    rect({ x, y: 6.20, w: chW, h: 0.30, r: 0.05, fill: C.CHIP });
    text({ x, y: 6.20, w: chW, h: 0.30, align: "center", runs: [{ t: cText, font: FONT, size: 8, color: C.INK }] });
  });

  // ===== NOTE =====
  text({ x: X0, y: 6.62, w: CW, h: 0.5, valign: "top", runs: [{ t: "说明：WMS 与自动化供应商系统之间不直连，全部通过 WCS 标准指令集完成上下行交互；自研 WCS 承担调度引擎、指令协议与能力适配的核心职责，供应商系统作为可插拔执行体，按统一适配规范接入、可横向扩展替换。", font: FONT, size: 8, color: C.LBL }] });

  return ops;
}

module.exports = { CANVAS, C, FONT, FONT_EN, buildOps };
