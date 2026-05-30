# -*- coding: utf-8 -*-
"""
WHC（仓库调度平台）平台化规划方案 - 可编辑 PPTX 生成脚本
风格：深蓝科技风 / 中文 / 混合版（战略 + 技术）
依赖：python-pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn

# ----------------------------------------------------------------------------
# 主题色板（深蓝科技风）
# ----------------------------------------------------------------------------
NAVY   = RGBColor(0x0E, 0x24, 0x46)   # 主背景深蓝
NAVY2  = RGBColor(0x12, 0x33, 0x60)   # 次深蓝
BLUE   = RGBColor(0x1C, 0x5B, 0xA8)   # 主蓝
BLUE2  = RGBColor(0x2E, 0x77, 0xC9)   # 亮蓝
CYAN   = RGBColor(0x16, 0xB4, 0xE8)   # 青
TEAL   = RGBColor(0x18, 0xC2, 0xA6)   # 蓝绿
AMBER  = RGBColor(0xF5, 0xA6, 0x23)   # 琥珀（强调）
CORAL  = RGBColor(0xE8, 0x51, 0x6A)   # 珊瑚红（风险/痛点）
VIOLET = RGBColor(0x8A, 0x6B, 0xE0)   # 紫
INDIGO = RGBColor(0x44, 0x5B, 0xC4)   # 靛蓝
ROSE   = RGBColor(0xE5, 0x6E, 0x9B)   # 玫红

LIGHT  = RGBColor(0xF2, 0xF6, 0xFB)   # 浅底
CARD   = RGBColor(0xFF, 0xFF, 0xFF)   # 卡片白
INK    = RGBColor(0x1A, 0x27, 0x40)   # 正文深
GRAY   = RGBColor(0x60, 0x70, 0x88)   # 次要灰
LINE   = RGBColor(0xD6, 0xDF, 0xEC)   # 分隔线
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
CHIPBG = RGBColor(0xE9, 0xF1, 0xFB)   # 标签底
SUBBG  = RGBColor(0xF6, 0xF9, 0xFD)

FONT   = "微软雅黑"

# 一级能力域配色（10 个）
DOMAIN_COLORS = [BLUE, CYAN, TEAL, BLUE2, VIOLET, AMBER, CORAL, INDIGO, ROSE, RGBColor(0x2A, 0x9D, 0x8F)]

EMU_W = Inches(13.333)
EMU_H = Inches(7.5)

prs = Presentation()
prs.slide_width = EMU_W
prs.slide_height = EMU_H
BLANK = prs.slide_layouts[6]

# ----------------------------------------------------------------------------
# 基础助手
# ----------------------------------------------------------------------------

def add_slide():
    return prs.slides.add_slide(BLANK)


def _set_run_font(run, name=FONT):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", name)


def bg(slide, color):
    """整页背景填充"""
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, EMU_W, EMU_H)
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    # 置底
    sp = s._element
    sp.getparent().remove(sp)
    slide.shapes._spTree.insert(2, sp)
    return s


def rect(slide, l, t, w, h, fill=None, line=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE, shadow=False):
    s = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    if shadow:
        _soft_shadow(s)
    return s


def _soft_shadow(shape):
    spPr = shape._element.spPr
    effLst = spPr.makeelement(qn('a:effectLst'), {})
    sh = spPr.makeelement(qn('a:outerShdw'), {
        'blurRad': '60000', 'dist': '25000', 'dir': '5400000', 'rotWithShape': '0'})
    clr = spPr.makeelement(qn('a:srgbClr'), {'val': '1A2740'})
    alpha = spPr.makeelement(qn('a:alpha'), {'val': '22000'})
    clr.append(alpha)
    sh.append(clr)
    effLst.append(sh)
    spPr.append(effLst)


def line(slide, x1, y1, x2, y2, color=LINE, w=1.5, dash=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(w)
    c.shadow.inherit = False
    if dash:
        ln = c._element.spPr.find(qn('a:ln'))
        d = ln.makeelement(qn('a:prstDash'), {'val': dash})
        ln.append(d)
    return c


def text(slide, l, t, w, h, content, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, font=FONT, italic=False, line_spacing=1.0, wrap=True):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = content if isinstance(content, list) else [content]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = ln
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
        _set_run_font(run, font)
    return tb


def bullets(slide, l, t, w, h, items, size=13, color=INK, gap=6, marker_color=CYAN,
            bold_lead=False, line_spacing=1.05):
    """items: list of (text) or (lead, rest) tuples"""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(gap)
        p.line_spacing = line_spacing
        # marker
        m = p.add_run(); m.text = "▍"
        m.font.size = Pt(size); m.font.color.rgb = marker_color; _set_run_font(m)
        if isinstance(it, tuple):
            lead, rest = it
            r1 = p.add_run(); r1.text = lead
            r1.font.size = Pt(size); r1.font.bold = True; r1.font.color.rgb = color; _set_run_font(r1)
            r2 = p.add_run(); r2.text = rest
            r2.font.size = Pt(size); r2.font.color.rgb = GRAY; _set_run_font(r2)
        else:
            r = p.add_run(); r.text = " " + it
            r.font.size = Pt(size); r.font.bold = bold_lead; r.font.color.rgb = color; _set_run_font(r)
    return tb


def chip(slide, l, t, w, h, label, fill=CHIPBG, color=BLUE, size=10.5, bold=False):
    s = rect(slide, l, t, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, l, t, w, h, label, size=size, color=color, bold=bold,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ----------------------------------------------------------------------------
# 版式：内容页页眉/页脚
# ----------------------------------------------------------------------------
PAGE = {"n": 0}

def content_header(slide, kicker, title, idx=None):
    bg(slide, LIGHT)
    # 左侧竖条
    rect(slide, 0.0, 0.0, 0.18, 7.5, fill=BLUE)
    rect(slide, 0.18, 0.0, 0.06, 7.5, fill=CYAN)
    # kicker
    text(slide, 0.7, 0.45, 8, 0.3, kicker, size=12, color=BLUE, bold=True)
    text(slide, 0.7, 0.72, 11.8, 0.7, title, size=25, color=INK, bold=True)
    line(slide, 0.72, 1.45, 12.9, 1.45, color=LINE, w=1.2)
    # 页脚
    _footer(slide, idx)


def _footer(slide, idx=None):
    PAGE["n"] += 1
    n = idx if idx is not None else PAGE["n"]
    text(slide, 0.7, 7.06, 8, 0.3, "WHC 仓库调度平台 · 平台化规划方案", size=8.5, color=GRAY)
    text(slide, 11.6, 7.06, 1.3, 0.3, "%02d" % n, size=9, color=BLUE, bold=True, align=PP_ALIGN.RIGHT)


def section_divider(no, kicker, title, subtitle=""):
    slide = add_slide()
    bg(slide, NAVY)
    rect(slide, 0, 3.05, 13.333, 0.02, fill=BLUE2)
    # 大号编号
    text(slide, 0.85, 1.75, 3, 2.2, no, size=110, color=NAVY2, bold=True)
    rect(slide, 0.95, 3.55, 0.9, 0.09, fill=CYAN)
    text(slide, 0.95, 2.55, 11, 0.5, kicker, size=14, color=CYAN, bold=True)
    text(slide, 0.92, 3.78, 11.4, 1.2, title, size=34, color=WHITE, bold=True)
    if subtitle:
        text(slide, 0.95, 4.95, 11, 0.6, subtitle, size=13.5, color=RGBColor(0xB8, 0xC6, 0xDA))
    # 右下装饰
    for i, c in enumerate([BLUE, CYAN, TEAL]):
        rect(slide, 11.0 + i*0.5, 6.2, 0.34, 0.34, fill=c, shape=MSO_SHAPE.OVAL)
    return slide


print("helpers loaded")



# ============================================================================
# 01 封面
# ============================================================================
def slide_cover():
    s = add_slide()
    bg(s, NAVY)
    # 背景几何装饰
    rect(s, 9.4, -1.2, 5.5, 5.5, fill=NAVY2, shape=MSO_SHAPE.OVAL)
    rect(s, 11.2, 3.6, 4.0, 4.0, fill=RGBColor(0x10, 0x2C, 0x55), shape=MSO_SHAPE.OVAL)
    rect(s, 0.0, 0.0, 0.28, 7.5, fill=CYAN)
    # 顶部标签
    chip(s, 0.95, 0.95, 2.5, 0.42, "企业级中台规划方案", fill=NAVY2, color=CYAN, size=11, bold=True)
    # 主标题
    text(s, 0.92, 2.05, 11.5, 1.4, "WHC 仓库调度平台", size=50, color=WHITE, bold=True)
    text(s, 0.95, 3.35, 11.5, 0.9, "面向多 WMS 异构生态的平台化建设规划", size=22, color=RGBColor(0x9F, 0xC4, 0xEC))
    rect(s, 0.98, 4.45, 1.5, 0.1, fill=AMBER)
    # 副信息条
    subs = ["连接适配多厂商 WMS", "通用能力上移 · 平台化 WMS", "跨仓协同调度 · 全链路可视"]
    x = 0.98
    for i, txt in enumerate(subs):
        w = 0.36 + len(txt) * 0.165
        chip(s, x, 4.85, w, 0.5, txt, fill=NAVY2, color=WHITE, size=12)
        x += w + 0.25
    text(s, 0.95, 6.55, 9, 0.4, "ERP · OMS · PMS · OIC · Master Data  ⇄  WHC  ⇄  WMS / WCS / 机器人 / 3PL",
         size=12, color=RGBColor(0x7F, 0x93, 0xB2))
    text(s, 10.7, 6.55, 2.0, 0.4, "Confidential", size=10, color=GRAY, align=PP_ALIGN.RIGHT)


# ============================================================================
# 02 目录
# ============================================================================
def slide_agenda():
    s = add_slide()
    bg(s, LIGHT)
    rect(s, 0.0, 0.0, 4.6, 7.5, fill=NAVY)
    rect(s, 4.6, 0.0, 0.08, 7.5, fill=CYAN)
    text(s, 0.7, 1.5, 3.6, 0.5, "CONTENTS", size=14, color=CYAN, bold=True)
    text(s, 0.7, 1.95, 3.6, 1.6, "目录", size=46, color=WHITE, bold=True)
    text(s, 0.72, 3.5, 3.6, 2.5, "从战略定位到能力地图，\n再到技术架构与分期落地，\n形成完整可执行的建设蓝图。",
         size=12.5, color=RGBColor(0x9F, 0xB4, 0xD2), line_spacing=1.35)
    items = [
        ("01", "背景、挑战与平台定位", "多WMS痛点 · A→B渐进式定位 · 中台边界"),
        ("02", "WHC 平台化能力地图", "10 大一级能力域 · L1/L2/L3 能力分解"),
        ("03", "总体技术架构与核心设计", "分层架构 · 适配层 · 双链路调度 · 库存一致性"),
        ("04", "建设路线图与保障", "三期 18 个月 · 治理组织 · KPI/ROI · 风险"),
    ]
    y = 1.35
    for no, t, d in items:
        rect(s, 5.4, y, 0.62, 0.62, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        text(s, 5.4, y, 0.62, 0.62, no, size=18, color=BLUE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 6.25, y - 0.02, 6.6, 0.5, t, size=18, color=INK, bold=True)
        text(s, 6.27, y + 0.5, 6.6, 0.4, d, size=11.5, color=GRAY)
        y += 1.42
    _footer(s)


# ============================================================================
# 03 背景与挑战
# ============================================================================
def slide_background():
    s = add_slide()
    content_header(s, "01  背景与挑战", "零售多节点履约：异构 WMS 各自为政，缺乏统一调度大脑")
    # 上方：现状描述
    text(s, 0.72, 1.65, 12.1, 0.9,
         "零售网络中，大仓 / 门店仓 / FWDC / FC / 云仓 / 3PL 等节点由不同厂商、不同 WMS、不同自动化设备支撑。"
         "ERP 与各 WMS 之间缺乏统一的调度与适配层，导致接入碎片化、库存不一致、跨仓协同困难、能力无法复用。",
         size=13, color=GRAY, line_spacing=1.3)
    # 现状 vs 目标 两栏
    cards = [
        ("当前：点对点烟囱式集成", CORAL, [
            "每接一个新 WMS / 3PL 都要重复开发对接",
            "库存口径分散，OIC 与各仓数据难对齐",
            "出入库策略、波次能力被锁死在各厂商系统",
            "跨仓调拨、缺货改派靠人工协调",
            "设备（存储/拣选/分拣机器人）烟囱式接入",
        ]),
        ("目标：WHC 统一调度大脑", TEAL, [
            "一套适配框架，新仓/新厂商快速接入",
            "仓内物理库存真相统一，三方对账闭环",
            "通用 WMS 能力上移至平台，可复用可替换",
            "寻仓 / 跨仓协同 / 改派由平台自动编排",
            "多厂商设备标准化协同，人机混合调度",
        ]),
    ]
    x = 0.72
    for title, col, its in cards:
        rect(s, x, 2.75, 5.95, 3.95, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 2.75, 5.95, 0.62, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, 3.05, 5.95, 0.32, fill=col)
        text(s, x + 0.3, 2.75, 5.5, 0.62, title, size=15, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        bullets(s, x + 0.35, 3.65, 5.3, 2.9, its, size=12.5, marker_color=col, gap=9)
        x += 6.18
    _footer(s)


# ============================================================================
# 04 痛点分析
# ============================================================================
def slide_painpoints():
    s = add_slide()
    content_header(s, "01  痛点剖析", "五类核心痛点：从“接得慢”到“调不动”")
    pains = [
        ("接入碎片化", "集成", "每个 WMS/3PL/设备私有协议，重复造接口，接入周期以月计", CORAL),
        ("库存不一致", "数据", "WMS↔WHC↔OIC 多处库存口径，差异靠人工核对，超卖/缺货频发", AMBER),
        ("能力被锁死", "复用", "波次、策略、计费等通用能力散落各厂商 WMS，无法沉淀复用", BLUE),
        ("协同靠人工", "调度", "跨仓调拨、缺货改派、产能均衡缺乏自动编排，时效与成本不可控", VIOLET),
        ("黑盒不可视", "运营", "全链路状态分散在各系统，缺乏统一控制塔与异常预警", TEAL),
    ]
    # 五张卡片横向
    cw, gap = 2.35, 0.12
    x = 0.72
    for name, tag, desc, col in pains:
        rect(s, x, 1.95, cw, 4.55, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 1.95, cw, 0.16, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x + cw/2 - 0.42, 2.4, 0.84, 0.84, fill=col, shape=MSO_SHAPE.OVAL)
        text(s, x + cw/2 - 0.42, 2.4, 0.84, 0.84, tag, size=13, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.12, 3.45, cw - 0.24, 0.5, name, size=15.5, color=INK, bold=True, align=PP_ALIGN.CENTER)
        text(s, x + 0.22, 4.05, cw - 0.44, 2.3, desc, size=11.5, color=GRAY, line_spacing=1.25, align=PP_ALIGN.CENTER)
        x += cw + gap
    text(s, 0.72, 6.72, 12, 0.4, "结论：需要在 ERP/中台 与 WMS 之间，建设一个统一适配 + 编排调度 + 能力上移的平台层 —— WHC。",
         size=12.5, color=BLUE, bold=True)
    _footer(s)


# ============================================================================
# 05 定位与愿景（A→B 渐进式）
# ============================================================================
def slide_positioning():
    s = add_slide()
    content_header(s, "01  平台定位", "定位：从“集成调度层”渐进演化为“平台化 WMS”")
    # 愿景语
    rect(s, 0.72, 1.62, 11.9, 0.92, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 1.05, 1.62, 11.3, 0.92,
         "愿景：让任意厂商 WMS 即插即用，让仓储通用能力沉淀为平台资产，让跨仓履约由平台智能调度。",
         size=14.5, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    # 三阶段演进
    stages = [
        ("阶段 A · 连接与调度", BLUE, "适配 · 路由 · 可视", [
            "多 WMS / 设备标准适配", "订单寻仓与编排路由", "仓内库存真相与对账", "全链路可视化"]),
        ("阶段 A→B · 能力上移", TEAL, "通用能力平台化", [
            "波次 / 出入库策略上移", "3PL 计费结算上移", "跨仓协同调度", "作业策略中心"]),
        ("阶段 B · 平台化 WMS", AMBER, "厂商 WMS 可替换", [
            "平台承载通用 WMS 能力", "厂商WMS退化为执行层", "设备直连与人机调度", "算法驱动智能优化"]),
    ]
    x = 0.72
    for i, (t, col, sub, its) in enumerate(stages):
        rect(s, x, 2.85, 3.78, 3.7, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 2.85, 3.78, 0.92, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, 3.4, 3.78, 0.37, fill=col)
        text(s, x + 0.25, 2.9, 3.3, 0.5, t, size=15, color=WHITE, bold=True)
        text(s, x + 0.25, 3.38, 3.3, 0.36, sub, size=11.5, color=RGBColor(0xEC,0xF4,0xFF))
        bullets(s, x + 0.3, 3.95, 3.2, 2.4, its, size=12, marker_color=col, gap=7)
        if i < 2:
            text(s, x + 3.78 + 0.02, 4.3, 0.36, 0.6, "➜", size=22, color=GRAY, align=PP_ALIGN.CENTER)
        x += 3.78 + 0.38
    text(s, 0.72, 6.74, 12, 0.4,
         "渐进式路线：先“通”（连得上、看得见），再“调”（调得动、对得准），后“上移”与“变聪明”，控制风险、快速见效。",
         size=12, color=GRAY)
    _footer(s)


print("strategy part-1 loaded")



# ============================================================================
# 06 系统边界与中台协同（关键图）
# ============================================================================
def slide_boundary():
    s = add_slide()
    content_header(s, "01  系统边界", "中台协同：WHC 管“仓库怎么干”，不重复造中台轮子")
    # 上层：四大自研中台 + ERP
    top = [
        ("ERP", "财务/总账", GRAY),
        ("PMS 采购订单中台", "采购·调拨·退供·加工", INDIGO),
        ("OMS 销售订单中台", "C 端销售履约单", BLUE),
        ("OIC 全渠道库存中台", "渠道可用量·ATP·共享前置", TEAL),
        ("Master Data", "货品·仓网·线路与时效", VIOLET),
    ]
    n = len(top); tw = 2.36; gapx = 0.12
    total = n*tw + (n-1)*gapx
    x0 = (13.333 - total) / 2
    x = x0
    for name, sub, col in top:
        rect(s, x, 1.7, tw, 0.95, fill=CARD, line=col, line_w=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 1.7, 0.12, 0.95, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x + 0.2, 1.78, tw - 0.28, 0.45, name, size=12.5, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.2, 2.22, tw - 0.28, 0.36, sub, size=9.5, color=GRAY)
        line(s, x + tw/2, 2.65, x + tw/2, 3.05, color=col, w=1.6)
        x += tw + gapx
    # 中层：WHC 平台
    rect(s, x0, 3.05, total, 1.65, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    text(s, x0 + 0.35, 3.16, 4, 0.5, "WHC 仓库调度平台", size=17, color=WHITE, bold=True)
    text(s, x0 + 0.35, 3.62, 5, 0.35, "适配 · 编排 · 作业策略 · 库存真相 · 计费 · 控制塔", size=10.5, color=CYAN)
    caps = ["接入适配", "双链路编排", "库存一致性", "作业调度", "标准化映射", "3PL计费", "控制塔"]
    cx = x0 + 0.35
    for c in caps:
        w = 0.3 + len(c)*0.19
        chip(s, cx, 4.16, w, 0.42, c, fill=NAVY2, color=WHITE, size=10)
        cx += w + 0.14
    line(s, 6.66, 4.7, 6.66, 5.05, color=BLUE2, w=1.6)
    # 下层：执行/设备层
    bottoms = [
        ("WMS-A / B / C", "多家异构 WMS", BLUE),
        ("WCS / WES", "仓控/执行系统", BLUE2),
        ("机器人（多厂商）", "存储·拣选·分拣", CYAN),
        ("3PL 系统", "三方仓/计费对账", AMBER),
    ]
    bw = 2.7; bg2 = 0.2
    btotal = len(bottoms)*bw + (len(bottoms)-1)*bg2
    bx = (13.333 - btotal)/2
    for name, sub, col in bottoms:
        rect(s, bx, 5.05, bw, 0.92, fill=SUBBG, line=col, line_w=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, bx + 0.2, 5.12, bw - 0.3, 0.45, name, size=12, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, bx + 0.2, 5.55, bw - 0.3, 0.35, sub, size=9.5, color=GRAY)
        bx += bw + bg2
    # 边界红线说明
    rect(s, 0.72, 6.18, 11.9, 0.78, fill=CHIPBG, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 0.95, 6.18, 11.5, 0.78,
         "边界红线：OMS/PMS 管订单业务 · OIC 管渠道库存账 · Master Data 管货品/仓网/线路时效 · "
         "WHC 只做仓库执行编排 + 多WMS标准化 + 仓内物理库存真相 + 调度（消费而非重建以上中台能力）。",
         size=11, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)
    _footer(s)


# ============================================================================
# 07 设计原则
# ============================================================================
def slide_principles():
    s = add_slide()
    content_header(s, "01  设计原则", "六项设计原则：可接入、可复用、可替换、可演进")
    principles = [
        ("适配解耦", BLUE, "厂商差异收敛在适配层，核心域不感知具体 WMS/设备厂商"),
        ("能力上移", TEAL, "通用 WMS 能力沉淀为平台资产，一次建设、多仓复用"),
        ("中台协同", VIOLET, "消费 OMS/PMS/OIC/MDM 能力，明确边界、不重复造轮子"),
        ("事件驱动", CYAN, "统一事件模型 + 消息总线，状态实时、链路可追踪"),
        ("配置优先", AMBER, "规则/策略/流程可配置、低代码编排，减少硬编码与定制"),
        ("渐进演进", INDIGO, "A→B 分期推进，单仓试点可灰度，厂商 WMS 可平滑替换"),
    ]
    cw, ch, gx, gy = 3.86, 1.95, 0.22, 0.28
    x0, y0 = 0.72, 1.85
    for i, (t, col, d) in enumerate(principles):
        r, c = divmod(i, 3)
        x = x0 + c*(cw+gx); y = y0 + r*(ch+gy)
        rect(s, x, y, cw, ch, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, y, 0.14, ch, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x + 0.38, y + 0.32, 0.62, 0.62, fill=col, shape=MSO_SHAPE.OVAL)
        text(s, x + 0.38, y + 0.32, 0.62, 0.62, str(i+1), size=18, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 1.18, y + 0.34, cw - 1.3, 0.55, t, size=16, color=INK, bold=True)
        text(s, x + 0.4, y + 1.08, cw - 0.65, 0.8, d, size=11.5, color=GRAY, line_spacing=1.2)
    _footer(s)


print("strategy part-2 loaded")



# ============================================================================
# 能力地图数据（L1 -> [(L2, L3代表能力)]）
# ============================================================================
DOMAINS = [
    ("L1-1", "接入与适配", "万能接口，屏蔽厂商差异", [
        ("WMS 适配", "适配器框架/SDK · 协议适配(API/MQ/EDI/File) · 报文转换 · 字段映射 · 灰度发布"),
        ("设备 / WCS / WES 接入", "多厂商机器人(存储·拣选·分拣) · WCS 标准指令 · 设备状态采集 · 能力注册"),
        ("上游接入", "OMS / PMS / OIC / MDM / ERP 对接 · 事件订阅 · 报文安全"),
        ("适配器治理", "注册中心 · 健康监控 · 限流熔断 · 重连补偿"),
    ]),
    ("L1-2", "双链路履约编排", "调度大脑（出库 + 入库）", [
        ("智能寻仓 / 分仓", "读取 MDM 线路与时效 · 拆合单落地 · 就近 / 成本 / SLA 策略"),
        ("出库链路编排（OMS 驱动）", "波次 / 任务编排 · 拣选 · 复核 · 打包 · 出库"),
        ("入库链路编排（PMS 驱动）", "采购收货 · 调拨双侧协同 · 退供 · 加工 / VAS"),
        ("异常与改派", "异常识别分类 · 自动改派 · 工单流转"),
    ]),
    ("L1-3", "仓内库存真相与一致性", "物理库存真相（上报 OIC）", [
        ("多 WMS 物理库存聚合", "实时同步 · 库存快照 · 库位 / 批次 / 序列号"),
        ("三方对账", "WMS ↔ WHC ↔ OIC 对账 · 差异告警 · 自动 / 人工冲正"),
        ("库存事件上报", "标准库存事件 · 实时上报 OIC"),
        ("盘点 / 冻结协同", "盘点协同 · 冻结 / 解冻 · 调整单"),
    ]),
    ("L1-4", "作业调度与策略", "通用作业能力上移", [
        ("入库策略", "预约 · 收货 · 质检 · 上架策略"),
        ("出库策略", "波次合并 · 拣选路径 · 复核打包策略"),
        ("资源调度", "人 / 设备 / 库区调度 · 产能均衡 · 优先级 / SLA 调度"),
        ("自动化协同", "多厂商机器人协同 · 人机混合 · 任务下发"),
    ]),
    ("L1-5", "标准化与映射", "厂商码 ↔ MDM 标准码", [
        ("编码映射", "厂商 WMS 编码 ↔ MDM 标准码 · 商品 / 库位 / 容器映射"),
        ("状态与事件标准", "统一状态机 · 标准事件模型 · 版本管理"),
        ("字典中心", "业务字典 · 单位 / 计量 · 异常码"),
        ("主数据消费", "引用 MDM 的 货品 / 仓网 / 线路与时效（非主数据源）"),
    ]),
    ("L1-6", "承运与配送协同", "出库到交付闭环", [
        ("运力对接", "TMS / 承运商对接 · 运力分配 · 面单 / 合规"),
        ("出库交接", "集货 / 交接 · 轨迹回传 · 签收闭环"),
        ("逆向协同", "退货入库 · 换货协同"),
    ]),
    ("L1-7", "3PL 计费与结算", "三方仓成本可算可对", [
        ("计量采集", "操作量 / 存储量 / 增值服务量采集"),
        ("计费引擎", "计费规则 · 阶梯 / 合同价 · 费用试算"),
        ("对账结算", "账单生成 · 3PL 对账 · 争议处理 · 结算输出"),
    ]),
    ("L1-8", "可视化与控制塔", "全链路看得见、管得住", [
        ("全链路可视", "订单 / 库存 / 作业追踪 · 时间轴"),
        ("KPI 看板", "仓库健康度 · 履约 / 库存 / 产能指标"),
        ("监控告警", "实时监控 · 阈值告警 · 大屏 / 数字孪生（后期）"),
    ]),
    ("L1-9", "数据与智能", "数据驱动持续优化", [
        ("数据底座", "采集 / ODS / 数仓 · 指标体系 · BI"),
        ("预测", "单量 / 产能 / 库存预测"),
        ("智能优化", "寻仓 / 路径 / 产能优化 · 异常检测 · 智能改派"),
    ]),
    ("L1-10", "平台与治理", "多租户技术底座", [
        ("多租户 / 组织", "自营 + 3PL 多租户 · 数据隔离 · 组织权限"),
        ("配置与低代码", "规则中心 · 配置中心 · 流程可视化编排"),
        ("开放平台", "API 网关 · 开发者门户 · Webhook"),
        ("可观测 / 高可用", "日志 / 链路 / 监控 · 灰度 · 容灾弹性 · 安全审计"),
    ]),
]


# ============================================================================
# 08 能力总览（10 大一级能力域 grid）
# ============================================================================
def slide_capability_overview():
    s = add_slide()
    content_header(s, "02  能力地图", "WHC 平台化能力全景：10 大一级能力域")
    text(s, 0.72, 1.6, 12, 0.4, "蓝色＝平台底座与连接 · 绿/青＝核心调度与上移能力 · 琥珀/紫＝增值与智能能力", size=11, color=GRAY)
    cols, cw, ch, gx, gy = 5, 2.36, 2.18, 0.13, 0.22
    x0, y0 = 0.72, 2.05
    for i, (no, name, sub, _l2) in enumerate(DOMAINS):
        r, c = divmod(i, cols)
        x = x0 + c*(cw+gx); y = y0 + r*(ch+gy)
        col = DOMAIN_COLORS[i]
        rect(s, x, y, cw, ch, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, y, cw, 0.5, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, y+0.25, cw, 0.25, fill=col)
        text(s, x + 0.15, y, 1.2, 0.5, no, size=12, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.15, y + 0.58, cw - 0.3, 0.6, name, size=13.5, color=INK, bold=True)
        text(s, x + 0.15, y + 1.2, cw - 0.3, 0.5, sub, size=10, color=GRAY, line_spacing=1.1)
        # L2 数量标记
        text(s, x + 0.15, y + 1.74, cw - 0.3, 0.32, "└ %d 项二级能力" % len(_l2), size=9.5, color=col, bold=True)
    _footer(s)


# ============================================================================
# 能力详解块
# ============================================================================
def cap_block(s, x, y, w, h, idx, l2list):
    no, name, sub, _ = DOMAINS[idx]
    col = DOMAIN_COLORS[idx]
    # 左侧 L1 卡
    lw = 2.45
    rect(s, x, y, lw, h, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, x + 0.22, y + 0.16, lw - 0.4, 0.34, no, size=12, color=RGBColor(0xEC,0xF4,0xFF), bold=True)
    text(s, x + 0.22, y + 0.5, lw - 0.4, 0.9, name, size=15, color=WHITE, bold=True, line_spacing=1.05)
    text(s, x + 0.22, y + h - 0.5, lw - 0.4, 0.4, sub, size=9.5, color=RGBColor(0xDCE if False else 0xDC,0xE8,0xF6))
    # 右侧 L2 行
    rx = x + lw + 0.12
    rw = w - lw - 0.12
    rect(s, rx, y, rw, h, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    n = len(l2list)
    rowh = (h - 0.2) / n
    for j, (l2, l3) in enumerate(l2list):
        ry = y + 0.1 + j*rowh
        rect(s, rx + 0.15, ry + rowh/2 - 0.05, 0.1, 0.1, fill=col, shape=MSO_SHAPE.OVAL)
        text(s, rx + 0.38, ry, 2.85, rowh, l2, size=12, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
        text(s, rx + 3.35, ry, rw - 3.5, rowh, "L3 · " + l3, size=10.3, color=GRAY,
             anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
        if j < n - 1:
            line(s, rx + 0.3, ry + rowh, rx + rw - 0.25, ry + rowh, color=LINE, w=0.75)


def slide_capability_detail(title, idxs):
    s = add_slide()
    content_header(s, "02  能力地图 · L1 / L2 / L3", title)
    y0 = 1.7
    avail = 6.95 - y0
    n = len(idxs)
    gy = 0.2
    h = (avail - (n-1)*gy) / n
    for k, idx in enumerate(idxs):
        cap_block(s, 0.72, y0 + k*(h+gy), 11.9, h, idx, DOMAINS[idx][3])
    _footer(s)


print("capability part loaded")



# ============================================================================
# 12 总体技术架构（分层）
# ============================================================================
def slide_architecture():
    s = add_slide()
    content_header(s, "03  总体架构", "六层架构：接入 · 适配 · 能力 · 数据 · 平台底座")
    x0, w = 0.72, 11.9
    def band(y, h, title, col, chips, titlecol=WHITE):
        rect(s, x0, y, w, h, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x0 + 0.22, y, 2.1, h, title, size=12.5, color=titlecol, bold=True, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
        cx = x0 + 2.45
        for c in chips:
            cwd = 0.3 + len(c)*0.158
            chip(s, cx, y + h/2 - 0.21, cwd, 0.42, c, fill=RGBColor(0xFF,0xFF,0xFF), color=col, size=10)
            cx += cwd + 0.12
    # 上游（外部）
    band(1.62, 0.62, "上游 / 中台", NAVY2, ["ERP", "OMS 销售单", "PMS 采购单", "OIC 渠道库存", "Master Data 货品·仓网·线路时效"])
    line(s, 6.66, 2.24, 6.66, 2.42, color=GRAY, w=1.4)
    # 接入/开放层
    band(2.42, 0.62, "接入开放层", BLUE, ["API 网关", "事件总线/订阅", "开发者门户", "Webhook", "安全认证"])
    # 能力/业务层（两行）
    rect(s, x0, 3.16, w, 1.62, fill=RGBColor(0xE9,0xF1,0xFB), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, x0 + 0.22, 3.22, 2.1, 0.4, "核心能力层", size=12.5, color=BLUE, bold=True)
    caps = ["双链路编排引擎", "智能寻仓", "作业调度与策略", "仓内库存一致性", "标准化与映射", "3PL 计费", "控制塔", "数据与智能"]
    cw2 = 2.78; gx2 = 0.1
    for i, c in enumerate(caps):
        r, cc = divmod(i, 4)
        cx = x0 + 0.25 + cc*(cw2+gx2); cy = 3.62 + r*0.56
        chip(s, cx, cy, cw2, 0.46, c, fill=CARD, color=INK, size=11, bold=True)
        rect(s, cx, cy, 0.09, 0.46, fill=DOMAIN_COLORS[i % len(DOMAIN_COLORS)], shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    # 适配层
    band(4.92, 0.62, "适配层", TEAL, ["WMS 适配器", "WCS/WES 适配器", "机器人适配器(多厂商)", "3PL 适配器", "协议/报文/字段映射"])
    line(s, 6.66, 5.54, 6.66, 5.72, color=GRAY, w=1.4)
    # 执行层（外部）
    band(5.72, 0.56, "执行层(外部)", RGBColor(0x5A,0x6B,0x88), ["WMS-A/B/C", "WCS / WES", "存储·拣选·分拣机器人", "3PL 系统"])
    # 平台底座（贯穿，右侧竖条）
    rect(s, x0, 6.42, w, 0.5, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, x0 + 0.22, 6.42, 2.1, 0.5, "平台底座", size=12, color=CYAN, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    base = ["多租户", "配置中心", "规则引擎", "流程编排", "消息中间件", "数据底座", "可观测", "灰度/容灾", "安全审计"]
    cx = x0 + 2.45
    for b in base:
        cwd = 0.26 + len(b)*0.16
        chip(s, cx, 6.49, cwd, 0.36, b, fill=NAVY2, color=WHITE, size=9.5)
        cx += cwd + 0.1
    _footer(s)


# ============================================================================
# 13 适配层核心设计
# ============================================================================
def slide_adapter():
    s = add_slide()
    content_header(s, "03  核心设计 · 适配层", "适配器框架：一次定义、快速接入、灰度可控")
    # 左：四级处理管道
    text(s, 0.72, 1.62, 6, 0.4, "统一适配处理管道", size=14, color=BLUE, bold=True)
    pipe = [
        ("接入协议", "API / MQ / EDI / File / DB-CDC", BLUE),
        ("报文解析与转换", "JSON / XML / EDI / 自定义 ⇄ 标准报文", BLUE2),
        ("字段与编码映射", "厂商字段/码 ↔ WHC 标准模型 (引用 MDM)", CYAN),
        ("校验与补偿", "幂等 / 重试 / 重连 / 死信补偿", TEAL),
    ]
    y = 2.15
    for i, (t, d, col) in enumerate(pipe):
        rect(s, 0.72, y, 5.85, 0.92, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, 0.72, y, 0.12, 0.92, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, 0.95, y + 0.18, 0.56, 0.56, fill=col, shape=MSO_SHAPE.OVAL)
        text(s, 0.95, y + 0.18, 0.56, 0.56, str(i+1), size=16, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 1.7, y + 0.12, 4.7, 0.42, t, size=13.5, color=INK, bold=True)
        text(s, 1.7, y + 0.52, 4.7, 0.34, d, size=10.5, color=GRAY)
        if i < 3:
            text(s, 3.4, y + 0.9, 0.5, 0.22, "▼", size=11, color=GRAY, align=PP_ALIGN.CENTER)
        y += 1.12
    # 右：适配器治理 + 收益
    rect(s, 6.85, 2.15, 5.75, 2.35, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 7.15, 2.32, 5.2, 0.4, "适配器治理中心", size=14, color=CYAN, bold=True)
    bullets(s, 7.15, 2.85, 5.2, 1.5, [
        ("注册中心：", "适配器/能力声明式注册与发现"),
        ("健康监控：", "心跳 / 成功率 / 时延 / 积压告警"),
        ("流量治理：", "限流 / 熔断 / 优先级隔离"),
        ("版本灰度：", "多版本并存 · 按仓灰度切换"),
    ], size=11.5, color=WHITE, marker_color=CYAN, gap=6)
    rect(s, 6.85, 4.65, 5.75, 2.05, fill=CHIPBG, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 7.15, 4.8, 5.2, 0.4, "标准化带来的收益", size=14, color=BLUE, bold=True)
    bullets(s, 7.15, 5.3, 5.2, 1.3, [
        "新 WMS / 3PL 接入周期从“月”级降至“周”级",
        "厂商 WMS 可平滑替换，避免被单一厂商锁定",
        "设备/机器人多厂商统一接入，复用调度能力",
        "适配资产沉淀，跨仓跨项目复用",
    ], size=11.5, color=INK, marker_color=TEAL, gap=6)
    _footer(s)


# ============================================================================
# 14 双链路调度编排
# ============================================================================
def slide_orchestration():
    s = add_slide()
    content_header(s, "03  核心设计 · 调度编排", "双链路编排：寻仓为入口，出/入库各成闭环")
    # 寻仓引擎（顶部）
    rect(s, 0.72, 1.62, 11.9, 0.78, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 1.0, 1.62, 3.6, 0.78, "智能寻仓 / 分仓引擎", size=14, color=CYAN, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    for i, t in enumerate(["读取 MDM 线路与时效", "实时库存(L1-3)", "成本 / SLA 策略", "拆单 / 合单 / 分仓"]):
        chip(s, 4.7 + i*1.95, 1.78, 1.85, 0.46, t, fill=NAVY2, color=WHITE, size=9.8)
    # 两条链路
    def lane(x, w, title, col, driver, steps):
        rect(s, x, 2.72, w, 3.55, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 2.72, w, 0.66, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, 3.05, w, 0.33, fill=col)
        text(s, x + 0.28, 2.72, w - 0.5, 0.66, title, size=14.5, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.28, 3.5, w - 0.5, 0.36, driver, size=11, color=col, bold=True)
        yy = 3.95
        for st, dd in steps:
            rect(s, x + 0.3, yy, w - 0.6, 0.5, fill=SUBBG, line=col, line_w=1.0, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            text(s, x + 0.5, yy, 2.0, 0.5, st, size=11.5, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
            text(s, x + 2.45, yy, w - 2.75, 0.5, dd, size=9.8, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
            yy += 0.585
    lane(0.72, 5.85, "出库链路", BLUE, "▶ 由 OMS 销售履约单驱动", [
        ("接单落地", "履约单 → 寻仓结果落地到目标仓"),
        ("波次/任务", "波次合并 · 任务生成 · 优先级"),
        ("拣选复核", "下发 WMS/WCS · 人机协同"),
        ("打包出库", "复核 · 打包 · 交接承运"),
    ])
    lane(6.75, 5.85, "入库链路", INDIGO, "▶ 由 PMS 采购/调拨/退供/加工单驱动", [
        ("接单落地", "采购到货 / 调拨 / 退供 / 加工单"),
        ("预约收货", "预约 · 卸货 · 收货 · 质检"),
        ("上架/加工", "上架策略 · VAS 加工作业"),
        ("库存确认", "库存上报 · 调拨双侧协同"),
    ])
    # 底部编排能力
    text(s, 0.72, 6.4, 11.9, 0.5,
         "贯穿能力：流程编排(状态机/Workflow) · SAGA 补偿 · 超时重试 · 人工干预节点 · 异常识别与自动改派 · 全程事件驱动。",
         size=11, color=GRAY)
    _footer(s)


print("technical part-1 loaded")



# ============================================================================
# 15 仓内库存真相与一致性（三方对账）
# ============================================================================
def slide_inventory():
    s = add_slide()
    content_header(s, "03  核心设计 · 库存一致性", "三方对账：WMS 物理真相 → WHC 聚合 → OIC 渠道账")
    # 三个节点
    nodes = [
        (1.1, "WMS（各仓）", "物理库存真相\n库位/批次/序列号", BLUE),
        (5.4, "WHC 库存聚合", "多仓实时聚合\n标准库存事件", TEAL),
        (9.7, "OIC 渠道库存", "渠道可用量 / ATP\n共享 / 前置仓", VIOLET),
    ]
    for x, t, d, col in nodes:
        rect(s, x, 2.1, 2.55, 1.55, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 2.1, 2.55, 0.5, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, 2.35, 2.55, 0.25, fill=col)
        text(s, x + 0.15, 2.1, 2.25, 0.5, t, size=12.5, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.2, 2.72, 2.2, 0.85, d, size=10.5, color=GRAY, line_spacing=1.15)
    # 箭头
    line(s, 3.65, 2.88, 5.4, 2.88, color=BLUE2, w=2.0)
    text(s, 3.7, 2.5, 1.7, 0.35, "实时同步/快照", size=9.5, color=BLUE2, align=PP_ALIGN.CENTER)
    line(s, 7.95, 2.88, 9.7, 2.88, color=TEAL, w=2.0)
    text(s, 8.0, 2.5, 1.7, 0.35, "库存事件上报", size=9.5, color=TEAL, align=PP_ALIGN.CENTER)
    # 对账引擎
    rect(s, 3.0, 4.05, 7.35, 0.95, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 3.25, 4.05, 3.0, 0.95, "对账引擎", size=14, color=CYAN, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    for i, t in enumerate(["定时/实时对账", "差异识别告警", "自动/人工冲正"]):
        chip(s, 5.2 + i*1.7, 4.32, 1.6, 0.42, t, fill=NAVY2, color=WHITE, size=10)
    line(s, 2.37, 3.65, 4.6, 4.05, color=GRAY, w=1.2, dash="dash")
    line(s, 6.67, 3.65, 6.67, 4.05, color=GRAY, w=1.2, dash="dash")
    line(s, 10.97, 3.65, 9.0, 4.05, color=GRAY, w=1.2, dash="dash")
    # 底部三卡：关键设计
    cards = [
        ("职责红线", VIOLET, ["WHC 只管仓内物理真相", "渠道可用量/ATP 归 OIC", "不在 WHC 重建渠道库存"]),
        ("一致性机制", TEAL, ["事件 + 快照双保险", "幂等 / 顺序 / 去重", "差异分级与自愈"]),
        ("协同闭环", BLUE, ["盘点 / 冻结 / 解冻协同", "调整单回流各 WMS", "异常工单闭环"]),
    ]
    x = 0.72
    for t, col, its in cards:
        rect(s, x, 5.25, 3.86, 1.62, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 5.25, 0.12, 1.62, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x + 0.32, 5.36, 3.4, 0.4, t, size=13, color=INK, bold=True)
        bullets(s, x + 0.34, 5.78, 3.4, 1.0, its, size=10.3, marker_color=col, gap=3)
        x += 4.05
    _footer(s)


# ============================================================================
# 16 标准化与映射
# ============================================================================
def slide_standardization():
    s = add_slide()
    content_header(s, "03  核心设计 · 标准化", "标准化与映射：把厂商语言翻译成平台语言")
    # 左：映射示意
    text(s, 0.72, 1.62, 6, 0.4, "编码与状态映射（引用 MDM 标准码）", size=14, color=BLUE, bold=True)
    rows = [
        ("商品编码", "厂商 SKU 码", "MDM 标准货品码"),
        ("库位/库区", "厂商库位码", "WHC 标准库位模型"),
        ("容器/包装", "厂商容器码", "MDM 包装/容器码"),
        ("作业状态", "厂商状态码", "WHC 统一状态机"),
        ("业务事件", "厂商事件", "标准事件模型"),
    ]
    y = 2.15
    rect(s, 0.72, y, 5.95, 0.5, fill=NAVY)
    text(s, 0.9, y, 1.7, 0.5, "对象", size=11, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 2.55, y, 1.9, 0.5, "厂商侧（多样）", size=11, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 4.65, y, 1.9, 0.5, "WHC 标准（唯一）", size=11, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    y += 0.5
    for i, (a, b, c) in enumerate(rows):
        fill = CARD if i % 2 == 0 else SUBBG
        rect(s, 0.72, y, 5.95, 0.5, fill=fill, line=LINE, line_w=0.5)
        text(s, 0.9, y, 1.7, 0.5, a, size=10.8, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 2.55, y, 1.9, 0.5, b, size=10.3, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 4.45, y, 0.25, 0.5, "→", size=11, color=TEAL, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 4.7, y, 1.95, 0.5, c, size=10.3, color=TEAL, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        y += 0.5
    # 右：标准化资产
    rect(s, 6.95, 2.15, 5.65, 2.05, fill=CHIPBG, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 7.2, 2.3, 5.2, 0.4, "平台标准化资产", size=14, color=BLUE, bold=True)
    bullets(s, 7.2, 2.8, 5.2, 1.3, [
        ("标准业务对象：", "订单/任务/库存/容器/事件统一模型"),
        ("统一状态机：", "出入库/作业状态标准化与版本管理"),
        ("字典中心：", "单位/计量/异常码/原因码"),
    ], size=11, color=INK, marker_color=BLUE, gap=6)
    rect(s, 6.95, 4.35, 5.65, 2.5, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 7.2, 4.5, 5.2, 0.4, "与 Master Data 的关系（消费方）", size=13.5, color=CYAN, bold=True)
    bullets(s, 7.2, 5.05, 5.2, 1.7, [
        "货品 / 仓网 / 货品×仓网线路与时效 → 全部来自 MDM",
        "WHC 不定义主数据，只建立“厂商码 ↔ MDM 标准码”映射",
        "寻仓引擎运行时引用 MDM 线路与时效做落地决策",
        "MDM 变更通过事件订阅同步，保证口径一致",
    ], size=11, color=WHITE, marker_color=CYAN, gap=7)
    _footer(s)


# ============================================================================
# 17 集成方案
# ============================================================================
def slide_integration():
    s = add_slide()
    content_header(s, "03  集成方案", "对内消费中台、对外适配执行，事件驱动贯穿全链路")
    headers = ["集成对象", "方向", "主要方式", "关键交互内容"]
    data = [
        ("OMS 销售订单中台", "双向", "API + 事件", "接收履约单，回传出库/履约状态、库存事件", BLUE),
        ("PMS 采购订单中台", "双向", "API + 事件", "接收采购/调拨/退供/加工单，回传入库作业状态", INDIGO),
        ("OIC 全渠道库存中台", "上报为主", "事件 + API", "上报仓内物理库存与变动事件，参与三方对账", TEAL),
        ("Master Data", "消费", "API + 事件订阅", "获取货品/仓网/线路与时效，建立标准码映射", VIOLET),
        ("ERP", "按需", "API / 文件", "单据/成本/结算等必要数据交互", GRAY),
        ("各厂商 WMS", "双向", "适配器(API/MQ/EDI/File)", "下发作业指令、采集执行与库存结果", BLUE2),
        ("WCS / WES / 机器人", "双向", "适配器(API/MQ)", "设备任务下发、状态与产能采集", CYAN),
        ("3PL 系统", "双向", "适配器(API/EDI/File)", "作业协同、计量采集、计费对账", AMBER),
    ]
    x0 = 0.72
    widths = [3.0, 1.2, 2.4, 5.3]
    y = 1.75
    # header
    cx = x0
    for i, hh in enumerate(headers):
        rect(s, cx, y, widths[i], 0.52, fill=NAVY)
        text(s, cx + 0.15, y, widths[i]-0.2, 0.52, hh, size=11.5, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        cx += widths[i]
    y += 0.52
    for r, (obj, dirn, mode, desc, col) in enumerate(data):
        fill = CARD if r % 2 == 0 else SUBBG
        cx = x0
        vals = [obj, dirn, mode, desc]
        for i, v in enumerate(vals):
            rect(s, cx, y, widths[i], 0.555, fill=fill, line=LINE, line_w=0.5)
            if i == 0:
                rect(s, cx, y, 0.1, 0.555, fill=col)
                text(s, cx + 0.22, y, widths[i]-0.3, 0.555, v, size=10.8, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
            elif i == 1:
                text(s, cx, y, widths[i], 0.555, v, size=10.3, color=col, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            else:
                text(s, cx + 0.15, y, widths[i]-0.2, 0.555, v, size=10.2, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
            cx += widths[i]
        y += 0.555
    text(s, 0.72, 6.74, 12, 0.4, "统一通过消息总线承载事件，配合 API 网关与适配器治理，实现松耦合、可观测、可灰度的集成。",
         size=11, color=BLUE, bold=True)
    _footer(s)


print("technical part-2 loaded")



# ============================================================================
# 18 建设路线图（三期）
# ============================================================================
def slide_roadmap():
    s = add_slide()
    content_header(s, "04  建设路线图", "三期 · 约 18 个月：连得上 → 调得动 → 提得效")
    phases = [
        ("一期", "0 - 6 个月", "连得上、看得见", BLUE,
         ["接入适配框架 + 适配器治理", "标准化与映射 / 字典中心", "仓内库存真相与三方对账", "控制塔 V1 + 平台底座/多租户"],
         "试点：大仓 + 3PL 电商仓"),
        ("二期", "6 - 12 个月", "调得动、对得准", TEAL,
         ["双链路履约编排 + 智能寻仓", "出入库作业策略上移", "3PL 计费与结算", "承运配送协同"],
         "扩展：自营 FC"),
        ("三期", "12 - 18 个月", "提得效、变聪明", AMBER,
         ["资源调度 + 自动化人机协同", "数据底座 + 预测与智能优化", "控制塔升级 / 数字孪生", "厂商 WMS 可替换验证"],
         "扩展：门店仓 + 云仓"),
    ]
    # 时间轴
    line(s, 1.0, 2.05, 12.4, 2.05, color=LINE, w=2.5)
    cw = 3.85; x0 = 0.72; gx = 0.2
    for i, (name, period, theme, col, items, scope) in enumerate(phases):
        x = x0 + i*(cw+gx)
        cx = x + cw/2
        rect(s, cx - 0.16, 1.89, 0.32, 0.32, fill=col, shape=MSO_SHAPE.OVAL)
        rect(s, x, 2.45, cw, 4.2, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 2.45, cw, 1.0, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, 2.95, cw, 0.5, fill=col)
        text(s, x + 0.28, 2.52, cw-0.5, 0.45, name + " · " + period, size=13, color=WHITE, bold=True)
        text(s, x + 0.28, 2.96, cw-0.5, 0.45, theme, size=15, color=WHITE, bold=True)
        bullets(s, x + 0.32, 3.65, cw - 0.6, 2.3, items, size=11.5, marker_color=col, gap=9)
        rect(s, x + 0.25, 5.95, cw - 0.5, 0.55, fill=CHIPBG, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x + 0.25, 5.95, cw - 0.5, 0.55, scope, size=11, color=col, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    _footer(s)


# ============================================================================
# 19 一期范围详解
# ============================================================================
def slide_phase1():
    s = add_slide()
    content_header(s, "04  一期落地", "一期范围：以大仓 + 3PL 电商仓试点，跑通“连接 + 可视”")
    cols = [
        ("交付能力", BLUE, [
            "适配器框架 + 2~3 家 WMS / 3PL 接入",
            "标准化模型、编码映射、字典中心",
            "仓内库存聚合 + WMS↔WHC↔OIC 对账",
            "控制塔 V1（全链路可视 + 基础告警）",
            "平台底座：多租户 / 配置 / 消息总线 / 可观测",
        ]),
        ("试点范围", TEAL, [
            "大仓 1 个（自动化设备较多的节点）",
            "3PL 电商仓 1~2 个（含计量数据采集）",
            "对接 OMS / PMS 必要单据与状态",
            "对接 OIC 做库存上报与对账验证",
            "引用 MDM 货品 / 仓网 / 线路与时效",
        ]),
        ("成功标准", AMBER, [
            "新仓接入周期 < 4 周（含联调）",
            "库存对账差异率 < 0.5%，差异可追溯",
            "全链路状态可视，关键节点延迟告警",
            "适配资产沉淀，二期可直接复用",
            "形成厂商接入规范与上线 SOP",
        ]),
    ]
    x = 0.72
    for t, col, its in cols:
        rect(s, x, 1.75, 3.86, 4.95, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, 1.75, 3.86, 0.66, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(s, x, 2.08, 3.86, 0.33, fill=col)
        text(s, x + 0.28, 1.75, 3.4, 0.66, t, size=15, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        bullets(s, x + 0.32, 2.62, 3.35, 3.9, its, size=11.5, marker_color=col, gap=11)
        x += 4.05
    text(s, 0.72, 6.78, 12, 0.4, "原则：单仓灰度、小步快跑、先难后易（先啃自动化复杂的大仓与多结算的 3PL，沉淀通用能力）。",
         size=11, color=GRAY)
    _footer(s)


# ============================================================================
# 20 治理与组织保障
# ============================================================================
def slide_governance():
    s = add_slide()
    content_header(s, "04  治理保障", "组织与机制：平台团队 + 能力域 Owner + 厂商接入规范")
    left = [
        ("平台团队（Platform）", BLUE, "负责适配框架、平台底座、标准模型与开放平台；保障稳定性与可演进。"),
        ("能力域 Owner（Domain）", TEAL, "按 10 大能力域设负责人，负责能力规划、策略沉淀与跨仓推广。"),
        ("仓侧 BizOps", AMBER, "对接各仓与 3PL，负责接入实施、灰度切换与运营反馈。"),
    ]
    y = 1.8
    for t, col, d in left:
        rect(s, 0.72, y, 6.0, 1.32, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, 0.72, y, 0.12, 1.32, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, 1.0, y + 0.16, 5.5, 0.45, t, size=14, color=INK, bold=True)
        text(s, 1.0, y + 0.62, 5.5, 0.65, d, size=11, color=GRAY, line_spacing=1.2)
        y += 1.5
    # 右：机制
    rect(s, 6.95, 1.8, 5.65, 4.5, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 7.25, 1.98, 5.2, 0.4, "关键机制", size=14.5, color=CYAN, bold=True)
    bullets(s, 7.25, 2.5, 5.2, 3.6, [
        ("厂商接入规范：", "标准协议/报文/字段/SLA 准入清单"),
        ("能力准入评审：", "新能力上移前评估边界与复用性"),
        ("标准变更管理：", "状态/事件/编码版本化与兼容策略"),
        ("灰度与回滚：", "按仓灰度、可观测、可快速回滚"),
        ("数据一致性例会：", "对账差异闭环与根因治理"),
        ("中台协同机制：", "与 OMS/PMS/OIC/MDM 边界对齐与联调"),
    ], size=11.3, color=WHITE, marker_color=CYAN, gap=9)
    _footer(s)


# ============================================================================
# 21 KPI 与 ROI
# ============================================================================
def slide_kpi():
    s = add_slide()
    content_header(s, "04  价值度量", "KPI 与 ROI：标准化提效、协同增效、运营降本")
    kpis = [
        ("新仓/厂商接入周期", "数月", "< 4 周", BLUE),
        ("库存对账差异率", "人工/不可控", "< 0.5%", TEAL),
        ("跨仓缺货改派", "人工协调", "自动改派", VIOLET),
        ("3PL 对账人力", "高人工", "↓ 60%+", AMBER),
        ("全链路可视覆盖", "分散黑盒", "100% 可视", CYAN),
        ("通用能力复用率", "重复建设", "一次建设多仓复用", INDIGO),
    ]
    cw, ch, gx, gy = 3.86, 1.62, 0.22, 0.28
    x0, y0 = 0.72, 1.85
    for i, (name, before, after, col) in enumerate(kpis):
        r, c = divmod(i, 3)
        x = x0 + c*(cw+gx); y = y0 + r*(ch+gy)
        rect(s, x, y, cw, ch, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, y, cw, 0.1, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x + 0.3, y + 0.22, cw - 0.5, 0.45, name, size=12.5, color=INK, bold=True)
        text(s, x + 0.3, y + 0.78, 1.6, 0.6, before, size=11, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 1.85, y + 0.82, 0.4, 0.5, "→", size=14, color=col, bold=True)
        text(s, x + 2.2, y + 0.78, cw - 2.4, 0.6, after, size=14, color=col, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        x += 0
    rect(s, 0.72, 5.95, 11.9, 0.92, fill=CHIPBG, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 1.0, 5.95, 11.4, 0.92,
         "ROI 逻辑：标准化降低集成与维护成本、能力上移避免重复建设、自动调度提升时效与产能、对账自动化释放人力；"
         "随接入仓数增加，平台边际成本递减、价值递增。",
         size=11.5, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
    _footer(s)


# ============================================================================
# 22 风险与应对
# ============================================================================
def slide_risks():
    s = add_slide()
    content_header(s, "04  风险管理", "主要风险与应对：提前识别、分级管控")
    risks = [
        ("厂商配合度", "WMS/3PL 厂商接口能力与配合不足", "制定接入规范作为准入；提供标准 SDK 与文档；合同约束", CORAL),
        ("数据一致性", "多源库存/状态口径不一致导致差异", "事件+快照双保险；对账引擎；差异分级自愈与例会闭环", AMBER),
        ("边界蔓延", "WHC 越界重建 OIC/PMS/OMS 能力", "明确边界红线；能力准入评审；架构看护", VIOLET),
        ("组织协同", "跨中台/跨仓协同与责任不清", "能力域 Owner 制；中台协同机制；RACI 明确", BLUE),
        ("演进与替换", "厂商 WMS 替换/能力上移影响业务", "渐进灰度；双轨并行；可回滚；试点先行", TEAL),
        ("性能与稳定", "大促峰值下编排/对账压力", "异步化+削峰；限流熔断；容量规划与压测", INDIGO),
    ]
    cw, ch, gx, gy = 3.86, 1.95, 0.22, 0.28
    x0, y0 = 0.72, 1.85
    for i, (name, risk, fix, col) in enumerate(risks):
        r, c = divmod(i, 3)
        x = x0 + c*(cw+gx); y = y0 + r*(ch+gy)
        rect(s, x, y, cw, ch, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
        rect(s, x, y, 0.12, ch, fill=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x + 0.32, y + 0.16, cw - 0.5, 0.4, "⚠ " + name, size=13, color=col, bold=True)
        text(s, x + 0.32, y + 0.62, cw - 0.55, 0.6, risk, size=10.3, color=INK, line_spacing=1.15)
        text(s, x + 0.32, y + 1.28, cw - 0.55, 0.6, "应对：" + fix, size=10, color=GRAY, line_spacing=1.15)
    _footer(s)


# ============================================================================
# 23 总结与下一步
# ============================================================================
def slide_summary():
    s = add_slide()
    bg(s, NAVY)
    rect(s, 0.0, 0.0, 0.28, 7.5, fill=CYAN)
    text(s, 0.9, 0.85, 11, 0.4, "SUMMARY", size=13, color=CYAN, bold=True)
    text(s, 0.88, 1.2, 11.5, 0.9, "总结与下一步", size=32, color=WHITE, bold=True)
    pts = [
        ("一个定位", "WHC = ERP/中台 与 WMS 之间的“仓库调度大脑”，A→B 渐进式演进为平台化 WMS。"),
        ("四条边界", "OMS/PMS 管订单、OIC 管渠道库存、MDM 管货品/仓网/线路时效，WHC 管执行编排+标准化+物理库存真相+调度。"),
        ("十大能力", "接入适配 / 双链路编排 / 库存一致性 / 作业调度 / 标准化 / 承运 / 3PL计费 / 控制塔 / 数据智能 / 平台治理。"),
        ("三期落地", "0-6 月连得上看得见（大仓+3PL电商仓）→ 6-12 月调得动对得准（FC）→ 12-18 月提得效变聪明（门店/云仓）。"),
    ]
    y = 2.45
    for t, d in pts:
        rect(s, 0.9, y, 0.12, 0.95, fill=CYAN, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, 1.2, y + 0.02, 2.2, 0.9, t, size=16, color=AMBER, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 3.3, y, 9.0, 0.95, d, size=12.5, color=RGBColor(0xD7,0xE2,0xF2), anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
        y += 1.02
    rect(s, 0.9, 6.55, 11.5, 0.55, fill=NAVY2, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 1.15, 6.55, 11.2, 0.55, "下一步：确认一期范围与试点仓 → 组建平台团队与能力域 Owner → 启动适配框架与标准模型设计。",
         size=12, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    _footer(s)


# ============================================================================
# 24 结束页
# ============================================================================
def slide_end():
    s = add_slide()
    bg(s, NAVY)
    rect(s, 9.4, 3.0, 5.5, 5.5, fill=NAVY2, shape=MSO_SHAPE.OVAL)
    rect(s, 0.0, 0.0, 0.28, 7.5, fill=CYAN)
    text(s, 0.9, 2.7, 11, 1.2, "Thank You", size=46, color=WHITE, bold=True)
    text(s, 0.95, 3.95, 11, 0.6, "WHC 仓库调度平台 · 平台化建设规划", size=18, color=RGBColor(0x9F,0xC4,0xEC))
    rect(s, 0.98, 4.75, 1.5, 0.1, fill=AMBER)
    text(s, 0.95, 5.0, 11, 0.4, "欢迎就能力边界、分期范围与试点方案进一步共创。", size=12.5, color=RGBColor(0x8F,0xA6,0xC6))


# ============================================================================
# 装配
# ============================================================================
def build():
    slide_cover()
    slide_agenda()
    section_divider("01", "BACKGROUND & POSITIONING", "背景、挑战与平台定位",
                    "多 WMS 痛点 · A→B 渐进式定位 · 四大中台边界")
    slide_background()
    slide_painpoints()
    slide_positioning()
    slide_boundary()
    slide_principles()
    section_divider("02", "CAPABILITY MAP", "WHC 平台化能力地图",
                    "10 大一级能力域 · L1 / L2 / L3 能力分解")
    slide_capability_overview()
    slide_capability_detail("能力详解（一）：接入适配 · 双链路编排 · 库存一致性", [0, 1, 2])
    slide_capability_detail("能力详解（二）：作业调度 · 标准化映射 · 承运配送", [3, 4, 5])
    slide_capability_detail("能力详解（三）：3PL计费 · 控制塔 · 数据智能 · 平台治理", [6, 7, 8, 9])
    section_divider("03", "ARCHITECTURE & DESIGN", "总体技术架构与核心设计",
                    "分层架构 · 适配层 · 双链路调度 · 库存一致性 · 集成")
    slide_architecture()
    slide_adapter()
    slide_orchestration()
    slide_inventory()
    slide_standardization()
    slide_integration()
    section_divider("04", "ROADMAP & GOVERNANCE", "建设路线图与保障",
                    "三期 18 个月 · 治理组织 · KPI/ROI · 风险")
    slide_roadmap()
    slide_phase1()
    slide_governance()
    slide_kpi()
    slide_risks()
    slide_summary()
    slide_end()
    out = "WHC仓库调度平台_平台化规划方案.pptx"
    prs.save(out)
    print("saved:", out, "slides:", len(prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
