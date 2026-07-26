# -*- coding: utf-8 -*-
"""一品多区备货 —— 业务需求评审与系统落地方案"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_deck_lib import *   # noqa

prs = new_deck()
IDX = [0]


def page(title, kicker=None, sub=None, note=None):
    s = blank(prs)
    IDX[0] += 1
    y = slide_title(s, title, kicker, sub)
    footer(s, IDX[0], note)
    return s, y


# ============================================================ 封面
s = blank(prs)
bar(s, Emu(0), Emu(0), SW, SH, INK)
bar(s, Emu(0), Emu(0), Inches(0.11), SH, BLUE)
_, tf = textbox(s, Inches(1.15), Inches(2.35), Inches(9.4), Inches(0.4))
write(tf, [("方案评审 · WAREHOUSE SLOTTING", dict(size=12, bold=True,
      color=RGBColor(0x7E, 0xA6, 0xF5), font=FONT_EN))], first=True, space_after=0)
_, tf = textbox(s, Inches(1.15), Inches(2.92), Inches(10.6), Inches(1.0))
write(tf, [("一品多区备货", dict(size=46, bold=True, color=WHITE))], first=True, space_after=0)
_, tf = textbox(s, Inches(1.15), Inches(3.95), Inches(10.6), Inches(0.5))
write(tf, [("业务需求评审与系统落地方案", dict(size=20, color=RGBColor(0xC3, 0xCF, 0xDE)))],
      first=True, space_after=0)
bar(s, Inches(1.15), Inches(4.72), Inches(1.1), Pt(3), BLUE)
_, tf = textbox(s, Inches(1.15), Inches(5.08), Inches(10.6), Inches(0.9))
write(tf, [("电商仓 · AGV 料箱区 × 人工分区   |   10 仓 · 单仓 1.5 万单/日 · 峰值 2×",
            dict(size=13, color=RGBColor(0x92, 0xA3, 0xB8)))], first=True, space_after=6)
write(tf, [("2026-07", dict(size=12, color=RGBColor(0x6B, 0x7C, 0x93), font=FONT_EN))], space_after=0)

# ============================================================ 执行摘要
s, y = page("执行摘要", "EXECUTIVE SUMMARY", "五个核心判断,决定这个需求怎么做、做到哪一层")
rows = [
    ("01", "需求本质是「拆单从查表变成决策」", BLUE, BLUE_BG,
     "难点从来不是「一个 SKU 放多个库位」——WMS 库位模型天然支持。真正新增的是:同一 SKU 存在于多区时,「从哪个区扣、哪个区拣」成为一个带约束的分配决策。全部系统复杂度都源于此。"),
    ("02", "80/20 不该拍脑袋,应该被算出来", PURPLE, PURPLE_BG,
     "比例的正确形态是 Slotting 引擎的输出:各区目标库存 = 该区所服务订单流的需求 × 补货覆盖周期 + 安全库存。比例设错的代价是区间互补货不降反升。"),
    ("03", "分区是「效率分区」,不是「库存隔离」", AMBER, AMBER_BG,
     "中台已按 SKU 总量向客户承诺。因此分区只决定「从哪拣」,绝不能决定「能不能履约」——任何分区规则都不得使可履约总量低于中台承诺量。各区互为兜底。"),
    ("04", "架构:WHC 定规则出建议,WMS 终裁绑库位", GREEN, GREEN_BG,
     "分配算法本身存在天然分界:前 4 步只依赖主数据/配置/订单自身,后 2 步必须与实时库存和设备同地。控制面上移平台、数据面留在本地,不是折中而是顺着算法切。"),
    ("05", "最大的新增风险在运营,不在架构", RED, RED_BG,
     "一品多区后总量仍与中台对平,但分区级账实不符中台对账查不出来,却会直接导致首选区命中失败→改派→时效恶化。分区级盘点与命中率监控是上线前置条件。"),
]
yy, rh, gap = y + Inches(0.02), Inches(0.88), Inches(0.11)
for num, ttl, ac, bg, desc in rows:
    sp = rect(s, M, yy, CW, rh, fill=bg, line_color=None)
    bar(s, M, yy, Pt(3.2), rh, ac)
    _, ntf = textbox(s, M + Inches(0.20), yy + Inches(0.17), Inches(0.55), Inches(0.5))
    write(ntf, [(num, dict(size=21, bold=True, color=ac, font=FONT_EN))], first=True, space_after=0)
    _, ttf = textbox(s, M + Inches(0.86), yy + Inches(0.11), CW - Inches(1.1), Inches(0.72))
    write(ttf, [(ttl, dict(size=14, bold=True, color=INK))], first=True, space_after=3)
    write(ttf, [(desc, dict(size=10.5, color=INK2))], space_after=0, line=1.2)
    yy += rh + gap

# ============================================================ PART 1
IDX[0] += 1
section_divider(prs, IDX[0], 1, "命题再审视", "先把「要解决什么问题」定准,再谈方案",
                ["现状盘点:业务与系统两条线", "需求本质:确定性拆单 → 决策性分配", "价值论证:四项收益与其成立条件"])

# ---- 现状盘点
s, y = page("现状盘点", "CONTEXT", "业务侧与系统侧各自的既有约束,是后续所有设计的边界条件")
cw2 = (CW - Inches(0.32)) / 2
card(s, M, y, cw2, Inches(2.42), "业务现状", [
    "10 个电商仓;单仓日均 1.5 万单,节假日订单量翻倍",
    "客单平均 6.7 件,299 包邮 —— 多行订单是常态",
    "一品一区:食品区 / 化学品区 / AGV 区,SKU→区 一一映射",
    "分区拣货、独立包裹出库,仓内不集单",
    "集单在物流工作站完成(OFC 前置面单 + 子单运单绑定,快递站聚合),已在生产运行",
    "高峰方案:租外仓承接高流 SKU,仍是一品一区",
], accent=SLATE, bg=SLATE_BG)
card(s, M + cw2 + Inches(0.32), y, cw2, Inches(2.42), "系统现状", [
    "链路:APP(渠道) → OMS(销售单) → OFC(履约单) → WHC(转发出库单) → WMS",
    "APP 预占的是中台库存(SKU 总量口径),与 WMS 定期对账,双方准确性高",
    "WMS 接单不预占;分货拆单后进入波次,才开始分配库存",
    "WHC 定位为平台化 WMS;WMS 为 3PL 所有,核心能力有上移诉求",
], accent=BLUE, bg=BLUE_BG)

yy = y + Inches(2.62)
sp = rect(s, M, yy, CW, Inches(2.28), fill=WHITE, line_color=LINE)
tf = sp.text_frame
write(tf, [("三条必须被尊重的既有设计", dict(size=13.5, bold=True, color=INK))], first=True, space_after=7)
for t, d in [
    ("WMS「接单不预占 + 波次晚绑定」是刻意设计,不是缺陷",
     "晚绑定才能让 WMS 在波次阶段做批量优化——合波、拣货路径、设备负载均衡、就近库位。任何把库存提前锁死的方案,都是在牺牲这个核心优化。这是评判所有架构路径的标尺。"),
    ("中台库存只认 SKU 总量,不感知「区」",
     "一品多区不改变任何 SKU 的总量,因此中台预占逻辑、中台↔WMS 对账链路 零改动。这是本需求最有利的边界条件。"),
    ("包裹聚合已在物流工作站解决,且已上生产",
     "「多区 = 多包裹」在下游已经不是问题。这解除了本需求最常被担心的一项成本约束。"),
]:
    write(tf, [("▸ ", dict(size=11, bold=True, color=BLUE)),
               (t, dict(size=11.5, bold=True, color=INK))], space_after=2, line=1.2)
    write(tf, [("   " + d, dict(size=10.5, color=INK2))], space_after=6, line=1.2)

# ---- 需求本质
s, y = page("需求本质:从「查表」到「决策」", "PROBLEM FRAMING",
            "这是判断工作量、划分系统边界、评估风险的唯一正确起点")
cw2 = (CW - Inches(0.5)) / 2
h1 = Inches(2.35)
sp = rect(s, M, y, cw2, h1, fill=SLATE_BG, line_color=None)
bar(s, M, y, Pt(3.2), h1, SLATE)
tf = sp.text_frame
write(tf, [("现状 · 一品一区", dict(size=10, bold=True, color=SLATE, font=FONT_EN))],
      first=True, space_after=4)
write(tf, [("SKU → 区  一一映射", dict(size=16, bold=True, color=INK))], space_after=8)
for t in ["拆单 = 一次查表,输入确定则输出确定",
          "无并发竞争:不存在两个区争抢同一 SKU",
          "无改派概念:只有一个区,拣不到就是缺货",
          "分区库存精度 ≡ 总量精度,中台对账即可覆盖"]:
    write(tf, [("· ", dict(size=11, bold=True, color=SLATE)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

sp = rect(s, M + cw2 + Inches(0.5), y, cw2, h1, fill=BLUE_BG, line_color=None)
bar(s, M + cw2 + Inches(0.5), y, Pt(3.2), h1, BLUE)
tf = sp.text_frame
write(tf, [("目标 · 一品多区", dict(size=10, bold=True, color=BLUE, font=FONT_EN))],
      first=True, space_after=4)
write(tf, [("SKU → {区A, 区B}  一对多", dict(size=16, bold=True, color=INK))], space_after=8)
for t in ["拆单 = 带约束的分配决策,需要规则与优先级",
          "产生并发竞争:多订单争抢同一区的同一 SKU",
          "产生改派:首选区拣不到,需顺位回退到次选区",
          "分区精度成为独立失效模式,中台对账查不出"]:
    write(tf, [("· ", dict(size=11, bold=True, color=BLUE)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

_, atf = textbox(s, M + cw2 + Inches(0.05), y + Inches(0.95), Inches(0.4), Inches(0.4))
write(atf, [("→", dict(size=24, bold=True, color=LINE, font=FONT_EN))], first=True,
      space_after=0, align=PP_ALIGN.CENTER)

yy = y + h1 + Inches(0.26)
sp = rect(s, M, yy, CW, Inches(1.62), fill=PURPLE_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(1.62), PURPLE)
tf = sp.text_frame
write(tf, [("请注意区分两种「复杂度」", dict(size=13, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("可接受 —— 决策流复杂度:", dict(size=11.5, bold=True, color=PURPLE)),
           ("多了一套规则、一次分区决策、一条只读快照同步。它落在流程上,边界清晰、可测试、可灰度。",
            dict(size=11, color=INK2))], space_after=5, line=1.2)
write(tf, [("不可接受 —— 账本复杂度:", dict(size=11.5, bold=True, color=RED)),
           ("如果引入第二本分区库存账并做实时加减,就必然产生漂移与无止境对账。这是本方案必须绕开的唯一致命陷阱。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 价值论证
s, y = page("为什么要做:四项收益", "VALUE", "前两项是确定性收益,后两项有成立条件——条件写在卡片里")
cw2 = (CW - Inches(0.3)) / 2
ch = Inches(2.35)
card(s, M, y, cw2, ch, "保护 AGV 吞吐(第一收益)", [
    "一个 30 件的大单进入 AGV,会长时间占用料箱与工作站,直接压制整区吞吐",
    "一品多区把大单所需库存常备在人工区,使大单不必、也不会进入 AGV",
    "收益不是「同一件拣得更快」,而是「把会拖垮 AGV 的订单挡在 AGV 之外」",
], accent=GREEN, bg=GREEN_BG, tag="确定性收益")
card(s, M + cw2 + Inches(0.3), y, cw2, ch, "订单分流,各走最优拣选模式", [
    "小单 / 单件 → AGV 货到人,发挥自动化设计能力",
    "大单 / 原箱 → 人工按单拣、按单出库",
    "人工区打包效率有上限,把高频小单移走,人工区产能才用在真正需要它的订单上",
], accent=GREEN, bg=GREEN_BG, tag="确定性收益")

yy = y + ch + Inches(0.18)
card(s, M, yy, cw2, ch, "补货从「应急」变「计划」", [
    "一品一区下,大单往往触发一次 AGV→人工 的按单急搬",
    "一品多区把这部分需求事先备好,消除按单触发的区间搬运",
    ("成立条件:", dict(size=11, bold=True, color=AMBER)),
], accent=AMBER, bg=AMBER_BG, tag="条件性收益")
_, ctf = textbox(s, M + Inches(0.28), yy + Inches(1.78), cw2 - Inches(0.5), Inches(0.5))
write(ctf, [("互补货不会归零。目标是「频次下降 + 可排期到低峰」,补货源优先走储备区/入库直上架,而非区间互搬。",
             dict(size=10.5, color=INK2))], first=True, space_after=0, line=1.18)

card(s, M + cw2 + Inches(0.3), yy, cw2, ch, "真实缺货率下降", [
    "一品一区:那个区拣不到 = 缺货,只能走人工处理",
    "一品多区:一个区拣不到,另一个区可以顶上",
    ("原本的一部分「缺货」被转化为「改派」,履约成功率提升——这是常被忽略的收益。",
     dict(size=10.5, color=INK2)),
], accent=AMBER, bg=AMBER_BG, tag="条件性收益")

# ============================================================ PART 2
IDX[0] += 1
section_divider(prs, IDX[0], 2, "三个关键洞察", "本轮复盘中,对既有认知的三处修正",
                ["包裹数:方向判断需要修正", "80/20:它是输出,不是输入", "分区语义:效率分区 ≠ 库存隔离"])

# ---- 洞察1 包裹数
s, y = page("洞察一:包裹数不是风险项,反而是收益项", "INSIGHT 01",
            "这是对「多区→多包裹→成本上升」这一直觉判断的修正")
sp = rect(s, M, y, CW, Inches(1.0), fill=RED_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(1.0), RED)
tf = sp.text_frame
write(tf, [("直觉判断(需要修正)", dict(size=11, bold=True, color=RED))], first=True, space_after=4)
write(tf, [("同一 SKU 分散到多区 → 订单被拆到更多区 → 包裹数上升 → 运费与体验恶化。",
            dict(size=12, color=INK2))], space_after=0, line=1.2)

yy = y + Inches(1.2)
sp = rect(s, M, yy, CW, Inches(2.28), fill=GREEN_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(2.28), GREEN)
tf = sp.text_frame
write(tf, [("实际结论", dict(size=11, bold=True, color=GREEN))], first=True, space_after=5)
write(tf, [("在客单 6.7 件的前提下,订单本来就已经是跨区的。", dict(size=13.5, bold=True, color=INK))],
      space_after=7)
for t in [
    "一品一区下,一张 6.7 件的订单横跨食品区、化学品区、AGV 区是常态——区数是被 SKU 摆放「强制」决定的,分配器没有任何选择权。",
    "一品多区后,若某 SKU 同时存在于 AGV 区与人工区,分配器第一次获得了自由度:可以主动把它拉到订单其余行已经落到的那个区。",
    "因此在「方案 B(整行落单区)+ 显式的区数最小化目标」下,一品多区是 减少 而非增加订单的跨区数。",
    "叠加物流工作站集单已上生产,下游对多包裹本就不敏感。",
]:
    write(tf, [("· ", dict(size=11, bold=True, color=GREEN)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

yy += Inches(2.48)
sp = rect(s, M, yy, CW, Inches(1.05), fill=WHITE, line_color=LINE)
tf = sp.text_frame
write(tf, [("对方案的要求", dict(size=11.5, bold=True, color=INK))], first=True, space_after=4)
write(tf, [("收益不会自动发生。必须在分配规则中把「订单跨区数最小化」写成一个显式的优化目标(算法第 4 步),否则分配器会各行独立选区,收益归零。同时把 ",
            dict(size=11, color=INK2)),
           ("单均包裹数", dict(size=11, bold=True, color=INK)),
           (" 纳入上线前后对比指标。", dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 洞察2 80/20
s, y = page("洞察二:80/20 是算出来的,不是定出来的", "INSIGHT 02",
            "业务应交付的是「怎么算」,而不是一个静态常数")
cw2 = (CW - Inches(0.3)) / 2
sp = rect(s, M, y, cw2, Inches(2.5), fill=PURPLE_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(2.5), PURPLE)
tf = sp.text_frame
write(tf, [("正确的形态", dict(size=11, bold=True, color=PURPLE))], first=True, space_after=6)
write(tf, [("每个区的目标库存,应覆盖「它所服务的那股订单流」在补货周期内的需求。",
            dict(size=11.5, color=INK2))], space_after=8, line=1.2)
for lbl, formula in [
    ("人工区目标库存", "= 大单日均需求 × 覆盖天数 + 安全库存"),
    ("AGV 区目标库存", "= 小单日均需求 × 覆盖天数 + 安全库存"),
]:
    write(tf, [(lbl, dict(size=11, bold=True, color=INK))], space_after=1)
    write(tf, [("  " + formula, dict(size=11, color=PURPLE, font=FONT_EN))], space_after=6)
write(tf, [("80 / 20 只是上式的结果比值。它逐 SKU 不同,并随季节、促销、订单结构变化。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

card(s, M + cw2 + Inches(0.3), y, cw2, Inches(2.5), "如果按常数拍死,会发生什么", [
    "比例与真实的大单/小单需求结构不匹配",
    "某一区先见底,另一区仍有富余",
    "触发区间互补货 —— 恰恰是本需求想消除的动作",
    ("结论:比例设错时,一品多区不但拿不到收益,还会让互补货比现在更多。",
     dict(size=11, bold=True, color=RED)),
], accent=RED, bg=RED_BG)

yy = y + Inches(2.7)
sp = rect(s, M, yy, CW, Inches(1.62), fill=WHITE, line_color=LINE)
tf = sp.text_frame
write(tf, [("对业务与系统的分工要求", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("业务方交付:", dict(size=11, bold=True, color=BLUE)),
           ("大单/小单的判定口径、补货覆盖天数、安全库存策略、重算频率(建议周度 + 大促前专项)。",
            dict(size=11, color=INK2))], space_after=5, line=1.2)
write(tf, [("系统方交付:", dict(size=11, bold=True, color=GREEN)),
           ("Slotting 计算能力。一期可先支持「人工配置比例 + 系统校验偏离度」,二期再上自动测算与动态调整。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 洞察3 效率分区
s, y = page("洞察三:分区是效率分区,不是库存隔离", "INSIGHT 03",
            "这条决定了缺货、改派、可售量三者的语义,是全案的底层约束")
sp = rect(s, M, y, CW, Inches(1.42), fill=AMBER_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(1.42), AMBER)
tf = sp.text_frame
write(tf, [("一个必须被回答的场景", dict(size=11, bold=True, color=AMBER))], first=True, space_after=5)
write(tf, [("一张小单进来,AGV 区该 SKU 已空,而人工区还有 20% 的库存。这 20% 是「给大单备的」——那么,让不让这张小单拿?",
            dict(size=12.5, bold=True, color=INK))], space_after=5, line=1.22)
write(tf, [("若答「不让」:客户的订单在 APP 下单时已由中台按 SKU 总量预占并承诺。拒绝发货 = 系统自己制造了一次本不该发生的履约失败。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

yy = y + Inches(1.62)
cw2 = (CW - Inches(0.3)) / 2
sp = rect(s, M, yy, cw2, Inches(2.35), fill=INK, line_color=None)
tf = sp.text_frame
write(tf, [("铁律", dict(size=10.5, bold=True, color=RGBColor(0x7E, 0xA6, 0xF5), font=FONT_EN))],
      first=True, space_after=6)
for t in ["分区只决定「从哪拣」,不决定「能不能履约」",
          "任何分区规则,不得使可履约总量 < 中台已承诺总量",
          "各区互为兜底;优先级只决定顺序,不决定可达性",
          "「区内缺货」不是缺货,是改派;只有全区皆无才是真缺货"]:
    write(tf, [("— ", dict(size=11.5, bold=True, color=RGBColor(0x7E, 0xA6, 0xF5))),
               (t, dict(size=11.5, color=WHITE))], space_after=7, line=1.2)

card(s, M + cw2 + Inches(0.3), yy, cw2, Inches(2.35), "由此推导出的三个设计结论", [
    "「全部缺货」应重新定义为「所有区皆无」。这类事件一旦发生,同时意味着中台↔WMS 账实出现偏差,应触发库存核查,而不只是转人工。",
    "预留(reservation)语义不引入。20% 是摆放目标,不是被锁住的份额。",
    "分区不减少可售量 ⇒ 中台预占逻辑、对账链路完全不动。这正是本需求上游改造量极小的根因。",
], accent=GREEN, bg=GREEN_BG)

# ============================================================ PART 3
IDX[0] += 1
section_divider(prs, IDX[0], 3, "业务方案", "把规则定义清楚,系统才有可能落地",
                ["待补充信息清单与已澄清项", "大单判定的循环依赖与解法", "分配算法六步法", "补货体系与指标体系"])

# ---- 待补充信息
s, y = page("业务待补充信息清单", "REQUIREMENTS",
            "业务要交付的不是「80/20」这个数字,而是下列八组规则")
headers = ["#", "信息项", "状态", "内容 / 待明确点"]
rows = [
    ["1", "目的与优先级", "已明确", "提升 AGV 吞吐与利用率、保障高效正常履约、减少区间互补货"],
    ["2", "比例的性质", "需转化", "应从「静态 80/20」转为「按大单/小单需求结构测算」——见洞察二"],
    ["3", "选区优先级", "已明确", "按订单属性驱动:大单(同区 ≥30 件)→ 人工区按单拣;小单 → AGV"],
    ["4", "是否跨区拆行", "已明确", "一期方案 B:规则计算后整行落单区;方案 A(跨区拆行)二期评估"],
    ["5", "包裹与成本取舍", "已解除", "集单已在物流工作站/快递站完成,下游不构成约束"],
    ["6", "SKU×区 约束", "已明确", "商品主数据「是否上机」标识,人工维护"],
    ["7", "缺货降级", "已明确", "部分缺量 → 紧急补货;全部缺货 → 标记转人工(沟通取消 / 补货后发)"],
    ["8", "指标口径与基线", "待补充", "需在上线前完成基线采集,否则无法验证收益 —— 见指标体系页"],
]
cc = {}
for i, r in enumerate(rows):
    st = r[2]
    col = {"已明确": (GREEN_BG, GREEN, True), "已解除": (GREEN_BG, GREEN, True),
           "需转化": (AMBER_BG, AMBER, True), "待补充": (RED_BG, RED, True)}[st]
    cc[(i, 2)] = col
kv_table(s, M, y + Inches(0.04), CW, headers, rows, [0.5, 2.3, 1.1, 8.4],
         row_h=Inches(0.46), font_size=10.5, cell_colors=cc)

yy = y + Inches(0.04) + Inches(0.40) + Inches(0.46) * 8 + Inches(0.16)
sp = rect(s, M, yy, CW, Inches(0.72), fill=AMBER_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(0.72), AMBER)
tf = sp.text_frame
write(tf, [("新增待澄清项:", dict(size=11, bold=True, color=AMBER)),
           ("① 大单阈值「30 件」的计数口径 —— 商品件数 / 拣选行数 / 原箱按箱还是按件?  ② 外仓的定位 —— 独立仓(走跨仓寻源)还是本仓的溢出储区(走仓内分区)?这决定它接在哪一层。",
            dict(size=10.5, color=INK2))], first=True, space_after=0, line=1.2)

# ---- 大单判定循环依赖
s, y = page("大单判定存在循环依赖,需两阶段求解", "RULE DESIGN",
            "「同分区 30 件为大单」——但分区本身正是待决策的结果")
sp = rect(s, M, y, CW, Inches(0.95), fill=RED_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(0.95), RED)
tf = sp.text_frame
write(tf, [("循环点", dict(size=11, bold=True, color=RED))], first=True, space_after=4)
write(tf, [("要统计「同区件数」,必须先知道每行落在哪个区;而要决定落在哪个区,又必须先知道它是不是大单。规则不能直接执行。",
            dict(size=11.5, color=INK2))], space_after=0, line=1.2)

yy = y + Inches(1.15)
cw3 = (CW - Inches(0.44)) / 3
for i, (num, ttl, desc, ac, bg) in enumerate([
    ("1", "预分区", "仅用 SKU 级硬属性:是否上机、区 SKU 白名单,加默认区偏好,得到每行的候选区,并按候选区分组。此步不看件数。", BLUE, BLUE_BG),
    ("2", "大单判定", "对每个候选区分组统计件数。≥ 阈值的分组整体改判为「人工区 · 按单拣货按单出库」。此步不看库存。", PURPLE, PURPLE_BG),
    ("3", "库存校验与终裁", "在 WMS 侧按分区实时可用量校验,不足则按优先级序列顺位回退,最终绑定到库位。", GREEN, GREEN_BG),
]):
    x = M + (cw3 + Inches(0.22)) * i
    chevron(s, x, yy, cw3, Inches(1.72), num, ttl, desc, ac, bg)

yy += Inches(1.92)
sp = rect(s, M, yy, CW, Inches(1.62), fill=WHITE, line_color=LINE)
tf = sp.text_frame
write(tf, [("两条必须写进规格的细则", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("阈值口径必须唯一且可计算:", dict(size=11, bold=True, color=BLUE)),
           ("「件」是商品件数还是拣选行数?原箱商品按箱计还是按内装件数计?口径不同,同一张订单的判定结果会完全相反。",
            dict(size=11, color=INK2))], space_after=5, line=1.2)
write(tf, [("阶段 2 的判定结果不可被阶段 3 推翻:", dict(size=11, bold=True, color=GREEN)),
           ("若大单因库存不足需要回退,回退目标仍应是「按单拣」的区,而不是把大单塞回 AGV——否则第一收益(保护 AGV 吞吐)就被破坏了。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 两类路由信号
s, y = page("两类路由信号必须分层,不能合并", "RULE DESIGN",
            "把 SKU 级硬约束和订单级软规则混成一个字段,是这类需求最常见的设计事故")
cw2 = (CW - Inches(0.3)) / 2
h = Inches(2.62)
sp = rect(s, M, y, cw2, h, fill=SLATE_BG, line_color=None)
bar(s, M, y, Pt(3.2), h, SLATE)
tf = sp.text_frame
write(tf, [("信号 A · SKU 级 · 硬约束", dict(size=10.5, bold=True, color=SLATE, font=FONT_EN))],
      first=True, space_after=5)
write(tf, [("是否上机 / 原箱属性", dict(size=15, bold=True, color=INK))], space_after=7)
for t in ["来源:商品主数据,人工维护,长期稳定",
          "语义:决定这个 SKU 「能不能」进 AGV",
          "作用:过滤候选区集合 —— 不满足即从候选中剔除",
          "特性:与订单无关,可全量预计算并缓存"]:
    write(tf, [("· ", dict(size=11, bold=True, color=SLATE)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

sp = rect(s, M + cw2 + Inches(0.3), y, cw2, h, fill=PURPLE_BG, line_color=None)
bar(s, M + cw2 + Inches(0.3), y, Pt(3.2), h, PURPLE)
tf = sp.text_frame
write(tf, [("信号 B · 订单级 · 软规则", dict(size=10.5, bold=True, color=PURPLE, font=FONT_EN))],
      first=True, space_after=5)
write(tf, [("大单判定(同区 ≥ 30 件)", dict(size=15, bold=True, color=INK))], space_after=7)
for t in ["来源:订单自身的件数结构,逐单动态计算",
          "语义:决定这个 SKU 「该不该」进 AGV",
          "作用:调整候选区的优先级顺序,不删除候选",
          "特性:同一 SKU 在不同订单上结论可以相反"]:
    write(tf, [("· ", dict(size=11, bold=True, color=PURPLE)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

yy = y + h + Inches(0.22)
sp = rect(s, M, yy, CW, Inches(1.05), fill=RED_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(1.05), RED)
tf = sp.text_frame
write(tf, [("合并的后果", dict(size=11, bold=True, color=RED))], first=True, space_after=4)
write(tf, [("若用一个「推荐区」字段同时承载两者,就无法表达「这个 SKU 可以进 AGV,但这一单不该进」。一旦大单场景需要回退,系统会分不清 该区不可用(硬)还是 该区不合适(软),从而把大单错误地回退进 AGV,直接摧毁第一收益。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 六步法
s, y = page("分配算法六步法", "ALGORITHM",
            "每一步右下角标注其数据依赖 —— 这直接决定了系统边界怎么切")
steps = [
    ("1", "候选区过滤", "按 是否上机、区 SKU 白名单,剔除物理上不可行的区", "主数据", BLUE, BLUE_BG),
    ("2", "预分区", "按区偏好规则给出每行的初始候选区,并按区分组", "配置", BLUE, BLUE_BG),
    ("3", "大单判定", "按候选分组统计件数,≥ 阈值整组改判人工区按单拣", "订单自身", BLUE, BLUE_BG),
    ("4", "集中度优化", "对多候选行,优先并入订单其余行已落的区,最小化跨区数", "订单自身", BLUE, BLUE_BG),
    ("5", "库存校验与终裁", "校验分区实时可用量,不足则按优先级序列顺位回退", "实时库存", GREEN, GREEN_BG),
    ("6", "波次与库位绑定", "结合设备负载、拣货路径,晚绑定到具体库位", "实时库存 + 设备", GREEN, GREEN_BG),
]
cw3 = (CW - Inches(0.44)) / 3
for i, (num, ttl, desc, dep, ac, bg) in enumerate(steps):
    col, row = i % 3, i // 3
    x = M + (cw3 + Inches(0.22)) * col
    yy = y + Inches(0.02) + row * (Inches(1.62) + Inches(0.18))
    sp = rect(s, x, yy, cw3, Inches(1.62), fill=bg, line_color=None)
    bar(s, x, yy, Pt(3.2), Inches(1.62), ac)
    tf = sp.text_frame
    write(tf, [(f"STEP {num}", dict(size=9, bold=True, color=ac, font=FONT_EN))], first=True, space_after=3)
    write(tf, [(ttl, dict(size=12.5, bold=True, color=INK))], space_after=4)
    write(tf, [(desc, dict(size=10.5, color=INK2))], space_after=5, line=1.18)
    write(tf, [("依赖:", dict(size=9.5, color=MUTED)), (dep, dict(size=9.5, bold=True, color=ac))],
          space_after=0)

yy = y + Inches(0.02) + 2 * (Inches(1.62) + Inches(0.18)) + Inches(0.06)
sp = rect(s, M, yy, CW, Inches(1.08), fill=INK, line_color=None)
tf = sp.text_frame
write(tf, [("算法本身给出了系统边界", dict(size=12.5, bold=True, color=WHITE))], first=True, space_after=5)
write(tf, [("步骤 1–4 只依赖 主数据 / 配置 / 订单自身,与实时库存无关 —— 可以在平台侧(WHC)完成。",
            dict(size=11, color=RGBColor(0x9E, 0xC0, 0xFA)))], space_after=3, line=1.2)
write(tf, [("步骤 5–6 必须与实时库存和设备状态同地 —— 必须留在 WMS。这不是妥协,是顺着算法的天然分界线切。",
            dict(size=11, color=RGBColor(0x8E, 0xDC, 0xBE)))], space_after=0, line=1.2)

# ============================================================ PART 4
IDX[0] += 1
section_divider(prs, IDX[0], 4, "系统方案", "控制面上移平台,数据面留在本地",
                ["三条架构路径的对比与取舍", "量级测算:为什么路径 1 不可行", "推荐架构与关键接口", "库存账本的唯一性原则"])

# ---- 三路径
s, y = page("三条架构路径对比", "ARCHITECTURE",
            "核心矛盾:决策在平台、不提前预占、高频下不产生大量改派 —— 三者只能取其二")
headers = ["", "路径 1 · WHC 锁表预占", "路径 2 · WMS 全做", "路径 3 · WHC 定规则,WMS 执行"]
rows = [
    ["做法", "WMS 提供实时分区库存,WHC 调用并锁定预占,账本仍在 WMS",
     "分区规则与执行全部由各仓 3PL WMS 自行实现", "WHC 版本化下发规则并出建议序列,WMS 终裁绑定与改派"],
    ["优势", "决策有预占背书,不漂移,改派少", "决策与执行同地,无时间窗,晚绑定完整保留,本地锁最稳",
     "规则平台统一 + 运行时本地执行,战略与性能兼得"],
    ["代价", "违背晚绑定,牺牲波次批量优化;热点 SKU 行锁竞争;WHC 进入库存事务关键路径,需分布式事务补偿",
     "10 仓各写一套,规则不一致、迭代慢、被 3PL 绑定,平台能力无法沉淀",
     "新增规则下发与结果回传链路(复杂度落在决策流,不触账本)"],
    ["结论", "不推荐 · 仅作兜底", "不推荐 · 战略不可接受", "推荐"],
]
cc = {(3, 1): (RED_BG, RED, True), (3, 2): (RED_BG, RED, True), (3, 3): (GREEN_BG, GREEN, True),
      (0, 0): (SLATE_BG, INK, True), (1, 0): (SLATE_BG, INK, True),
      (2, 0): (SLATE_BG, INK, True), (3, 0): (SLATE_BG, INK, True)}
kv_table(s, M, y + Inches(0.1), CW, headers, rows, [0.85, 3.4, 3.0, 3.7],
         row_h=Inches(1.12), head_h=Inches(0.46), font_size=10, cell_colors=cc, zebra=False)

# ---- 量级测算
s, y = page("量级测算:为什么路径 1 不可行", "SIZING",
            "同一份负载,在两种架构下的代价差异 —— 数量级估算,口径见页脚",
            note="估算口径:15,000 单/仓/日 × 6.7 行/单 ≈ 10 万行/日;峰值 2×;按高峰时段集中度折算。实际值需以生产埋点为准。")
cw2 = (CW - Inches(0.3)) / 2
sp = rect(s, M, y, cw2, Inches(2.5), fill=BG_SOFT, line_color=LINE)
tf = sp.text_frame
write(tf, [("负载估算", dict(size=13, bold=True, color=INK))], first=True, space_after=7)
for lbl, val in [("单仓日均行数", "1.5 万单 × 6.7 行 ≈ 10 万行/日"),
                 ("单仓峰值", "≈ 20 万行/日"),
                 ("10 仓峰值合计", "≈ 200 万行/日"),
                 ("折算峰值速率", "约 150 – 200 行/秒(数量级)")]:
    write(tf, [(lbl, dict(size=11, color=MUTED))], space_after=1)
    write(tf, [(val, dict(size=12.5, bold=True, color=INK))], space_after=7)

card(s, M + cw2 + Inches(0.3), y, cw2, Inches(2.5), "同一负载下的两种代价", [
    ("路径 3:", dict(size=11.5, bold=True, color=GREEN)),
    ("纯计算 —— 输入是订单报文 + 缓存的主数据与配置,无跨系统写、无锁。无状态服务水平扩展即可,与仓数线性无关。",
     dict(size=11, color=INK2)),
    ("路径 1:", dict(size=11.5, bold=True, color=RED)),
    ("每行一次跨系统预占调用 + 热点 SKU 上的行锁竞争。大促 2× 时锁等待非线性放大,且需要 TTL 与超时补偿来兜住订单变更。",
     dict(size=11, color=INK2)),
], accent=SLATE, bg=SLATE_BG)

yy = y + Inches(2.7)
sp = rect(s, M, yy, CW, Inches(1.62), fill=RED_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(1.62), RED)
tf = sp.text_frame
write(tf, [("决定性的一点:预占是为了覆盖一个小概率分支,却要付出全量成本",
            dict(size=13, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("在本场景中,选区结论主要由 是否上机(主数据)与 大单判定(订单自身)决定,二者都与实时库存无关。只有「首选区库存不足」这一分支才真正需要实时数据。为这一分支给 100% 的行加锁,是典型的代价错配。",
            dict(size=11, color=INK2))], space_after=6, line=1.2)
write(tf, [("因此建议引入一个可度量的选型依据:", dict(size=11, bold=True, color=RED)),
           ("属性可判定率 = 仅凭主数据与订单属性即可确定唯一目标区的行数占比。该值高 ⇒ 路径 3 明确成立;若显著偏低,才需重新评估。上线前应先用历史订单离线回放测出此值。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 推荐架构
s, y = page("推荐架构:控制面上移,数据面本地", "ARCHITECTURE",
            "WHC 拿到规则定义权与跨仓标准化,WMS 保留实时账本与晚绑定优化")
chain = ["APP 渠道", "OMS 销售单", "OFC 履约单", "WHC 转发出库单", "WMS 执行"]
bwidth = Inches(2.14)
gapx = (CW - bwidth * 5) / 4
for i, nm in enumerate(chain):
    x = M + (bwidth + gapx) * i
    hot = i >= 3
    sp = rect(s, x, y, bwidth, Inches(0.46),
              fill=(BLUE_BG if i == 3 else (GREEN_BG if i == 4 else BG_SOFT)),
              line_color=(BLUE if i == 3 else (GREEN if i == 4 else LINE)))
    tf = sp.text_frame
    write(tf, [(nm, dict(size=10.5, bold=hot,
                         color=(BLUE if i == 3 else (GREEN if i == 4 else MUTED))))],
          first=True, space_after=0, align=PP_ALIGN.CENTER)

yy = y + Inches(0.66)
pw = Inches(4.75)
mid_w = CW - pw * 2
sp = rect(s, M, yy, pw, Inches(3.35), fill=BLUE_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(3.35), BLUE)
tf = sp.text_frame
write(tf, [("控制面 · WHC(平台)", dict(size=10.5, bold=True, color=BLUE, font=FONT_EN))],
      first=True, space_after=5)
write(tf, [("定规则、出建议", dict(size=15, bold=True, color=INK))], space_after=7)
for t in ["持有并版本化下发分区分配策略",
          "执行算法 步骤 1–4(候选过滤 / 预分区 / 大单判定 / 集中度优化)",
          "输出:子单 + 每行的区优先级序列",
          "只读一份分区库存快照,用于边界裁量",
          "不预占、不记账、不参与对账",
          "跨仓统一:一套规则覆盖 10 仓,灰度与实验在此完成"]:
    write(tf, [("· ", dict(size=11, bold=True, color=BLUE)), (t, dict(size=10.5, color=INK2))],
          space_after=4, line=1.18)

sp = rect(s, M + pw + mid_w, yy, pw, Inches(3.35), fill=GREEN_BG, line_color=None)
bar(s, M + pw + mid_w, yy, Pt(3.2), Inches(3.35), GREEN)
tf = sp.text_frame
write(tf, [("数据面 · WMS(3PL 本地)", dict(size=10.5, bold=True, color=GREEN, font=FONT_EN))],
      first=True, space_after=5)
write(tf, [("终裁、绑定、纠偏", dict(size=15, bold=True, color=INK))], space_after=7)
for t in ["执行算法 步骤 5–6(库存校验终裁 / 波次与库位绑定)",
          "唯一权威库存账本,精确到库位",
          "顺位改派:首选不中则取序列下一位,WMS 内闭环",
          "保留接单不预占与波次晚绑定的批量优化",
          "执行补货任务与分区盘点",
          "回传分配结果,供平台侧可视与 KPI"]:
    write(tf, [("· ", dict(size=11, bold=True, color=GREEN)), (t, dict(size=10.5, color=INK2))],
          space_after=4, line=1.18)

flows = [("规则版本化下发", "→", BLUE), ("子单 + 优先级序列", "→", BLUE),
         ("分区库存快照(只读)", "←", GREEN), ("分配结果回传", "←", GREEN)]
fy = yy + Inches(0.42)
for txt, arrow, col in flows:
    sp = rect(s, M + pw + Inches(0.06), fy, mid_w - Inches(0.12), Inches(0.62),
              fill=WHITE, line_color=LINE)
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.04)
    write(tf, [(arrow, dict(size=13, bold=True, color=col, font=FONT_EN))],
          first=True, space_after=1, align=PP_ALIGN.CENTER)
    write(tf, [(txt, dict(size=8.8, color=INK2))], space_after=0, align=PP_ALIGN.CENTER, line=1.05)
    fy += Inches(0.72)

# ---- 优先级序列
s, y = page("关键设计:下发「优先级序列」而非锁死单区", "KEY DESIGN",
            "这是让 WHC 可以「不那么准」、而系统整体依然正确的机制")
cw2 = (CW - Inches(0.3)) / 2
sp = rect(s, M, y, cw2, Inches(2.28), fill=SLATE_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(2.28), SLATE)
tf = sp.text_frame
write(tf, [("如果下发单一区(不推荐)", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
for t in ["WHC 下发「必须去 AGV 区」",
          "WMS 发现 AGV 区不足 → 无可用指令",
          "只能回调 WHC 重新计算 → WHC→WMS→WHC 跨系统长回路",
          "高峰期该回路的时延与故障率被同时放大"]:
    write(tf, [("· ", dict(size=11, bold=True, color=SLATE)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

sp = rect(s, M + cw2 + Inches(0.3), y, cw2, Inches(2.28), fill=GREEN_BG, line_color=None)
bar(s, M + cw2 + Inches(0.3), y, Pt(3.2), Inches(2.28), GREEN)
tf = sp.text_frame
write(tf, [("下发优先级序列(推荐)", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("zonePrioritySeq = [ AGV区, 人工区-食品, … ]",
            dict(size=11, bold=True, color=GREEN, font=FONT_EN))], space_after=6)
for t in ["WMS 按序列自上而下尝试,首选不中即取下一位",
          "改派完全在 WMS 内闭环,不跨系统、不回 WHC",
          "时序最短、故障面最小、无分布式事务"]:
    write(tf, [("· ", dict(size=11, bold=True, color=GREEN)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)

yy = y + Inches(2.48)
sp = rect(s, M, yy, CW, Inches(1.72), fill=PURPLE_BG, line_color=None)
bar(s, M, yy, Pt(3.2), Inches(1.72), PURPLE)
tf = sp.text_frame
write(tf, [("由此得到本方案最重要的一条性质", dict(size=13, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("WHC 的决策允许「不准」,系统的正确性不依赖快照的实时性。",
            dict(size=14, bold=True, color=PURPLE))], space_after=6)
write(tf, [("快照过期只会降低「首选区命中率」,不会导致错误结果 —— 因为 WMS 持有权威账本并负责纠偏。这条性质直接解除了「WHC 不记账就没法决策」的顾虑,也正是路径 3 能够成立的根本原因。相应地,",
            dict(size=11, color=INK2)),
           ("首选区命中率", dict(size=11, bold=True, color=INK)),
           (" 成为衡量快照新鲜度是否足够的核心指标,而不需要追求强一致。", dict(size=11, color=INK2))],
      space_after=0, line=1.2)

# ---- 账本原则 + 接口
s, y = page("库存账本原则与关键接口", "DATA & INTERFACE",
            "唯一权威账本留在 WMS;平台侧只读、不加减、不参与对账")
cw2 = (CW - Inches(0.3)) / 2
sp = rect(s, M, y, cw2, Inches(2.25), fill=RED_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(2.25), RED)
tf = sp.text_frame
write(tf, [("必须绕开的陷阱", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("若 WHC 维护第二本分区库存账并随订单/拣货/补货/盘点实时加减:",
            dict(size=11, color=INK2))], space_after=5, line=1.2)
for t in ["两本账必然漂移 → 无止境对账",
          "对账口径还要新增「分区」维度,中台现有对账无法复用",
          "任何一侧故障都会造成账实双向不一致,恢复成本极高"]:
    write(tf, [("✕ ", dict(size=11, bold=True, color=RED)), (t, dict(size=11, color=INK2))],
          space_after=4, line=1.2)
write(tf, [("增加的应是决策流复杂度(可控),而不是账本复杂度(不可控)。",
            dict(size=11, bold=True, color=RED))], space_after=0, line=1.2)

card(s, M + cw2 + Inches(0.3), y, cw2, Inches(2.25), "账本归属", [
    ("WMS", dict(size=11.5, bold=True, color=GREEN)),
    ("唯一权威账本,库位级。所有加减仅发生于此。", dict(size=11, color=INK2)),
    ("WHC", dict(size=11.5, bold=True, color=BLUE)),
    ("只读快照,仅用于优先级排序时的边界裁量,不做加减。", dict(size=11, color=INK2)),
    ("中台", dict(size=11.5, bold=True, color=SLATE)),
    ("仍按 SKU 总量与 WMS 对账,分区对其完全透明 —— 对账链路零改动。", dict(size=11, color=INK2)),
], accent=GREEN, bg=GREEN_BG)

yy = y + Inches(2.42)
headers = ["接口", "方向", "频次", "关键内容"]
rows = [
    ["规则下发 RuleSetPublish", "WHC → WMS", "低频 / 版本化",
     "ruleSetVersion、生效时间、适用仓、区偏好规则、大单阈值与口径、是否允许跨区拆行、比例目标、缺货降级策略"],
    ["分配建议 AllocationSuggestion", "WHC → WMS", "随单",
     "子单结构、每行 zonePrioritySeq、命中的规则版本号"],
    ["结果回传 AllocationResult", "WMS → WHC", "随单",
     "最终落区、是否发生改派、包裹构成、缺量与处置动作、规则版本号"],
    ["分区快照 ZoneStockSnapshot", "WMS → WHC", "分钟级 + 低水位事件",
     "SKU × 区 可用量。仅供排序裁量,非权威账,严禁据此记账"],
]
kv_table(s, M, yy, CW, headers, rows, [2.5, 1.5, 1.8, 6.6],
         row_h=Inches(0.56), head_h=Inches(0.40), font_size=10)

# ============================================================ PART 5
IDX[0] += 1
section_divider(prs, IDX[0], 5, "落地与治理", "分期、指标、风险、以及需要拍板的事项",
                ["补货体系设计", "指标体系与基线", "分期路线图", "风险清单与决策事项"])

# ---- 补货体系
s, y = page("补货体系:把「应急搬运」降为「计划作业」", "REPLENISHMENT",
            "诚实的目标不是消灭互补货,而是降低频次并让它可排期")
cw3 = (CW - Inches(0.44)) / 3
for i, (ttl, lines, ac, bg, tag) in enumerate([
    ("入库直上架分流", ["收货上架时即按各区目标水位分流", "不产生任何区间搬运,成本最低",
                  "对新品与高频补货 SKU 尤其有效"], GREEN, GREEN_BG, "优先级 1"),
    ("储备区 → 拣选区", ["由水位(min/max)驱动的常规前置区补货", "叠加波次预补:按已释放波次的需求前瞻补货",
                   "可排期到低峰时段执行"], BLUE, BLUE_BG, "优先级 2"),
    ("区间互补(兜底)", ["仅当某区见底且其他补货源来不及时启用", "属于异常处置,应被监控与复盘",
                   "其频次是衡量比例是否设准的直接信号"], AMBER, AMBER_BG, "优先级 3"),
]):
    x = M + (cw3 + Inches(0.22)) * i
    card(s, x, y, cw3, Inches(2.15), ttl, lines, accent=ac, bg=bg, tag=tag, body_size=10.5)

yy = y + Inches(2.35)
sp = rect(s, M, yy, CW, Inches(1.85), fill=WHITE, line_color=LINE)
tf = sp.text_frame
write(tf, [("与现状的真实差异", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("现状(一品一区):", dict(size=11, bold=True, color=SLATE)),
           ("大单到达 → 触发一次 AGV→人工 的按单急搬。搬运由订单驱动,不可预测、不可排期、且发生在高峰。",
            dict(size=11, color=INK2))], space_after=5, line=1.2)
write(tf, [("目标(一品多区):", dict(size=11, bold=True, color=GREEN)),
           ("大单所需库存已常备于人工区 → 消除按单触发的急搬。补货改由水位驱动,可预测、可排期、可错峰。",
            dict(size=11, color=INK2))], space_after=5, line=1.2)
write(tf, [("需要说清楚的是:", dict(size=11, bold=True, color=AMBER)),
           ("互补货不会归零。当比例与真实需求结构偏离时它仍会出现——因此「区间互补货频次」既是结果指标,也是比例是否设准的诊断信号。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 风险
s, y = page("最主要的新增风险:分区库存准确率", "RISK",
            "它是运营风险,不是架构风险 —— 也正因如此最容易被漏掉")
sp = rect(s, M, y, CW, Inches(1.60), fill=RED_BG, line_color=None)
bar(s, M, y, Pt(3.2), Inches(1.60), RED)
tf = sp.text_frame
write(tf, [("为什么中台对账发现不了", dict(size=13, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("一品一区时,一个 SKU 只在一处,总量准 ≡ 分区准。一品多区后,假设 AGV 区账面 100 实物 80,而差额 20 恰在人工区——",
            dict(size=11, color=INK2)),
           ("SKU 总量完全对得平,中台对账全绿。", dict(size=11, bold=True, color=RED))],
      space_after=5, line=1.2)
write(tf, [("但生产上会立刻表现为:首选区反复拣不到 → 改派激增 → 波次重排 → 出库时效恶化。这是一个「对账正常、生产恶化」的隐蔽失效模式。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

yy = y + Inches(1.80)
headers = ["风险", "影响", "应对", "责任方"]
rows = [
    ["分区级账实不符", "首选命中率下降、改派激增、时效恶化", "新增分区级循环盘点(高频 SKU 高频盘);监控首选区命中率作为早期信号", "运营 + IT"],
    ["比例与需求结构偏离", "区间互补货不降反升,收益归零", "一期人工配置 + 偏离度校验;二期上 Slotting 自动测算与周期重算", "业务 + 算法"],
    ["大单阈值口径不清", "判定结果相反,大单误入 AGV", "上线前锁定计数口径(件/行/箱),并写入规则版本", "业务"],
    ["3PL WMS 改造受限", "路径 3 无法落地", "启用兜底方案(见下页),定位为过渡,目标仍是迁回路径 3", "IT + 3PL"],
    ["改派带来额外包裹", "单均包裹数与运费上升", "监控单均包裹数并设阈值告警;必要时在规则中加大集中度权重", "运营"],
]
kv_table(s, M, yy, CW, headers, rows, [2.2, 3.0, 5.4, 1.5],
         row_h=Inches(0.56), head_h=Inches(0.40), font_size=10)

# ---- 指标
s, y = page("指标体系与基线", "METRICS",
            "上线前必须完成基线采集,否则收益无法证明、比例无法迭代")
cw2 = (CW - Inches(0.3)) / 2
card(s, M, y, cw2, Inches(2.25), "效率类 —— 验证第一收益", [
    "AGV 区 件/小时、人工区 件/小时",
    "AGV 区工作站占用时长分布(大单被挡出后应显著收敛)",
    "单均拣货时长、订单准时出库率",
], accent=GREEN, bg=GREEN_BG, tag="RESULT")
card(s, M + cw2 + Inches(0.3), y, cw2, Inches(2.25), "成本类 —— 验证洞察一", [
    "单均包裹数、订单平均跨区数",
    "单均运费",
    "补货工时 与 区间互补货频次",
], accent=BLUE, bg=BLUE_BG, tag="RESULT")

yy = y + Inches(2.45)
card(s, M, yy, cw2, Inches(2.25), "健康度类 —— 系统自诊断", [
    "首选区命中率(核心:反映快照新鲜度与分区账实是否健康)",
    "改派率、改派后包裹增量",
    "分区库存准确率、各区水位达标率、比例偏离度",
], accent=AMBER, bg=AMBER_BG, tag="LEADING")
card(s, M + cw2 + Inches(0.3), yy, cw2, Inches(2.25), "选型验证 —— 决定架构是否成立", [
    "属性可判定率:仅凭主数据与订单属性即可确定唯一目标区的行数占比",
    "该值高 ⇒ 路径 3 明确成立;显著偏低则需重新评估架构",
    "建议在方案立项阶段,先用历史订单离线回放测出此值",
], accent=PURPLE, bg=PURPLE_BG, tag="DECISION")

# ---- 分期
s, y = page("分期落地路线", "ROADMAP", "一期以最小风险验证核心收益,收益成立后再扩展能力边界")
phases = [
    ("一期 · MVP", "验证核心收益", GREEN, GREEN_BG, [
        "方案 B:整行落单区,不做跨区拆行",
        "WHC 下发规则 + 出区优先级序列",
        "WMS 终裁绑定 + 顺位改派闭环",
        "比例人工配置,系统做偏离度校验",
        "上线分区级盘点与命中率监控",
        "缺货按既定降级流处置",
    ], "关口:首选区命中率 > 90%,AGV 吞吐提升可量化,单均包裹数不劣化"),
    ("二期 · 自动化", "让规则自己变好", BLUE, BLUE_BG, [
        "Slotting 引擎自动测算各 SKU 比例",
        "补货引擎自动化(水位 + 波次预补)",
        "集中度优化权重可按品类调参",
        "KPI 看板与规则灰度实验能力",
        "大促场景的比例预案与切换",
    ], "关口:区间互补货频次下降,比例偏离度收敛"),
    ("三期 · 扩展", "打开能力边界", PURPLE, PURPLE_BG, [
        "方案 A:允许跨区拆行(需成本门槛约束)",
        "按实时设备负载动态调整区偏好",
        "与跨仓寻源策略联动(需先澄清外仓定位)",
    ], "前置:方案 A 对分区实时性要求上升,仍由 WMS 持账"),
]
cw3 = (CW - Inches(0.44)) / 3
for i, (ttl, sub, ac, bg, items, gate) in enumerate(phases):
    x = M + (cw3 + Inches(0.22)) * i
    sp = rect(s, x, y, cw3, Inches(3.35), fill=bg, line_color=None)
    bar(s, x, y, Pt(3.2), Inches(3.35), ac)
    tf = sp.text_frame
    write(tf, [(ttl, dict(size=14, bold=True, color=INK))], first=True, space_after=2)
    write(tf, [(sub, dict(size=10.5, color=ac, bold=True))], space_after=7)
    for it in items:
        write(tf, [("· ", dict(size=10.5, bold=True, color=ac)), (it, dict(size=10.5, color=INK2))],
              space_after=4, line=1.18)
    sp2 = rect(s, x + Inches(0.12), y + Inches(3.5), cw3 - Inches(0.24), Inches(0.82),
               fill=WHITE, line_color=LINE)
    tf2 = sp2.text_frame
    tf2.margin_top = tf2.margin_bottom = Inches(0.06)
    write(tf2, [(gate, dict(size=9.5, color=INK2))], first=True, space_after=0, line=1.15)

# ---- 兜底
s, y = page("兜底方案:若 3PL WMS 改造受限", "FALLBACK",
            "退化到路径 1,但必须加上四条约束,把锁竞争压在可控范围")
cw2 = (CW - Inches(0.3)) / 2
card(s, M, y, cw2, Inches(2.6), "四条必须同时成立的约束", [
    "只对稀缺区预占 —— 临近低水位的区才锁,充裕的 AGV 区仍走 WMS 晚绑定不锁",
    "按「区」聚合预占,不锁到库位 —— 大幅减少锁行数",
    "乐观并发 + 短 TTL + 超时自动释放与补偿",
    "仅当区跨越低水位线时启用;常态下纯属性路由,不预占",
], accent=AMBER, bg=AMBER_BG)
card(s, M + cw2 + Inches(0.3), y, cw2, Inches(2.6), "定位与退出条件", [
    "定位为过渡方案,不作为目标态",
    "必须同步埋点:锁等待时长、锁冲突率、预占超时释放率",
    "一旦 3PL WMS 具备执行平台规则的能力,即迁回路径 3",
    ("注意:该方案仍牺牲了波次批量优化,收益上限低于路径 3。",
     dict(size=11, bold=True, color=RED)),
], accent=SLATE, bg=SLATE_BG)

yy = y + Inches(2.8)
sp = rect(s, M, yy, CW, Inches(1.4), fill=BG_SOFT, line_color=LINE)
tf = sp.text_frame
write(tf, [("关于跨仓与仓内的层级澄清", dict(size=12.5, bold=True, color=INK))], first=True, space_after=6)
write(tf, [("跨仓 = 寻源:", dict(size=11, bold=True, color=BLUE)),
           ("由 OMS / 中台基于各仓 SKU 总量可用性决策。   ", dict(size=11, color=INK2)),
           ("仓内跨区 = 分配:", dict(size=11, bold=True, color=GREEN)),
           ("由 WMS 基于分区库存与订单画像决策。", dict(size=11, color=INK2))], space_after=5, line=1.2)
write(tf, [("二者规则形态相似,但数据与决策点不同,不能混为一层。因此「外仓能否当作一个区」取决于它的定位:若为独立仓则走寻源,若为本仓溢出储区才可走分区。这一点需业务先行澄清。",
            dict(size=11, color=INK2))], space_after=0, line=1.2)

# ---- 决策事项
s, y = page("需要拍板的事项", "DECISIONS", "以下事项不决,方案无法进入详细设计")
items = [
    ("01", "大单阈值的计数口径", "「同分区 30 件」中的「件」= 商品件数 / 拣选行数 / 原箱按箱?口径不同会导致同一订单判定结果相反。", RED),
    ("02", "外仓的层级定位", "独立仓(走跨仓寻源,归 OMS/中台)还是本仓溢出储区(走仓内分区,归 WMS)?决定它接在哪一层。", RED),
    ("03", "一期是否接受不做跨区拆行", "建议一期锁定方案 B。跨区拆行会显著提高对分区实时性的要求,不宜与首期同时上。", AMBER),
    ("04", "3PL WMS 的改造范围与商务边界", "路径 3 要求 WMS 能执行平台下发的规则并做顺位改派。需确认各仓 3PL 的改造意愿、周期与成本。", AMBER),
    ("05", "指标基线采集的时间窗", "效率、成本、健康度三类基线需在改造上线前采集完成,否则收益无法证明。请确定采集起止时间。", BLUE),
]
yy, rh = y + Inches(0.06), Inches(0.88)
for num, ttl, desc, ac in items:
    bgc = {RED: RED_BG, AMBER: AMBER_BG, BLUE: BLUE_BG}[ac]
    sp = rect(s, M, yy, CW, rh, fill=bgc, line_color=None)
    bar(s, M, yy, Pt(3.2), rh, ac)
    _, ntf = textbox(s, M + Inches(0.20), yy + Inches(0.18), Inches(0.55), Inches(0.5))
    write(ntf, [(num, dict(size=19, bold=True, color=ac, font=FONT_EN))], first=True, space_after=0)
    _, ttf = textbox(s, M + Inches(0.84), yy + Inches(0.13), CW - Inches(1.1), Inches(0.7))
    write(ttf, [(ttl, dict(size=13, bold=True, color=INK))], first=True, space_after=3)
    write(ttf, [(desc, dict(size=10.5, color=INK2))], space_after=0, line=1.2)
    yy += rh + Inches(0.10)

# ---- 收口
s = blank(prs)
IDX[0] += 1
bar(s, Emu(0), Emu(0), SW, SH, INK)
bar(s, Emu(0), Emu(0), Inches(0.11), SH, BLUE)
_, tf = textbox(s, Inches(1.15), Inches(1.35), Inches(11.0), Inches(0.4))
write(tf, [("一句话收口", dict(size=12, bold=True, color=RGBColor(0x7E, 0xA6, 0xF5), font=FONT_EN))],
      first=True, space_after=0)
_, tf = textbox(s, Inches(1.15), Inches(1.95), Inches(11.0), Inches(1.6))
write(tf, [("业务上,", dict(size=19, bold=True, color=RGBColor(0x7E, 0xA6, 0xF5))),
           ("交付的不是「80/20」这个数字,而是一套可计算的规则:比例由需求结构反算,选区由订单属性驱动,分区只影响效率、绝不影响可履约性。",
            dict(size=19, color=WHITE))], first=True, space_after=14, line=1.32)
_, tf = textbox(s, Inches(1.15), Inches(3.55), Inches(11.0), Inches(1.6))
write(tf, [("系统上,", dict(size=19, bold=True, color=RGBColor(0x8E, 0xDC, 0xBE))),
           ("顺着算法的天然分界线切:WHC 定规则、出优先级序列、只读不记账;WMS 保留唯一权威账本、晚绑定终裁、内部闭环改派。",
            dict(size=19, color=WHITE))], first=True, space_after=0, line=1.32)
bar(s, Inches(1.15), Inches(5.35), Inches(1.1), Pt(3), BLUE)
_, tf = textbox(s, Inches(1.15), Inches(5.68), Inches(11.0), Inches(0.9))
write(tf, [("如此,既拿到「核心能力上移平台、10 仓统一、弱化 3PL 绑定」的战略收益,又避开双账本复杂度与高频锁竞争。剩下的关键前置动作只有两个:锁定大单口径,采集指标基线。",
            dict(size=13, color=RGBColor(0xA8, 0xB6, 0xC8)))], first=True, space_after=0, line=1.3)

out = "/home/user/jiangzw/docs/一品多区备货-业务与系统方案.pptx"
os.makedirs(os.path.dirname(out), exist_ok=True)
prs.save(out)
print("saved:", out)
print("slides:", len(prs.slides.__iter__.__self__._sldIdLst))
