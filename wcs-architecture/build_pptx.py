#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the WCS architecture slide (single, fully-editable pptx page).

Visual style mirrors the original deck (clean white cards, thin borders,
blue header bars, dashed platform containers). Core framework: WMS row ->
(bidirectional, WCS-only) -> WCS platform (scheduling / standard
instruction-set / device-adapter layers + visualization side panel) ->
(bidirectional, WCS-only) -> automation vendor systems row.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn

# ---------- palette (matches original: white cards, thin gray-blue borders, blue headers) ----------
RED_ACCENT   = RGBColor(0xE3, 0x3A, 0x2E)
DARK_BLUE    = RGBColor(0x1F, 0x4E, 0x79)
MED_BLUE     = RGBColor(0x2E, 0x75, 0xB6)
BORDER_BLUE  = RGBColor(0x9F, 0xB7, 0xD4)
BORDER_GRAY  = RGBColor(0xC9, 0xC9, 0xC9)
CHIP_FILL    = RGBColor(0xFB, 0xFC, 0xFE)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK    = RGBColor(0x26, 0x26, 0x26)
TEXT_GRAY    = RGBColor(0x7A, 0x7A, 0x7A)
LABEL_GRAY   = RGBColor(0x59, 0x59, 0x59)

FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[6])

SW, SH = 13.333, 7.5
MX = 0.3
CW = SW - 2 * MX


def add_rect(x, y, w, h, fill=None, line=None, line_w=1.0, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
             dash=None, round_adj=0.045):
    sp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sp.adjustments[0] = round_adj
        except Exception:
            pass
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(line_w)
        if dash:
            ln = sp.line._get_or_add_ln()
            d = ln.makeelement(qn('a:prstDash'), {'val': dash})
            ln.append(d)
    sp.shadow.inherit = False
    return sp


def text_card(sp, title, sub=None, title_size=11, sub_size=8.5, title_color=TEXT_DARK,
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, bold_title=True):
    tf = sp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_top = Pt(1); tf.margin_bottom = Pt(1); tf.margin_left = Pt(2); tf.margin_right = Pt(2)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run(); r.text = title; r.font.size = Pt(title_size); r.font.bold = bold_title
    r.font.color.rgb = title_color; r.font.name = FONT
    if sub:
        for seg in sub.split("\n"):
            pp = tf.add_paragraph()
            pp.alignment = align
            rr = pp.add_run(); rr.text = seg; rr.font.size = Pt(sub_size)
            rr.font.color.rgb = TEXT_GRAY; rr.font.name = FONT
    return sp


def plain_text(x, y, w, h, text, size=10.5, color=TEXT_DARK, bold=False,
               align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Pt(0); tf.margin_right = Pt(0); tf.margin_top = Pt(0); tf.margin_bottom = Pt(0)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = bold
    r.font.italic = italic; r.font.color.rgb = color; r.font.name = font
    return tb


def thin_arrow(x, y1, y2, color=RGBColor(0x8C, 0x9B, 0xB3), weight=1.0):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(weight)
    ln = conn.line._get_or_add_ln()
    ln.append(ln.makeelement(qn('a:headEnd'), {'type': 'triangle', 'w': 'sm', 'len': 'sm'}))
    ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'sm', 'len': 'sm'}))
    return conn


# ============================================================= Title =====
add_rect(MX, 0.16, 0.07, 0.40, fill=RED_ACCENT, shape=MSO_SHAPE.RECTANGLE)
plain_text(MX + 0.18, 0.12, 10.6, 0.48, "全渠道仓库自动化接入 WCS · 产品方案",
           size=23, bold=True, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)
