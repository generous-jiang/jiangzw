#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the WCS architecture slide (single, fully-editable pptx page)."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
import copy

# ---------- palette ----------
RED_ACCENT   = RGBColor(0xE3, 0x3A, 0x2E)
DARK_BLUE    = RGBColor(0x1F, 0x4E, 0x79)
MED_BLUE     = RGBColor(0x2E, 0x75, 0xB6)
DEEP_BLUE    = RGBColor(0x16, 0x3A, 0x5C)
LIGHT_BLUE   = RGBColor(0xDC, 0xEA, 0xF8)
WCS_BG       = RGBColor(0xEE, 0xF5, 0xFC)
LAYER_BG_1   = RGBColor(0xDC, 0xEA, 0xF8)
LAYER_BG_2   = RGBColor(0xCF, 0xE3, 0xF7)
LAYER_BG_3   = RGBColor(0xDC, 0xEA, 0xF8)
CHIP_FILL_1  = RGBColor(0xFF, 0xFF, 0xFF)
CHIP_FILL_2  = RGBColor(0x2E, 0x75, 0xB6)
CHIP_FILL_3  = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_BORDER  = RGBColor(0xB8, 0xB8, 0xB8)
GRAY_FILL    = RGBColor(0xF3, 0xF3, 0xF3)
GRAY_TEXT    = RGBColor(0x6B, 0x6B, 0x6B)
TEXT_DARK    = RGBColor(0x24, 0x24, 0x24)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[6])

SW, SH = 13.333, 7.5
MX = 0.3
CW = SW - 2 * MX  # content width


def add_rect(x, y, w, h, fill=None, line=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE,
             dash=None, shadow=False):
    sp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
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


def set_text(sp, text, size=11, color=TEXT_DARK, bold=False, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE, font=FONT, line_spacing=1.0, wrap=True):
    tf = sp.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = Pt(2)
    tf.margin_right = Pt(2)
    tf.margin_top = Pt(1)
    tf.margin_bottom = Pt(1)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
    return tf


