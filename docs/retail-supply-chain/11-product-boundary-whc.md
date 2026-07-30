# 11 · 产品边界与系统交互：PFC / WHC / WMS / OIC

> 本文档对齐实际系统命名，是 [01 领域边界](01-domain-boundaries.md) 的落地版本。
> 解决的核心问题：**DC → 门店调拨场景下，出库单与入库单的多对多。**

## 0. 术语对齐

| 实际系统 | 本套文档中的对应物 | 定位 |
| --- | --- | --- |
| **PFC** | ERP + OMS 的单据部分 | 单据主控 + 逻辑库存调度 |
| **OIC** | 库存中心 | 全渠道库存视图，消费 WMS 实物流水 |
| **WHC** | （原文档未独立建模） | **仓配物流协同层 —— 需新建的那一层** |
| **WMS** | WMS（发货 WMS / 收货 WMS，各仓独立） | 仓内执行 |
| **发运凭证** | `shipment` | 一批出库单的发货流水凭证 |

---

## 1. 产品边界

### 1.1 五个系统的职责

| 系统 | 拥有的事实（SOR） | 明确不拥有 |
| --- | --- | --- |
| **PFC** | 调拨主单、出入库单据（**只有商品+数量，无批次**）、货权、逻辑库存调度、**在途库存** | 批次、货位、容器、车 |
| **OIC** | 全渠道库存视图（消费 WMS 流水）、可售库存 | 单据、作业 |
| **WHC** | **跨仓作业编排、装车集单、容器标签与 pegging、发运凭证、承运协调** | 仓内作业、库存过账 |
| **WMS** | 物理库存、**批次（由 WMS 产生）**、仓内作业、货位 | 单据主控、跨仓协同、车 |
| **TMS / DMS** | 车、线路、运单、POD | 库存、单据 |

### 1.2 已确定的五条边界

1. **批次归 WMS**：PFC 下发单据不带批次，WMS 收发货产生批次，可回传但 **PFC 不用批次调度库存**
2. **实物库存流水归 OIC**：WMS → OIC 是**流水**，不是快照
3. **发货 WMS 按出库单维度回传发货明细**
4. **发货 WMS 与收货 WMS 相互独立，不感知彼此差异**
   → **推论：差异比对只能在 PFC 层做，不能在 WMS 之间做**
5. **容器与单据解耦** —— 见 §1.3 的精确化

### 1.3 「容器与单据解耦」必须精确化

否则会被实现成灾难 —— XDK「一单到底」将无法实现。

| | 内容 | 判断 |
| --- | --- | --- |
| ✅ **要解耦的** | 容器与**出库单的强绑定**：一个容器可装多张出库单的货，容器不再「属于」某张单 | 正确，这是集单与拼车的效率来源 |
| ❌ **不能解耦的** | 容器**内容的单据溯源**：`container_content` **行级**必须能追到来源单据行 | 这个不能丢 |

由此得出 WHC 最重要的一条职责定义：

> **容器标签是跨节点 pegging 的物理载体。WHC 拥有容器标签，因此 WHC 是跨仓单据关联的 SOR。**

这一条把「缺失协同层」与「XDK 回传方式无共识」两个问题连起来了 ——
**后者之所以没有共识，是因为前者那一层还不存在，pegging 没有归属方。**

### 1.4 系统交互全景

```mermaid
flowchart TB
  PFC["PFC 单据主控<br/>调拨主单·出入库单(商品+数量)<br/>货权·在途库存"]
  WHC["WHC 仓配物流协同层<br/>跨仓编排·装车集单<br/>容器标签+pegging·发运凭证"]
  WMSA["发货 WMS (DC)<br/>批次·货位·作业"]
  WMSB["收货 WMS (门店/RDC)"]
  TMS["TMS/DMS<br/>车·线路·POD"]
  OIC["OIC 库存中心"]

  PFC -->|①出库单 商品+数量| WMSA
  PFC -->|①'越库 ASN 预分配| WMSA
  WHC -->|②集单方案+容器标签| WMSA
  WMSA -->|③实装容器扫码事实| WHC
  WMSA -->|④发货明细 按出库单维度<br/>商品+批次| PFC
  WHC -->|⑤发运凭证 按车×门店| PFC
  WHC <-->|配载·派车| TMS
  PFC -->|⑥门店入库单 1:1 对发运凭证| WMSB
  WMSB -->|⑦收货回传 商品+批次<br/>XDK行带入库单行ID| PFC
  WMSA --> OIC
  WMSB --> OIC
```