plain_text(MX + 0.18, 0.60, CW - 0.2, 0.32,
           "Flux WMS 与 WHC 自动化任务编排在上，自研 WCS 以标准指令集统一下发、按能力分层调度自动化设备；上下行交互均经 WCS 贯通衔接",
           size=11.5, color=TEXT_GRAY, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================= grid columns ===
GAP = 0.16

# ---------------------------------------------------------------- WMS row -----
plain_text(MX, 0.96, 7.0, 0.22, "业务决策层 · WMS（上游多源系统接入）", size=10, bold=True, color=LABEL_GRAY)
WMS_Y, WMS_H = 1.18, 0.58
GROUP_PAD_X = 0.08
CARD_GAP = 0.05
GROUP_GAP = 0.18

wms_groups = [
    ("供应链 WMS", [
        ("DC Flux WMS", ["DC"]),
        ("FC Flux WMS", ["CDC"]),
        ("City DC Flux WMS", ["FWDC", "FC", "CBEC"]),
    ]),
    ("门店域 WMS", [
        ("门店 WMS", ["门店"]),
        ("云仓 WMS", ["云仓", "社区店", "Darkstore"]),
    ]),
]


def slot_weight(subs):
    return 1.3 if len(subs) <= 1 else 1.3 + 0.55 * (len(subs) - 1)


group_card_weights = [[slot_weight(subs) for _, subs in items] for _, items in wms_groups]
group_raw_w = [sum(w) + (len(w) - 1) * CARD_GAP + 2 * GROUP_PAD_X for w in group_card_weights]
raw_total = sum(group_raw_w) + (len(wms_groups) - 1) * GROUP_GAP
wms_scale = CW / raw_total

card_y = WMS_Y + 0.07
card_h = WMS_H - 0.14
wms_arrow_x = []
gx = MX
for gi, (glabel, items) in enumerate(wms_groups):
    gw = group_raw_w[gi] * wms_scale
    plain_text(gx + 0.02, WMS_Y - 0.22, 3.0, 0.18, glabel, size=9, bold=True, color=LABEL_GRAY)
    add_rect(gx, WMS_Y, gw, WMS_H, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_BLUE, line_w=1.0,
             dash="dash", round_adj=0.05)
    cx = gx + GROUP_PAD_X * wms_scale
    for ci, (name, subs) in enumerate(items):
        cw = group_card_weights[gi][ci] * wms_scale
        add_rect(cx, card_y, cw, card_h, fill=WHITE, line=BORDER_BLUE, line_w=1.0, round_adj=0.07)
        plain_text(cx, card_y + 0.04, cw, 0.20, name, size=11 if cw < 2.2 else 12, bold=True,
                   color=DARK_BLUE, align=PP_ALIGN.CENTER)
        add_rect(cx + cw * 0.18, card_y + 0.245, cw * 0.64, 0.016, fill=MED_BLUE,
                 shape=MSO_SHAPE.RECTANGLE)
        plain_text(cx + 0.02, card_y + 0.27, cw - 0.04, 0.17, " / ".join(subs), size=7.5,
                   color=TEXT_GRAY, align=PP_ALIGN.CENTER)
        wms_arrow_x.append(cx + cw / 2)
        cx += cw + CARD_GAP * wms_scale
    gx += gw + GROUP_GAP * wms_scale

# ---------------------------------------------------------- arrow zone 1 ------
A1_Y0, A1_Y1 = WMS_Y + WMS_H + 0.03, 2.05
for x in wms_arrow_x:
    thin_arrow(x, A1_Y0, A1_Y1)
plain_text(MX + CW * 0.30, A1_Y0 - 0.01, CW * 0.40, 0.26,
           "标准指令双向交互：下行指令 / 上行状态，统一经 WCS",
           size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================ WCS platform ===
WCS_Y = A1_Y1
WCS_H = 3.55
plain_text(MX, WCS_Y - 0.24, 2.6, 0.22, "WCS 平台", size=10, color=LABEL_GRAY)
wcs_outer = add_rect(MX, WCS_Y, CW, WCS_H, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_BLUE,
                      line_w=1.0, dash="dash", round_adj=0.02)

side_w = CW * 0.205
main_w = CW - side_w - 0.18
main_x = MX + 0.16
side_x = main_x + main_w + 0.18
pad_top = WCS_Y + 0.13

# header bar
HDR_H = 0.52
hdr = add_rect(main_x, pad_top, main_w, HDR_H, fill=DARK_BLUE, round_adj=0.10)
tf = hdr.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_top = Pt(1); tf.margin_bottom = Pt(1)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
r = p.add_run(); r.text = "WCS · 仓储自动化统一调度引擎"; r.font.size = Pt(13.5); r.font.bold = True
r.font.color.rgb = WHITE; r.font.name = FONT
p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
r2 = p2.add_run()
r2.text = "标准指令协议：版本化管理 · 幂等重试 · 灰度发布 · 限流降级"
r2.font.size = Pt(9); r2.font.color.rgb = RGBColor(0xCF, 0xE0, 0xF3); r2.font.name = FONT

layers_top = pad_top + HDR_H + 0.10
layers_bottom = WCS_Y + WCS_H - 0.13
layers_h_total = layers_bottom - layers_top
gap_l = 0.08

# layer weighting: scheduling(1) : instruction-set(2 rows -> weight 2) : device-adapter(1)
w1, w2, w3 = 1.0, 1.7, 1.0
unit = (layers_h_total - 2 * gap_l) / (w1 + w2 + w3)
h1, h2, h3 = unit * w1, unit * w2, unit * w3

TITLE_H = 0.20


def layer_block(y, h, title_en, title_cn, rows):
    """rows: list of row -> list of (name, sub)"""
    plain_text(main_x, y, main_w, TITLE_H, f"{title_cn}", size=10.5, bold=True, color=DARK_BLUE)
    plain_text(main_x + main_w - 1.9, y, 1.9, TITLE_H, title_en, size=8.5, color=TEXT_GRAY,
               align=PP_ALIGN.RIGHT)
    grid_y = y + TITLE_H + 0.03
    grid_h = h - TITLE_H - 0.03
    n_rows = len(rows)
    r_gap = 0.035
    row_h = (grid_h - (n_rows - 1) * r_gap) / n_rows
    for ridx, row in enumerate(rows):
        ry = grid_y + ridx * (row_h + r_gap)
        n = len(row)
        c_gap = 0.035
        c_w = (main_w - (n - 1) * c_gap) / n
        for cidx, (name, sub) in enumerate(row):
            cx = main_x + cidx * (c_w + c_gap)
            chip = add_rect(cx, ry, c_w, row_h, fill=CHIP_FILL, line=BORDER_GRAY, line_w=0.75,
                             round_adj=0.06)
            text_card(chip, name, sub, title_size=9.5, sub_size=8, title_color=TEXT_DARK)


y1 = layers_top
layer_block(y1, h1, "Scheduling", "① 统一调度层", [
    [("任务编排", "多任务并行"), ("优先级调度", "SLA分级"), ("路由分配", "最优匹配"),
     ("限流降级", "峰值保护"), ("异常熔断", "失败重试"), ("执行监控", "时效预警")],
])

y2 = y1 + h1 + gap_l
layer_block(y2, h2, "Standard Instruction Set", "② 标准指令集层（核心）", [
    [("商品信息指令", "创建·修改"), ("收货指令", "DWS称重·提码"), ("上架指令", "存储·返回库位"),
     ("盘点指令", "RFID·物理盘"), ("移库指令", "存储·返回库位"), ("监控预警指令", "过程跟踪")],
    [("容器信息指令", "容器绑定·解绑"), ("波次指令", "波次旗号·产能"), ("拣货指令", "货架/货位/托盘到人"),
     ("分播指令", "格口/订单/门店"), ("对账指令", "存储·返回库位"), ("任务单看板指令", "数据回传")],
])

y3 = y2 + h2 + gap_l
layer_block(y3, h3, "Capability Adapter", "③ 设备能力适配层", [
    [("货架到人适配", "PopPick类"), ("料箱到人适配", "Shuttle类"), ("托盘到人适配", "高位密存类"),
     ("分拣机器人适配", "柔性分拣类"), ("语音适配拣选", "语音引导·免视觉"),
     ("通用设备适配", "AGV/RGV/输送线/机器人")],
])

# ---- side panel: 可视化平台 ----
plain_text(side_x, WCS_Y - 0.24, side_w, 0.22, "看板平台", size=10, color=LABEL_GRAY)
side_box = add_rect(side_x, pad_top, side_w, layers_bottom - pad_top, fill=WHITE, line=BORDER_BLUE,
                     line_w=1.0, dash="dash", round_adj=0.04)
plain_text(side_x + 0.14, pad_top + 0.10, side_w - 0.28, 0.26, "可视化平台", size=12, bold=True,
           color=DARK_BLUE)
kanban_items = [
    ("全仓任务看板", "全仓任务 · 看板"),
    ("自动化区域监控", "自动化区任务监控"),
    ("指令执行看板", "指令时效 · 成功率"),
    ("设备监控层", "设备状态 · 能耗 · 故障预警"),
    ("异常工单看板", "异常 / 重试 / 告警"),
    ("数字孪生", "仓内全要素映射"),
]
ky = pad_top + 0.46
k_h = (layers_bottom - ky - 0.06) / len(kanban_items)
for name, sub in kanban_items:
    plain_text(side_x + 0.16, ky, side_w - 0.30, k_h * 0.55, name, size=10, bold=True, color=TEXT_DARK)
    plain_text(side_x + 0.16, ky + k_h * 0.50, side_w - 0.30, k_h * 0.45, sub, size=8, color=TEXT_GRAY)
    if name != kanban_items[-1][0]:
        add_rect(side_x + 0.14, ky + k_h - 0.02, side_w - 0.28, 0.012, fill=RGBColor(0xE3, 0xE7, 0xEC),
                 shape=MSO_SHAPE.RECTANGLE)
    ky += k_h

# ------------------------------------------------------- vendor systems row ---
VEND_Y_BASE = WCS_Y + WCS_H + 0.03
vendors = [
    ("WCS1 · 货架到人", "PopPick · 全品类订单单行"),
    ("WCS2 · 料箱到人", "RoboShuttle · 高密垂直存储"),
    ("WCS3 · 料箱到人", "闪擎 · 高效拣选"),
    ("WCS4 · 托盘到人", "上架/下拣 · 高密存储"),
    ("WCS5 · 语音拣选", "语音终端 · 免视觉拣选"),
    ("WCS N · 分拣机器人", "柔性分拣 · 可横向扩展"),
]
N_VEND = len(vendors)
vend_col_w = (CW - (N_VEND - 1) * GAP) / N_VEND
vend_col_x = [MX + i * (vend_col_w + GAP) for i in range(N_VEND)]

# ---------------------------------------------------------- arrow zone 2 ------
A2_Y0, A2_Y1 = VEND_Y_BASE, VEND_Y_BASE + 0.28
for i in range(N_VEND):
    thin_arrow(vend_col_x[i] + vend_col_w / 2, A2_Y0, A2_Y1)
plain_text(vend_col_x[1] + vend_col_w * 0.10, A2_Y0 - 0.01, vend_col_w * 3.2, 0.26,
           "标准指令下发 / 执行状态上报，统一经 WCS 适配对接",
           size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

VEND_Y = A2_Y1
VEND_H = 0.74
plain_text(MX, VEND_Y - 0.24, 6.0, 0.22, "下游 · 自动化供应商系统（按能力适配接入，可扩展）",
           size=10, bold=True, color=LABEL_GRAY)
for i, (name, desc) in enumerate(vendors):
    vb = add_rect(vend_col_x[i], VEND_Y, vend_col_w, VEND_H, fill=WHITE, line=BORDER_GRAY, line_w=1.0,
                  round_adj=0.05)
    plain_text(vend_col_x[i] + 0.06, VEND_Y + 0.07, vend_col_w - 0.12, 0.22, name, size=10, bold=True,
               color=DARK_BLUE, align=PP_ALIGN.CENTER)
    add_rect(vend_col_x[i] + vend_col_w * 0.18, VEND_Y + 0.30, vend_col_w * 0.64, 0.015, fill=BORDER_GRAY,
             shape=MSO_SHAPE.RECTANGLE)
    plain_text(vend_col_x[i] + 0.06, VEND_Y + 0.36, vend_col_w - 0.12, 0.32, desc, size=8, color=TEXT_GRAY,
               align=PP_ALIGN.CENTER)

# device-type tag strip (compact, single line, de-emphasized)
TAG_Y = VEND_Y + VEND_H + 0.08
device_types = ["输送机", "外形检测机", "缠膜机", "堆垛机", "四向车", "AGV", "机器人",
                 "工作站", "提升机", "无人叉车", "贴标机"]
n_tags = len(device_types)
tag_gap = 0.06
tag_w = (CW - (n_tags - 1) * tag_gap) / n_tags
for i, t in enumerate(device_types):
    tx = MX + i * (tag_w + tag_gap)
    tag = add_rect(tx, TAG_Y, tag_w, 0.26, fill=RGBColor(0xF5, 0xF6, 0xF7), line=BORDER_GRAY,
                   line_w=0.5, round_adj=0.18)
    plain_text(tx, TAG_Y, tag_w, 0.26, t, size=8, color=LABEL_GRAY, align=PP_ALIGN.CENTER,
               anchor=MSO_ANCHOR.MIDDLE)

FOOT_Y = TAG_Y + 0.26 + 0.08
plain_text(MX, FOOT_Y, CW, 0.28,
           "说明：WMS 与自动化供应商系统之间不直连，全部通过 WCS 标准指令集完成上下行交互；自研 WCS 承担调度引擎、指令协议与能力适配的核心职责，"
           "供应商系统作为可插拔执行层，按统一适配规范接入、可横向扩展替换。",
           size=9, color=TEXT_GRAY, align=PP_ALIGN.LEFT)

# ===================================================================== #
# ================= Slide 2: WCS internal architecture =================
# ===================================================================== #
slide = prs.slides.add_slide(prs.slide_layouts[6])


def dashed_arrow(x, y1, y2, bidir=False, color=RGBColor(0x8C, 0x9B, 0xB3), weight=1.0):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(weight)
    ln = conn.line._get_or_add_ln()
    ln.append(ln.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    if bidir:
        ln.append(ln.makeelement(qn('a:headEnd'), {'type': 'triangle', 'w': 'sm', 'len': 'sm'}))
    ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'sm', 'len': 'sm'}))
    return conn


def rail_bar(y, h, label, fill):
    add_rect(MX, y, RAIL_W, h, fill=fill, round_adj=0.10)
    plain_text(MX, y, RAIL_W, h, label, size=11.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
               anchor=MSO_ANCHOR.MIDDLE)


def sub_panel(x, y, w, h, title_cn, title_en, rows):
    """rows: list of row -> list of plain chip-name strings (a 1-item row spans full width)."""
    add_rect(x, y, w, h, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_GRAY, line_w=1.0, dash="dash",
             round_adj=0.03)
    pad = 0.10
    plain_text(x + pad, y + 0.06, w - 2 * pad, 0.18, title_cn, size=9.5, bold=True, color=DARK_BLUE)
    plain_text(x + pad, y + 0.06, w - 2 * pad, 0.18, title_en, size=7.5, color=TEXT_GRAY,
               align=PP_ALIGN.RIGHT)
    grid_y = y + 0.30
    grid_h = h - 0.30 - pad * 0.6
    n_rows = len(rows)
    r_gap = 0.04
    row_h = (grid_h - (n_rows - 1) * r_gap) / n_rows
    for ridx, row in enumerate(rows):
        ry = grid_y + ridx * (row_h + r_gap)
        n = len(row)
        c_gap = 0.04
        c_w = (w - 2 * pad - (n - 1) * c_gap) / n
        for cidx, name in enumerate(row):
            cx = x + pad + cidx * (c_w + c_gap)
            chip = add_rect(cx, ry, c_w, row_h, fill=CHIP_FILL, line=BORDER_GRAY, line_w=0.75,
                             round_adj=0.10)
            text_card(chip, name, None, title_size=8.5, title_color=TEXT_DARK, bold_title=False)


# ----------------------------------------------------------------- title -----
add_rect(MX, 0.16, 0.07, 0.40, fill=RED_ACCENT, shape=MSO_SHAPE.RECTANGLE)
plain_text(MX + 0.18, 0.12, 10.6, 0.48, "WCS 核心架构 · 服务能力分解",
           size=23, bold=True, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)
plain_text(MX + 0.18, 0.60, CW - 0.2, 0.32,
           "wcs-core 承接 WMS 标准指令并统一调度，向下按场景适配 / 厂商对接 / 调度策略下发执行；"
           "wcs-dashboard 独立完成运行数据的采集、加工与可视化展示",
           size=11.5, color=TEXT_GRAY, anchor=MSO_ANCHOR.MIDDLE)

# ----------------------------------------------------------- layout bands ----
RAIL_W = 0.62
CX0 = MX + RAIL_W + 0.14
MCW = CW - RAIL_W - 0.14

WMS2_Y, WMS2_H = 1.05, 0.55
GAP1_Y0, GAP1_Y1 = WMS2_Y + WMS2_H, WMS2_Y + WMS2_H + 0.30
WCS2_Y = GAP1_Y1
WCS2_H = 4.5
GAP2_Y0, GAP2_Y1 = WCS2_Y + WCS2_H, WCS2_Y + WCS2_H + 0.25
DEVICE2_Y, DEVICE2_H = GAP2_Y1, 0.50

rail_bar(WMS2_Y, WMS2_H, "WMS", DARK_BLUE)
rail_bar(WCS2_Y, WCS2_H, "WCS", MED_BLUE)
rail_bar(DEVICE2_Y, DEVICE2_H, "DEVICE", DARK_BLUE)

# --------------------------------------------------------------- WMS band ----
wms2_gap = 0.18
wms2_w = (MCW - wms2_gap) / 2
wms2_names = ["Flux WMS", "飞云 WMS"]
for i, name in enumerate(wms2_names):
    bx = CX0 + i * (wms2_w + wms2_gap)
    add_rect(bx, WMS2_Y, wms2_w, WMS2_H, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_GRAY, line_w=1.0,
             dash="dash", round_adj=0.04)
    plain_text(bx, WMS2_Y, wms2_w, WMS2_H, name, size=13, bold=True, color=DARK_BLUE,
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------- arrow zone 1 ----
dashed_arrow(CX0 + wms2_w * 0.5, GAP1_Y0, GAP1_Y1)
dashed_arrow(CX0 + wms2_w * 1.5 + wms2_gap, GAP1_Y0, GAP1_Y1)
plain_text(CX0 + wms2_w * 0.55, GAP1_Y0 + 0.02, 1.6, 0.2, "同步", size=9, color=TEXT_GRAY)

# --------------------------------------------------------------- WCS band ----
wcs_chunk_gap = 0.18
core_w = MCW * 0.665
dash_w = MCW - core_w - wcs_chunk_gap
core_x = CX0
dash_x = core_x + core_w + wcs_chunk_gap

add_rect(core_x, WCS2_Y, core_w, WCS2_H, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_BLUE, line_w=1.0,
         dash="dash", round_adj=0.02)
add_rect(dash_x, WCS2_Y, dash_w, WCS2_H, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_BLUE, line_w=1.0,
         dash="dash", round_adj=0.02)

plain_text(core_x + 0.14, WCS2_Y + 0.08, core_w - 1.6, 0.22, "自动化设备调度服务", size=12, bold=True,
           color=DARK_BLUE)
plain_text(core_x + core_w - 1.7, WCS2_Y + 0.08, 1.56, 0.22, "wcs-core", size=9, color=TEXT_GRAY,
           align=PP_ALIGN.RIGHT)

dash_hdr = slide.shapes.add_textbox(Inches(dash_x), Inches(WCS2_Y + 0.06), Inches(dash_w), Inches(0.40))
dtf = dash_hdr.text_frame
dtf.word_wrap = True
dtf.margin_left = Pt(0); dtf.margin_right = Pt(0); dtf.margin_top = Pt(0); dtf.margin_bottom = Pt(0)
dp1 = dtf.paragraphs[0]; dp1.alignment = PP_ALIGN.CENTER
dr1 = dp1.add_run(); dr1.text = "自动化设备可视化看板"; dr1.font.size = Pt(12); dr1.font.bold = True
dr1.font.color.rgb = DARK_BLUE; dr1.font.name = FONT
dp2 = dtf.add_paragraph(); dp2.alignment = PP_ALIGN.CENTER
dr2 = dp2.add_run(); dr2.text = "(wcs-dashboard)"; dr2.font.size = Pt(9); dr2.font.color.rgb = TEXT_GRAY
dr2.font.name = FONT

# core chunk: top pair (instruction / schedule) + bottom trio (scenario / integration / strategy)
core_pad = 0.12
core_top_y = WCS2_Y + 0.38
core_avail_h = WCS2_H - 0.38 - 0.10
top_h = (core_avail_h - 0.10) * 0.54
bottom_h = (core_avail_h - 0.10) - top_h
bottom_y = core_top_y + top_h + 0.10

top_avail_w = core_w - 2 * core_pad
subA_w = (top_avail_w - 0.14) * 3 / 5
subB_w = (top_avail_w - 0.14) * 2 / 5
subA_x = core_x + core_pad
subB_x = subA_x + subA_w + 0.14

sub_panel(subA_x, core_top_y, subA_w, top_h, "标准指令", "wcs-instruction", [
    ["商品信息", "收货", "分拣"],
    ["容器操作", "上架", "对账"],
    ["波次", "盘点", "补货"],
    ["拣货", "移库", "调整"],
])
sub_panel(subB_x, core_top_y, subB_w, top_h, "指令调度", "wcs-schedule", [
    ["指令编排", "优先调度"],
    ["限流降级", "熔断重试"],
    ["运行监控", "运行记录"],
    ["结果回传", "路由分配"],
])

bottom_avail_w = core_w - 2 * core_pad
subE_w = (bottom_avail_w - 2 * 0.12) * 2 / 5
subF_w = (bottom_avail_w - 2 * 0.12) * 2 / 5
subG_w = (bottom_avail_w - 2 * 0.12) * 1 / 5
subE_x = core_x + core_pad
subF_x = subE_x + subE_w + 0.12
subG_x = subF_x + subF_w + 0.12

sub_panel(subE_x, bottom_y, subE_w, bottom_h, "设备场景适配", "wcs-scenario", [
    ["货架到人", "料箱到人"],
    ["托盘到人", "分拣机器人"],
    ["语音拣选", "打包贴标"],
    ["通用设备适配"],
])
sub_panel(subF_x, bottom_y, subF_w, bottom_h, "设备厂商对接", "wcs-integration", [
    ["SDK对接", "数据映射适配"],
    ["设备管理", "执行日志"],
    ["传输协议适配"],
])
sub_panel(subG_x, bottom_y, subG_w, bottom_h, "调度策略", "wcs-strategy", [
    ["规则配置"],
    ["规则策略"],
    ["算法策略"],
])

# dashboard chunk: acquisition / visualization, side by side, full remaining height
dash_pad = 0.12
dash_top_y = WCS2_Y + 0.54
dash_avail_h = WCS2_H - 0.54 - 0.10
dash_avail_w = dash_w - 2 * dash_pad
subC_w = subD_w = (dash_avail_w - 0.14) / 2
subC_x = dash_x + dash_pad
subD_x = subC_x + subC_w + 0.14

sub_panel(subC_x, dash_top_y, subC_w, dash_avail_h, "数据采集传输", "wcs-acquisition", [
    ["异步消费"], ["定时采集"], ["数据标准化"], ["投递数据湖"],
])
sub_panel(subD_x, dash_top_y, subD_w, dash_avail_h, "可视化展示", "wcs-visualization", [
    ["数据展示"], ["数据分析"], ["数据加工"], ["数据源管理"],
])

# ---------------------------------------------------------- arrow zone 2 ----
dashed_arrow(core_x + core_w * 0.5, GAP2_Y0, GAP2_Y1, bidir=True)
plain_text(core_x + core_w * 0.5 + 0.10, GAP2_Y0 + 0.02, 1.0, 0.2, "同步", size=9, color=TEXT_GRAY)
dashed_arrow(dash_x + dash_w * 0.5, GAP2_Y0, GAP2_Y1, bidir=True)
plain_text(dash_x + dash_w * 0.5 + 0.10, GAP2_Y0 + 0.02, 1.0, 0.2, "异步", size=9, color=TEXT_GRAY)

# ------------------------------------------------------------ DEVICE band ----
add_rect(CX0, DEVICE2_Y, MCW, DEVICE2_H, fill=RGBColor(0xFC, 0xFD, 0xFE), line=BORDER_GRAY, line_w=1.0,
         dash="dash", round_adj=0.06)
n_tags2 = len(device_types)
tag2_gap = 0.08
tag2_pad = 0.10
tag2_w = (MCW - 2 * tag2_pad - (n_tags2 - 1) * tag2_gap) / n_tags2
for i, t in enumerate(device_types):
    tx = CX0 + tag2_pad + i * (tag2_w + tag2_gap)
    add_rect(tx, DEVICE2_Y + 0.09, tag2_w, DEVICE2_H - 0.18, fill=CHIP_FILL, line=BORDER_BLUE, line_w=0.75,
             round_adj=0.16)
    plain_text(tx, DEVICE2_Y + 0.09, tag2_w, DEVICE2_H - 0.18, t, size=8, bold=True, color=DARK_BLUE,
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

FOOT2_Y = DEVICE2_Y + DEVICE2_H + 0.07
plain_text(MX, FOOT2_Y, CW, 0.24,
           "说明：wcs-core 以标准指令承接上行 WMS 指令并统一调度，按场景适配 / 厂商对接 / 调度策略下发执行；"
           "wcs-dashboard 独立采集、加工并展示运行数据，分别通过同步 / 异步通路与执行层交互。",
           size=9, color=TEXT_GRAY, align=PP_ALIGN.LEFT)

out_path = "/tmp/claude-0/-home-user-jiangzw/81f8bea8-81f5-5c3f-ac7d-956c9b48b841/scratchpad/WCS架构产品方案.pptx"
prs.save(out_path)
print("saved", out_path)