def add_textbox(x, y, w, h, text, size=11, color=TEXT_DARK, bold=False,
                 align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    set_text(tb, text, size=size, color=color, bold=bold, align=align, anchor=anchor, font=font)
    return tb


def add_double_arrow(x, y1, y2, color=DEEP_BLUE, weight=1.75):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(weight)
    ln = conn.line._get_or_add_ln()
    head = ln.makeelement(qn('a:headEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    tail = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    ln.append(head)
    ln.append(tail)
    return conn


# ---------------- Title ----------------
add_rect(MX, 0.16, 0.07, 0.42, fill=RED_ACCENT)
add_textbox(MX + 0.18, 0.13, 10.5, 0.48,
            "全渠道仓库自动化接入 WCS · 产品方案",
            size=24, bold=True, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)

add_textbox(MX + 0.18, 0.62, CW - 0.2, 0.34,
            "Flux WMS 与 WHC 自动化任务编排在上 · 自研 WCS 以标准指令集 + 能力分层实现统一调度 · 上下行均经 WCS 贯通到自动化设备",
            size=12, color=RGBColor(0x55, 0x55, 0x55), anchor=MSO_ANCHOR.MIDDLE)

# ---------------- Grid columns (shared by WMS row / arrows / vendor row) ----------------
N_COL = 5
GAP = 0.16
col_w = (CW - (N_COL - 1) * GAP) / N_COL
col_x = [MX + i * (col_w + GAP) for i in range(N_COL)]

wms_names = ["DC Flux WMS", "FC Flux WMS", "City DC WMS", "门店 WMS", "云仓 WMS"]
WMS_Y, WMS_H = 1.08, 0.62

for i, name in enumerate(wms_names):
    box = add_rect(col_x[i], WMS_Y, col_w, WMS_H, fill=WHITE, line=MED_BLUE, line_w=1.25,
                    shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    box.adjustments[0] = 0.12
    set_text(box, name, size=13, bold=True, color=DARK_BLUE)

add_textbox(MX, 1.08 - 0.30, 3.0, 0.26, "上游 · 多 WMS / WHC 系统", size=10.5, bold=True,
            color=MED_BLUE)

# ---------------- Arrow zone 1: WMS -> WCS ----------------
ARROW1_Y0, ARROW1_Y1 = WMS_Y + WMS_H + 0.03, 2.04
for i in range(N_COL):
    add_double_arrow(col_x[i] + col_w / 2, ARROW1_Y0, ARROW1_Y1)

add_textbox(col_x[1] + col_w * 0.3, ARROW1_Y0 - 0.02, col_w * 2.4, 0.3,
            "标准指令双向交互：下行指令 / 上行状态，全部经 WCS",
            size=9.5, color=GRAY_TEXT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ---------------- WCS container (dominant block) ----------------
WCS_Y, WCS_H = ARROW1_Y1, 3.62
wcs_box = add_rect(MX, WCS_Y, CW, WCS_H, fill=WCS_BG, line=MED_BLUE, line_w=1.5,
                    shape=MSO_SHAPE.ROUNDED_RECTANGLE)
wcs_box.adjustments[0] = 0.035

add_textbox(MX - 0.02, WCS_Y - 0.30, 3.4, 0.26, "WCS 平台（自研核心）", size=10.5, bold=True,
            color=DARK_BLUE)

side_w = CW * 0.205
main_w = CW - side_w - 0.18
main_x = MX + 0.16
side_x = main_x + main_w + 0.18

# header strap
hdr = add_rect(main_x, WCS_Y + 0.12, main_w, 0.40, fill=DARK_BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
hdr.adjustments[0] = 0.25
set_text(hdr, "WCS · 仓储自动化统一调度引擎  —  标准指令集 + 能力分层", size=13, bold=True, color=WHITE)

layers_top = WCS_Y + 0.12 + 0.40 + 0.10
layers_h_total = WCS_Y + WCS_H - 0.14 - layers_top
gap_l = 0.09
layer_h = (layers_h_total - 2 * gap_l) / 3

label_w = 1.55
chip_area_x = main_x + label_w + 0.10
chip_area_w = main_w - label_w - 0.10


def add_layer(y, label, sub, chips, label_fill, chip_fill, chip_text_color, chip_border):
    lab = add_rect(main_x, y, label_w, layer_h, fill=label_fill, line=MED_BLUE, line_w=1.0,
                    shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    lab.adjustments[0] = 0.10
    tf = lab.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label; r.font.size = Pt(12.5); r.font.bold = True
    r.font.color.rgb = DARK_BLUE; r.font.name = FONT
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run(); r2.text = sub; r2.font.size = Pt(8.5); r2.font.color.rgb = MED_BLUE
    r2.font.name = FONT

    n = len(chips)
    c_gap = 0.07
    c_w = (chip_area_w - (n - 1) * c_gap) / n
    for j, c in enumerate(chips):
        cx = chip_area_x + j * (c_w + c_gap)
        chip = add_rect(cx, y, c_w, layer_h, fill=chip_fill, line=chip_border, line_w=1.0,
                         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        chip.adjustments[0] = 0.14
        set_text(chip, c, size=9.5 if n <= 6 else 9, bold=(chip_fill == CHIP_FILL_2),
                 color=chip_text_color)


# Layer 1: unified scheduling
add_layer(layers_top, "统一调度层", "Scheduling",
          ["任务编排", "优先级调度", "路由分配", "异常熔断/降级", "执行监控"],
          LAYER_BG_1, CHIP_FILL_1, DARK_BLUE, MED_BLUE)

# Layer 2: standard instruction set (highlighted - the core ask)
y2 = layers_top + layer_h + gap_l
add_layer(y2, "标准指令集层", "Instruction Set",
          ["入库指令", "上架指令", "移库指令", "盘点指令", "补货指令", "拣选指令", "分播指令", "对账指令"],
          MED_BLUE, CHIP_FILL_2, WHITE, DARK_BLUE)

# Layer 3: device capability adaptation
y3 = y2 + layer_h + gap_l
add_layer(y3, "设备适配层", "Capability Adapter",
          ["货架到人适配", "料箱到人适配", "托盘到人适配", "分拣机器人适配", "通用设备适配\n(AGV/输送线/机器人)"],
          LAYER_BG_3, CHIP_FILL_3, DARK_BLUE, MED_BLUE)

# ---- side panel: 看板平台 ----
side_box = add_rect(side_x, WCS_Y + 0.12, side_w, layers_top + layers_h_total - (WCS_Y + 0.12),
                     fill=WHITE, line=MED_BLUE, line_w=1.0, dash="dash",
                     shape=MSO_SHAPE.ROUNDED_RECTANGLE)
side_box.adjustments[0] = 0.05
add_textbox(side_x, WCS_Y + 0.16, side_w, 0.26, "看板平台 · 可视化", size=11.5, bold=True,
            color=DARK_BLUE, align=PP_ALIGN.CENTER)
kanban_items = ["全仓任务看板", "自动化区域监控", "指令执行看板", "数字孪生"]
ky = WCS_Y + 0.50
k_gap = 0.08
k_h = (layers_h_total - 0.38 - 3 * k_gap) / 4
for it in kanban_items:
    kb = add_rect(side_x + 0.12, ky, side_w - 0.24, k_h, fill=LIGHT_BLUE, line=MED_BLUE, line_w=0.75,
                  shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    kb.adjustments[0] = 0.18
    set_text(kb, it, size=10, color=DARK_BLUE)
    ky += k_h + k_gap

# ---------------- Arrow zone 2: WCS -> Vendor systems ----------------
ARROW2_Y0, ARROW2_Y1 = WCS_Y + WCS_H + 0.03, WCS_Y + WCS_H + 0.03 + 0.32
for i in range(N_COL):
    add_double_arrow(col_x[i] + col_w / 2, ARROW2_Y0, ARROW2_Y1)

add_textbox(col_x[1] + col_w * 0.15, ARROW2_Y0 - 0.02, col_w * 2.7, 0.3,
            "标准指令下发 / 执行状态上报，统一经 WCS 适配对接",
            size=9.5, color=GRAY_TEXT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ---------------- Vendor systems row (de-emphasized / condensed) ----------------
VEND_Y, VEND_H = ARROW2_Y1, 0.92
vendors = [
    ("WCS1", "货架到人 · PopPick"),
    ("WCS2", "料箱到人 · RoboShuttle"),
    ("WCS3", "料箱到人 · 闪擎"),
    ("WCS4", "托盘到人 · 上架/下拣"),
    ("WCS N", "分拣机器人 · 柔性分拣"),
]
for i, (name, desc) in enumerate(vendors):
    vb = add_rect(col_x[i], VEND_Y, col_w, VEND_H, fill=GRAY_FILL, line=GRAY_BORDER, line_w=1.0,
                  shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    vb.adjustments[0] = 0.10
    tf = vb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = name; r.font.size = Pt(11); r.font.bold = True
    r.font.color.rgb = RGBColor(0x59, 0x59, 0x59); r.font.name = FONT
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run(); r2.text = desc; r2.font.size = Pt(8.5)
    r2.font.color.rgb = GRAY_TEXT; r2.font.name = FONT

add_textbox(MX, VEND_Y - 0.28, 4.6, 0.24, "下游 · 自动化供应商系统（按能力适配接入，可扩展）",
            size=10, bold=True, color=GRAY_TEXT)

add_textbox(MX, VEND_Y + VEND_H + 0.05, CW, 0.26,
            "说明：WMS 与自动化供应商系统之间不直连，全部通过 WCS 标准指令集完成上下行交互，体系以自研 WCS 调度与指令能力为核心，供应商系统仅作为可插拔的执行层。",
            size=9.5, color=GRAY_TEXT, align=PP_ALIGN.LEFT)

out_path = "/tmp/claude-0/-home-user-jiangzw/81f8bea8-81f5-5c3f-ac7d-956c9b48b841/scratchpad/WCS架构产品方案.pptx"
prs.save(out_path)
print("saved", out_path)