---

## 2. 核心方案：用发运凭证打断出入库单的 M:N

### 2.1 现状诊断

```
PFC → 多张 out 单 → DC WMS
DC WMS 拼车 → 一车多出库单 → 回传 PFC
PFC 按【车】维度发货明细流水 → 一张入库单 → 门店
PFC 用「出库单 ↔ 入库单」配对调拨库存
```

| # | 问题 | 后果 |
| --- | --- | --- |
| 1 | **粒度错了**：按「车」生成入库单 | 一车拉 10 个门店只出一张入库单，门店无法收货 |
| 2 | **配对关系断了**：N 张出库单 → 1 张入库单 | PFC 调拨逻辑假设 1:1，N:1 时在途库存算不清 |
| 3 | **SSTK / XDK 混发** | 门店入库单有些行**根本没有对应出库单**（货来自供应商 ASN 越库）→ M:N 且部分行无对应 |

### 2.2 解法：两个 1:N 替代一个 M:N

```
出库单(N) ──合并──┐
                  ├──> 发运凭证 shipment(1) ──1:1──> 门店入库单(1)
XDK/ASN行(N) ─────┘
```

**粒度定义（整个方案的地基）：**

> **一张发运凭证 = 一次发车(load) × 一个收货节点(门店) × 一个货权(owner)**

| 关系 | 基数 | 说明 |
| --- | --- | --- |
| 出库单 : 发运凭证 | N : 1 | 多张调拨出库单合并到一票 |
| ASN 行(XDK) : 发运凭证 | N : 1 | 越库行也挂进来 |
| **发运凭证 : 门店入库单** | **1 : 1** | **PFC 用这个做调拨配对** |
| 出库单 : 门店入库单 | N : 1 | 间接，通过发运凭证传递，**不再直接配对** |

### 2.3 最关键的一处改动

> **PFC 的在途库存键，从 `出库单号` 改为 `发运凭证号`。**

```
DC 库存 ──发车──> 在途 (键 = shipment_no) ──门店收货──> 门店库存
```

出库单只负责**核销 DC 侧的库存扣减**，不再承担「配对入库单」的职责。
这两件事本来就不该由一个对象承担 —— 一个是仓储域的作业完结，一个是货权域的位移配对。

### 2.4 发运凭证由 WHC 生成，PFC 消费

发运凭证的切分依赖「车 × 门店」，这是 WHC 独有的信息（拼车结果），PFC 不知道。

PFC 拿到后做三件事：① 在途过账 ② 1:1 生成门店入库单 ③ 下发收货 WMS。

### 2.5 两条回传并存，但同源

「按出库单维度回传发货明细」与「按车×门店的发运凭证」是**同一批实物事实的两个视角**：

```mermaid
flowchart LR
  C["实装容器<br/>container + container_content<br/>（唯一事实源）"]
  C -->|按 出库单 聚合| A["④发货明细回传<br/>发货WMS → PFC<br/>用途: 核销出库单、扣DC库存"]
  C -->|按 车×门店 聚合| B["⑤发运凭证<br/>WHC → PFC<br/>用途: 建在途、生成门店入库单"]
```

> **两条回传都由实装容器反算，所以必然对得上。**
> 这是一致性的**结构性保证**，不靠对账补救。

---

## 3. SSTK / XDK 混发：行级 pegging

### 3.1 分歧的根因

「收货 WMS 到底按不按入库单行 ID 回传」——
这个问法把 pegging 当成了**整单级的二元选择**。它实际上是**行级的、按模式条件必填**。

