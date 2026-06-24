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
N_COL = 5
GAP = 0.16
col_w = (CW - (N_COL - 1) * GAP) / N_COL
col_x = [MX + i * (col_w + GAP) for i in range(N_COL)]

# ---------------------------------------------------------------- WMS row -----
plain_text(MX, 0.96, 4.0, 0.22, "上游 · 多 WMS / WHC 系统", size=10, bold=True, color=LABEL_GRAY)
WMS_Y, WMS_H = 1.18, 0.58
wms_names = ["DC Flux WMS", "FC Flux WMS", "City DC WMS", "门店 WMS", "云仓 WMS"]
for i, name in enumerate(wms_names):
    box = add_rect(col_x[i], WMS_Y, col_w, WMS_H, fill=WHITE, line=BORDER_BLUE, line_w=1.0,
                    round_adj=0.05)
    plain_text(col_x[i], WMS_Y + 0.08, col_w, 0.24, name, size=12.5, bold=True, color=DARK_BLUE,
               align=PP_ALIGN.CENTER)
    add_rect(col_x[i] + col_w * 0.18, WMS_Y + 0.34, col_w * 0.64, 0.018, fill=MED_BLUE,
             shape=MSO_SHAPE.RECTANGLE)

# ---------------------------------------------------------- arrow zone 1 ------
A1_Y0, A1_Y1 = WMS_Y + WMS_H + 0.03, 2.05
for i in range(N_COL):
    thin_arrow(col_x[i] + col_w / 2, A1_Y0, A1_Y1)
plain_text(col_x[1] + col_w * 0.25, A1_Y0 - 0.01, col_w * 2.5, 0.26,
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

# ---------------------------------------------------------- arrow zone 2 ------
A2_Y0, A2_Y1 = WCS_Y + WCS_H + 0.03, WCS_Y + WCS_H + 0.03 + 0.28
for i in range(N_COL):
    thin_arrow(col_x[i] + col_w / 2, A2_Y0, A2_Y1)
plain_text(col_x[1] + col_w * 0.10, A2_Y0 - 0.01, col_w * 2.8, 0.26,
           "标准指令下发 / 执行状态上报，统一经 WCS 适配对接",
           size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ------------------------------------------------------- vendor systems row ---
VEND_Y = A2_Y1
VEND_H = 0.74
plain_text(MX, VEND_Y - 0.24, 6.0, 0.22, "下游 · 自动化供应商系统（按能力适配接入，可扩展）",
           size=10, bold=True, color=LABEL_GRAY)
vendors = [
    ("WCS1 · 货架到人", "PopPick · 全品类订单单行"),
    ("WCS2 · 料箱到人", "RoboShuttle · 高密垂直存储"),
    ("WCS3 · 料箱到人", "闪擎 · 高效拣选"),
    ("WCS4 · 托盘到人", "上架/下拣 · 高密存储"),
    ("WCS N · 分拣机器人", "柔性分拣 · 可横向扩展"),
]
for i, (name, desc) in enumerate(vendors):
    vb = add_rect(col_x[i], VEND_Y, col_w, VEND_H, fill=WHITE, line=BORDER_GRAY, line_w=1.0,
                  round_adj=0.05)
    plain_text(col_x[i] + 0.08, VEND_Y + 0.07, col_w - 0.16, 0.22, name, size=10.5, bold=True,
               color=DARK_BLUE, align=PP_ALIGN.CENTER)
    add_rect(col_x[i] + col_w * 0.18, VEND_Y + 0.30, col_w * 0.64, 0.015, fill=BORDER_GRAY,
             shape=MSO_SHAPE.RECTANGLE)
    plain_text(col_x[i] + 0.08, VEND_Y + 0.36, col_w - 0.16, 0.32, desc, size=8.5, color=TEXT_GRAY,
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

out_path = "/tmp/claude-0/-home-user-jiangzw/81f8bea8-81f5-5c3f-ac7d-956c9b48b841/scratchpad/WCS架构产品方案.pptx"
prs.save(out_path)
print("saved", out_path)
