---
theme: default
title: 仓储平台化方案 业务评审
info: |
  受众：运营总监、财务经理、CEO
  目的：取得方案 v1.0 评审通过，启动 PRD 阶段
class: text-center
highlighter: shiki
transition: slide-left
mdc: true
---

# 仓储平台化方案 业务评审

零售供应链 · wms-platform · v1.0

汇报人：江某某 ｜ 2026-05-30

<!--
本份用 Slidev 编写。本地预览：slidev wms-platform-report-20260530-biz-review.md
导出 PPTX：slidev export --format pptx
-->

---

## 议程（10 分钟讲完）

1. **结论**（30 秒）
2. **痛点**（2 分钟）
3. **方案**（3 分钟）
4. **收益**（2 分钟）
5. **风险与下一步**（2 分钟）
6. **请决策事项**（30 秒）

---
layout: section
---

# 1. 结论

---

## 一句话结论

> **把 3 套独立仓储系统统一为一套平台 + 智能调度，**  
> **拣选人效 80 → 100 单/h，年化节省 480 万，9.5 个月回本。**

<div class="grid grid-cols-3 gap-4 mt-12">
<div class="text-center p-4 bg-green-50 rounded">
<div class="text-4xl font-bold text-green-600">+25%</div>
<div class="text-sm mt-2">人效提升</div>
</div>
<div class="text-center p-4 bg-blue-50 rounded">
<div class="text-4xl font-bold text-blue-600">¥480万</div>
<div class="text-sm mt-2">年化收益</div>
</div>
<div class="text-center p-4 bg-orange-50 rounded">
<div class="text-4xl font-bold text-orange-600">9.5个月</div>
<div class="text-sm mt-2">回本周期</div>
</div>
</div>

---
layout: section
---

# 2. 痛点：成本红线被突破

---

## 仓储成本占比已超红线

| 指标 | 2024 | 2025 | 2026 Q1 | 老板红线 |
|---|---|---|---|---|
| 仓储成本/GMV | 4.2% | 4.8% | **5.3%** | 4.5% |
| 拣选人效（单/h） | 95 | 85 | **80** | — |
| 缺货率 | 2.1% | 2.8% | **3.2%** | 1.5% |

<div class="mt-8 text-red-600 font-bold">
不改变现状，2026 全年仓储成本将多支出约 600 万元。
</div>

---

## 4 大痛点（按损失排序）

| # | 痛点 | 年损失 |
|---|---|---|
| 1 | 拣选人效持续下滑 | 600 万 |
| 2 | 跨业务线无法削峰，旺季加班暴增 | 200 万 |
| 3 | 班长经验排单，员工抱怨流失 | 80 万（招聘成本） |
| 4 | 三方仓对账靠人工，错账率 2% | 18 万 + 月底返工 3 人月/季 |

---
layout: section
---

# 3. 方案：1 套平台 + 智能调度

---

## 一图看懂

```mermaid {scale: 0.65}
flowchart TB
    subgraph 业务方
        BA[A 线主营]
        BB[B 线 KA]
        BC[C 线跨境]
    end
    subgraph 平台[仓储平台 ← 关键改造]
        OPS[作业中心<br/>入库·拣选·复核]
        INV[库存中心<br/>多仓·多业务统一]
        ALG[智能调度<br/>波次合并·路径优化]
        SETTLE[结算中心<br/>多租户分摊]
    end
    BA --> ALG
    BB --> ALG
    BC --> ALG
    ALG --> OPS
    OPS --> INV
    OPS --> SETTLE
    style 平台 fill:#E6F3FF,stroke:#4682B4
```

**白话**：把"3 套系统 + 班长经验"换成"1 套平台 + 系统智能合单"。

---

## 关键改造点

| 模块 | 现状 | 改造后 |
|---|---|---|
| 作业 | A/B/C 三套独立 | 一套平台，差异点配置化 |
| 库存 | 各业务线独立池 | 统一池化，可跨业务调拨 |
| 排单 | 班长 Excel 拍脑袋 | 系统按规则自动合并 |
| 结算 | 月底人工拆账 | 自动按租户分摊 |

---
layout: section
---

# 4. 收益：480 万 / 年

---

## 收益拆解（年化）

| 收益项 | 金额 | 测算口径 |
|---|---|---|
| 人力节省 | 115 万 | 节省 12 人 |
| 库存周转改善 | 80 万 | 释放占用资金 2000 万 |
| 缺货损失减少 | 45 万 | GMV × 缺货率改善 × 毛利 |
| 旺季加班减少 | 100 万 | 跨业务削峰 |
| 三方仓对账自动化 | 18 万 | 节省 12 财务人月 |
| 人员流失降低 | 50 万 | 流失率 18% → 10% |
| IT 运维节省 | 72 万 | 3 套系统并 1 套 |
| **合计** | **480 万** | |

<div class="mt-4 text-sm text-gray-600">
投入 380 万 → 年化 480 万 → 回本 9.5 个月
</div>

---

## 同时改善 4 项业务 KPI

<div class="grid grid-cols-2 gap-4 mt-8">

<div class="p-4 border rounded">
<div class="text-sm text-gray-600">仓储成本/GMV</div>
<div class="text-3xl font-bold">5.3% <span class="text-green-600">→ 4.5%</span></div>
<div class="text-xs text-gray-500">回到老板红线内</div>
</div>

<div class="p-4 border rounded">
<div class="text-sm text-gray-600">拣选人效</div>
<div class="text-3xl font-bold">80 <span class="text-green-600">→ 100</span> 单/h</div>
<div class="text-xs text-gray-500">+25%</div>
</div>

<div class="p-4 border rounded">
<div class="text-sm text-gray-600">缺货率</div>
<div class="text-3xl font-bold">3.2% <span class="text-green-600">→ 1.5%</span></div>
<div class="text-xs text-gray-500">客户体验改善</div>
</div>

<div class="p-4 border rounded">
<div class="text-sm text-gray-600">订单履约时效</div>
<div class="text-3xl font-bold">28h <span class="text-green-600">→ 18h</span></div>
<div class="text-xs text-gray-500">B2C 转化预估 +1.5%</div>
</div>

</div>

---
layout: section
---

# 5. 风险与下一步

---

## 主要风险（已有应对）

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 🔴 ERP 主数据治理项目延期 | 中 | 高 | 优先治理商品/库位，其他可解耦 |
| 🟡 三方仓接入标准不统一 | 高 | 中 | 6 月起运营总监牵头 SOP v1.0 |
| 🟡 旺季峰值未压测 | 中 | 高 | 8 月专项压测，按 1.5 倍预备 |

---

## 下一步（30 天）

- ✅ 6/10：本方案评审通过
- ✅ 6/15：启动 PRD-01 智能波次合并
- ✅ 6/20：三方仓 SOP v1.0
- ✅ 6/30：PRD-01 评审通过

---
layout: section
---

# 6. 请评审决策

---

## 请今天确认 3 件事

1. **方案 v1.0 是否通过？** → 是否继续 PRD 阶段
2. **资源是否到位？** → 380 万预算 + 业务方 80 人天投入
3. **试点仓选择？** → 建议华东 1 仓（数据基础最好）

<div class="mt-12 text-sm text-gray-500">
方案详情：jiangzw/projects/wms-platform/01-solution/wms-platform-solution-v1.0.md
</div>

---
layout: end
---

# 谢谢