### 3.2 统一报文结构，语义按模式分支

| 字段 | SSTK 行 | XDK 行 |
| --- | --- | --- |
| `sku_id` | 必填 | 必填 |
| `batch_no` | 必填（WMS 产生） | 必填（沿用供应商批次） |
| `qty` | 必填 | 必填 |
| `source_mode` | `SSTK` | `XDK` |
| `pegging_type` | `NONE` | `INBOUND_LINE` |
| `pegging_ref` | **空** | **必填**：门店入库单行 ID |

为什么可以这样分：

- **SSTK 行**：货进过 DC 库存池，pegging 在入库时已断开、出库时按「商品+批次」重建 → 不需要行 ID
- **XDK 行**：货从未进 DC 库存池，pegging 必须一路带到底 → 必须有行 ID

> **结论：报文结构统一，一张回传里可以混两种模式的行。**
> 不拆两个接口，不给 XDK 强行造批次去匹配，也不要求 SSTK 硬凑行 ID。

### 3.3 XDK 的行 ID 从哪来 —— 容器标签

```
PFC 越库预分配 → 生成门店入库单行 ID → 下发给 WHC
WHC 生成容器标签, SSCC 编码: 门店号 + inbound_line_id  (GS1 AI 403 路由码)
供应商预贴 / DC 分拣时贴
门店收货扫容器 → 读出 pegging → 按行 ID 回传
```

**这是「一单到底」的实现机制，也是 WHC 必须拥有容器标签的原因。**

### 3.4 XDK 在 PFC 侧的过账口径（待决策）

| 方案 | 过账 | DC 库存 | 适用 |
| --- | --- | --- | --- |
| **A. 视为 DC 瞬时进出** | 供应商→DC（收货）、DC→门店（发货），两次 | 瞬时进出，周转率虚高 | **采购合同是「送到 DC」，货权在 DC 转移**（自营零售通常如此） |
| **B. 视为供应商直送** | 供应商→门店，一次；DC 仅中转 | 干净 | 采购合同是「送到门店」，DC 只提供分拣服务 |

> **判据：货权在哪转移，就在哪过账。**
> 若 DC 要对供应商短溢负责、要与供应商结算，必须走 A —— 否则 DC 的收货差异无处记账。

---

## 4. 单据数据模型与上下游关键字段

### 4.1 调拨主单 `transfer_order`（PFC 内部）

`transfer_no`, `from_node_id`, `to_node_id`, `owner_id`, `required_arrive_date`

行：`sku_id`, `qty`, `uom`, `operation_mode`(SSTK/XDK) —— **无批次**

### 4.2 出库单 `outbound_order`（PFC → 发货 WMS）

**上游**：`transfer_no` + 行

| 字段 | 关键性 |
| --- | --- |
| `outbound_no` | |
| `source_doc_type`/`source_doc_no` = `TRANSFER`/`transfer_no` | 溯源 |
| **`ship_to_node_id`** | **门店 —— 发运凭证按此切分** |
| `owner_id` | 货权 |
| `required_ship_time` | 波次截单依据 |
| 行：`sku_id`, `order_qty`, `uom`，**无 `lot_no`** | 批次归 WMS |
| 行：**`operation_mode`** = SSTK/XDK | **必须打在行上** —— 混发的前提 |
| 行：`pegging_ref`（XDK 才有） | 门店入库单行 ID |

**下游**：`outbound_no + line_no` → 容器内容溯源 → 发货明细回传

### 4.3 越库 ASN（PFC → 发货 WMS，XDK 路径）

与出库单**并列**，是发运凭证的第二个来源。

`asn_no`, `supplier_id`；
行：`sku_id`, `expected_qty`, **`dest_node_id`（预分配门店）**, **`pegging_ref`（门店入库单行 ID）**, `is_pre_labeled`

### 4.4 容器 `container` / `container_content`（WHC 拥有）★ 枢纽

| 层 | 关键字段 |
| --- | --- |
| `container` | `lpn`(SSCC), `parent_lpn`, `container_type`, **`dest_node_id`(门店)**, `status`, `current_location` |
| `container_content` | `lpn`, `line_no`, `sku_id`, **`batch_no`**(WMS 产生), `qty`, **`ref_doc_type`**(OUTBOUND/ASN), **`ref_doc_no`**, **`ref_line_no`**, **`source_mode`**, **`pegging_ref`** |

> `container_content` 行级的 `ref_doc_*` + `source_mode` + `pegging_ref`
> **就是「容器与单据解耦但保留溯源」的落地方式**：容器头不绑单据，内容行绑。

**标签编码（GS1-128）**

```
(00)  SSCC 容器号
(01)  GTIN
(10)  批次                              ← WMS 产生
(17)  效期
(37)  数量
(403) 路由码 = 门店号 [+ inbound_line_id]  ← XDK 一单到底的载体
(410) 收货方 GLN
```

### 4.5 装车单 `load`（WHC / TMS）

结构见 [04 §2](04-transport-delivery.md) 与 [09 §2](09-load-relationships.md)。与本方案相关的三个字段：

| 字段 | 交互作用 |
| --- | --- |
| `load_no` | 发运凭证的切分维度之一 |
| `load_stop.node_id` | **门店** —— 发运凭证的另一个切分维度 |
| `load_detail.lpn` | **只存 root LPN**，展开靠容器树 |

### 4.6 发运凭证 `shipment`（WHC → PFC）★ 核心新增对象

**上游**：`load` + 实装容器（发车时反算，见 [10](10-goods-issue-timing.md)）

| 字段 | 上下游作用 |
| --- | --- |
| **`shipment_no`** | **PFC 的在途库存键** |
| `load_no`, `stop_seq` | 来自 WHC |
| `ship_from_node_id` / `ship_to_node_id` | DC / **门店** |
| `owner_id`, `title_transfer_point`, `inventory_bucket` | 货权与在途归属 |
| `plate_no`, `carrier_id`, `seal_no` | 门店核对依据 |
| `actual_depart_time` | **过账时点** |
| `posting_date` | 账期归属（按仓库作业日） |
| `total_pallets` / `total_cases` / `container_list` | 门店点收依据 |

**`shipment_line`**

| 字段 | 说明 |
| --- | --- |
| `sku_id`, `batch_no`, `qty`, `uom` | **由实装容器反算，不抄出库单** |
| **`source_mode`** | `SSTK` / `XDK` |
| `ref_doc_type` / `ref_doc_no` / `ref_line_no` | 来源出库单行 或 ASN 行 |
| `pegging_type` / `pegging_ref` | XDK 必填：门店入库单行 ID |
| `owner_id` | |

**下游**：PFC 用它 ① 建在途 ② 1:1 生成门店入库单 ③ 下发收货 WMS

### 4.7 发货明细回传（发货 WMS → PFC，按出库单维度）

| 字段 | 说明 |
| --- | --- |
| `outbound_no`, `line_no` | **按出库单维度** |
| `sku_id`, `batch_no`, `shipped_qty` | 商品 + 批次 |
| **`shipment_no`** | **关联发运凭证 —— 让 PFC 能把两个视角对起来** |
| `container_list` | 可选，追溯用 |
| `idem_key` | 幂等 |

> 加 `shipment_no` 这一个字段，PFC 就能验证「出库单核销视角」与「在途配对视角」一致，
> 不需要额外的对账作业。

### 4.8 门店入库单 `inbound_order`（PFC → 收货 WMS）

**上游**：`shipment`（**1:1**）

| 字段 | 说明 |
| --- | --- |
| `inbound_no` | |
| **`shipment_no`** | **1:1 溯源，调拨配对的锚点** |
| `source_doc_type`/`source_doc_no` | `TRANSFER` / 原调拨单（可多个，仅溯源） |
| `from_node_id` | DC |
| `plate_no`, `seal_no`, `expected_arrive` | 门店预约与核对 |
| `is_pre_labeled` = 1, `container_list` | **扫容器即收货** |
| 行：`sku_id`, `plan_qty`, `uom` | **无批次** |
| 行：`source_mode` | SSTK / XDK |
| 行：`pegging_ref` | XDK 才有 |

### 4.9 收货回传（收货 WMS → PFC）

| 字段 | SSTK | XDK |
| --- | --- | --- |
| `inbound_no` | ✅ | ✅ |
| `sku_id` + `batch_no` + `received_qty` | ✅ | ✅ |
| `source_mode` | `SSTK` | `XDK` |
| `pegging_ref`（入库单行 ID） | 空 | **必填** |
| `container_list` | ✅ 扫容器识别 | ✅ |
| `idem_key` | ✅ | ✅ |

---

## 5. 正常流时序

```mermaid
sequenceDiagram
  participant P as PFC
  participant H as WHC
  participant A as 发货WMS(DC)
  participant T as TMS
  participant B as 收货WMS(门店)

  P->>A: ① 出库单(商品+数量, ship_to=门店, mode=SSTK)
  P->>A: ①' 越库ASN(dest_node=门店, pegging_ref)
  P->>H: 集单需求
  H->>A: ② 集单方案 + 容器标签(SSCC 含 403 路由码)
  A->>A: 拣货/分拣 → 组容器(batch 由WMS产生)
  A->>H: ③ 容器 STAGED
  H->>T: 配载 → load / load_stop
  A->>H: ③ 装车扫 root LPN
  T->>H: 发车确认
  H->>H: 按实装容器反算, 生成发运凭证(车×门店×货权)
  H->>P: ⑤ 发运凭证 + shipment_line(含 source_mode/pegging_ref)
  A->>P: ④ 发货明细(按出库单, 带 shipment_no)
  P->>P: 核销出库单 / 建在途(键=shipment_no)
  P->>B: ⑥ 门店入库单(1:1 对发运凭证)
  B->>B: 扫容器收货 → 识别批次
  B->>P: ⑦ 收货回传(商品+批次; XDK行带 pegging_ref)
  P->>P: 在途核销 → 门店库存
```

---

## 6. 异常处理（清单与归属）

| 异常 | 归属 | 处理原则 |
| --- | --- | --- |
| **发/收货 WMS 数量不一致** | **PFC**（两个 WMS 互不感知） | 比对 `shipment_line` vs 收货回传行，差异挂 `shipment` 做在途差异池 |
| **XDK 供应商短送** | PFC / 补货 | 按门店优先级重分摊 `pegging_ref`，重发容器标签方案 |
| **门店拒收 / 部分拒收** | WHC + PFC | 货随车返仓 → 反向发运凭证 → 返仓入库单 |
| **甩货（计划装未装上）** | WHC | 发运凭证按实装反算 → **天然无此问题**（见 [10](10-goods-issue-timing.md)） |
| **批次匹配不上（SSTK）** | PFC | 门店收到批次应等于 DC 发出批次；不一致说明中途换货，走差异流程 |
| **发车事件丢失** | WHC | 超时补偿重推（[10 §5](10-goods-issue-timing.md#5-五个必须处理的工程细节)） |
| **容器失联** | WHC | `container.status=SHIPPED` 但无 POD → 在途异常告警 |

---

## 7. 待决策项

| # | 决策点 | 建议 |
| --- | --- | --- |
| 1 | XDK 在 PFC 的过账口径 | **方案 A**（DC 瞬时进出），除非采购合同是「送到门店」 |
| 2 | 发运凭证号由 WHC 还是 PFC 发号 | **WHC 发号**，PFC 接受 —— 切分依赖拼车结果 |
| 3 | 门店入库单是否允许一张对多车 | **不允许**，严格 1:1 对发运凭证；否则 M:N 会从后门回来 |
| 4 | WHC 建设范围的第一批 | 容器标签 + pegging + 发运凭证（这三个是解 M:N 的最小集）；装车集单与跨仓编排可第二批 |
