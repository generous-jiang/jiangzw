# 电商仓库自动化出库系统方案

> 面向中大型电商场景的全链路自动化出库设计，覆盖架构、交互时序、业务案例与落地建议。
>
> 所有图形均提供可视化 PNG 与 Mermaid 源码两种形式（点击 `<details>` 查看源码）。

## 一、系统概述

自动化出库系统的核心目标：**订单 → 波次 → 拣选 → 复核 → 打包 → 交接** 全流程无人化或少人化。

| 指标 | 传统人工 | 自动化系统 |
|------|---------|-----------|
| 单件处理时长 | 90~120s | 15~25s |
| 拣选准确率 | 99.2% | 99.99% |
| 单仓日处理峰值 | 3~5 万单 | 30~50 万单 |
| 人力成本 | 100% | 30~40% |

## 二、系统总体架构

![系统总体架构](images/01-architecture.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 15px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    secondaryColor: '#FFF3E0'
    tertiaryColor: '#E8F5E9'
    background: '#FFFFFF'
    mainBkg: '#E1EAFF'
    clusterBkg: '#F5F7FA'
    clusterBorder: '#DEE0E3'
    edgeLabelBackground: '#FFFFFF'
    titleColor: '#1F2329'
---
flowchart TB
    subgraph S1["上游系统"]
        EC["电商平台<br/>淘宝 / 京东 / 抖音"]:::up
        ERP["ERP 系统"]:::up
        TMS_OUT["承运商 TMS"]:::up
    end

    subgraph S2["中台系统层"]
        OMS["OMS<br/>订单管理"]:::mid
        WMS["WMS<br/>仓库管理"]:::mid
        TMS["TMS<br/>运输管理"]:::mid
        BMS["BMS<br/>计费结算"]:::mid
    end

    subgraph S3["执行控制层"]
        WCS["WCS<br/>设备控制"]:::exe
        WES["WES<br/>仓库执行"]:::exe
        PTL["Pick-to-Light<br/>电子标签"]:::exe
    end

    subgraph S4["硬件设备层"]
        AGV["AGV / AMR"]:::hw
        ASRS["堆垛机 / Shuttle"]:::hw
        SORTER["交叉带分拣机"]:::hw
        CONV["输送线"]:::hw
        ROBOT["拣选机器人"]:::hw
        DWS["DWS 动态称重"]:::hw
    end

    EC --> OMS
    ERP --> OMS
    OMS --> WMS
    WMS --> WES
    WES --> WCS
    WCS --> AGV
    WCS --> ASRS
    WCS --> SORTER
    WCS --> CONV
    WCS --> ROBOT
    WCS --> DWS
    WMS --> TMS
    TMS --> TMS_OUT
    WMS --> BMS

    classDef up fill:#FFF3E0,stroke:#FA8C16,color:#1F2329,rx:8,ry:8
    classDef mid fill:#E1EAFF,stroke:#3370FF,color:#1F2329,rx:8,ry:8
    classDef exe fill:#E8F5E9,stroke:#52C41A,color:#1F2329,rx:8,ry:8
    classDef hw fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
```

</details>

**分层职责：**
- **OMS**：订单清洗、拆单合单、库存锁定
- **WMS**：库存管理、波次策略、任务编排
- **WES**：实时调度、任务排序、设备协同
- **WCS**：设备指令翻译、状态回传
- **PTL**：人机交互终端（电子标签拣选/播种）

---

## 三、核心交互时序图

### 3.1 订单接收与履约决策

![订单接收与履约决策](images/02-order-fulfillment.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    sequenceNumberColor: '#FFFFFF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    participant EC as 电商平台
    participant OMS
    participant WMS
    participant INV as 库存中心
    participant TMS

    EC->>OMS: 推送订单(orderId, SKU, 收货地址)
    OMS->>OMS: 订单清洗 / 反欺诈 / 合规校验
    OMS->>INV: 查询可用库存(SKU, 区域)
    INV-->>OMS: 多仓库存分布
    OMS->>OMS: 履约决策引擎(选仓 / 拆单 / 合单)

    alt 单仓履约
        OMS->>WMS: 下发出库单
    else 多仓拆单
        OMS->>OMS: 按 SKU 拆分子订单
        OMS->>WMS: 下发子单 A 至仓库1
        OMS->>WMS: 下发子单 B 至仓库2
    end

    WMS->>INV: 锁定库存
    INV-->>WMS: 锁定成功
    WMS->>TMS: 预约承运商资源
    TMS-->>WMS: 返回运单号 / 预约时间
    WMS-->>OMS: 出库单受理成功
    OMS-->>EC: 订单状态:已接单
```

</details>

### 3.2 波次规划与任务下发

![波次规划与任务下发](images/03-wave-planning.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    participant WMS
    participant WAVE as 波次引擎
    participant WES
    participant WCS
    participant AGV
    participant SHUTTLE as Shuttle货架

    Note over WMS,WAVE: 每5分钟 / 每500单触发一次波次

    WMS->>WAVE: 待出库订单池
    WAVE->>WAVE: 聚类算法(同SKU合并 / 同分拣口聚集 / 截单时间优先)
    WAVE->>WAVE: 生成波次(WaveID)
    WAVE->>WMS: 波次结果

    WMS->>WES: 下发拣选任务集
    WES->>WES: 任务排序(路径最短优先)

    par 货到人区域
        WES->>WCS: 调度Shuttle出库指令
        WCS->>SHUTTLE: 取货箱A至工作站3
        SHUTTLE-->>WCS: 货箱已到达
        WCS-->>WES: 工作站3可拣选
    and 人到货区域
        WES->>WCS: 调度AGV搬运料箱
        WCS->>AGV: 移动至库位B-12-3
        AGV-->>WCS: 已到达
    end

    WES-->>WMS: 波次执行中
```

</details>

### 3.3 货到人拣选流程（核心）

![货到人拣选流程](images/04-picking.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    participant Picker as 拣选员
    participant PTL as 拣选工作站
    participant WES
    participant WCS
    participant SHUTTLE as Shuttle系统
    participant CONV as 输送线
    participant DWS as 动态称重

    SHUTTLE->>CONV: 货箱送达工位
    CONV->>PTL: RFID识别货箱到位
    PTL->>WES: 请求该工位任务
    WES-->>PTL: 返回任务列表(目标周转箱 / 数量)

    PTL->>Picker: 屏幕显示+灯光提示 取SKU-001 x 2件
    PTL->>Picker: 投放灯亮起 放入周转箱4号

    Picker->>PTL: 扫描SKU条码
    PTL->>PTL: 校验SKU与任务匹配

    alt SKU匹配
        Picker->>PTL: 按确认按钮
        PTL->>WES: 拣选完成(SKU, qty, boxId)
        WES->>WCS: 释放空货箱
        WCS->>SHUTTLE: 回库指令
    else SKU错误
        PTL->>Picker: 红灯报警+蜂鸣
        PTL->>WES: 异常上报
    end

    Note over CONV,DWS: 周转箱满箱后流转
    CONV->>DWS: 周转箱过磅
    DWS->>WES: 实重 vs 理论重

    alt 重量校验通过
        DWS->>CONV: 放行至复核区
    else 重量异常(漏拣 / 多拣)
        DWS->>CONV: 转入异常处理线
        WES->>PTL: 推送异常工单
    end
```

</details>

### 3.4 复核、打包与交接

![复核、打包与交接](images/05-packing.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    participant Tote as 周转箱
    participant SCAN as 复核台
    participant Packer as 打包员
    participant LABEL as 标签打印机
    participant SORTER as 交叉带分拣机
    participant TRUCK as 装车口
    participant TMS
    participant WMS
    participant OMS
    participant EC as 电商平台

    Tote->>SCAN: 输送线送达复核台
    SCAN->>SCAN: 扫码识别boxId
    SCAN->>WMS: 拉取订单明细

    alt 全自动复核
        SCAN->>SCAN: 视觉识别+称重三向校验
        SCAN-->>Packer: 校验通过,允许打包
    else 人工复核
        Packer->>SCAN: 逐件扫码
        SCAN->>Packer: 屏幕实时核对
    end

    Packer->>Packer: 装入纸箱+填充物
    SCAN->>LABEL: 触发面单打印
    LABEL->>Packer: 输出面单+发票
    Packer->>SCAN: 贴单后回扫

    SCAN->>TMS: 包裹绑定运单号
    TMS-->>SCAN: 确认+返回分拣口编号
    SCAN->>SORTER: 注入交叉带

    SORTER->>SORTER: 扫描面单条码计算落格
    SORTER->>TRUCK: 滑落至对应承运商笼车

    TRUCK->>TMS: 笼车满载,触发交接
    TMS->>TMS: 生成交接清单
    TMS-->>WMS: 出库完成
    WMS-->>OMS: 更新订单为已发货
    OMS-->>EC: 推送物流信息
```

</details>

### 3.5 异常处理流程

![异常处理流程](images/06-exception.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    participant System as 任意环节
    participant EXC as 异常中心
    participant WMS
    participant Ops as 现场主管
    participant OMS
    participant WCS
    participant WES

    System->>EXC: 上报异常(类型 / 单号 / 位置)
    EXC->>EXC: 异常分类

    alt 缺货
        EXC->>WMS: 触发盘点任务
        WMS->>OMS: 部分缺货,询问处理
        OMS->>OMS: 自动调拨 / 取消 / 换仓
    else 商品破损
        EXC->>Ops: 推送至PDA
        Ops->>EXC: 拍照+原因登记
        EXC->>WMS: 生成不良品入库单
        EXC->>OMS: 申请补拣
    else 设备故障
        EXC->>WCS: 故障设备隔离
        EXC->>WES: 任务重路由
        EXC->>Ops: 派工维修
    else 称重不符
        EXC->>EXC: 自动复称1次
        alt 仍不符
            EXC->>Ops: 转人工开箱核查
        end
    end
```

</details>

---

## 四、典型业务案例

### 案例 1：日常单仓履约（标准场景）

> **场景**：用户在某电商下单 1 瓶洗发水 + 1 包面巾纸，配送到上海。

**履约链路：**
1. **10:00:05** 订单进 OMS，履约引擎判定上海仓库存充足，单仓发货
2. **10:00:08** WMS 锁定库存，进入待波次池
3. **10:05:00** 波次引擎将该订单与其他 480 单合并为 Wave-2026052601
4. **10:05:30** Shuttle 调度货箱出库，AGV 同步搬运面巾纸料箱
5. **10:07:12** 拣选员在工作站完成 2 件拣选，投入周转箱 #047
6. **10:08:30** 周转箱满 12 单后流转复核台，DWS 通过
7. **10:09:00** 自动打包机封箱，面单贴附
8. **10:10:15** 交叉带分拣至顺丰口，装笼车
9. **11:30:00** 顺丰司机交接，订单状态变更为"已发货"

**总耗时：约 90 分钟，人工触点 1 次（拣选确认）**

---

### 案例 2：双 11 大促爆单（峰值压力）

> **场景**：双 11 零点开始 1 小时内涌入 50 万订单。

**关键策略：**

![大促削峰策略](images/07-peak-strategy.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 15px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    background: '#FFFFFF'
---
flowchart LR
    A["📦 订单洪峰"]:::peak --> B{"削峰策略"}:::decision
    B --> C["Kafka 消息缓冲"]:::layer1
    B --> D["库存预占<br/>(无锁化)"]:::layer1
    B --> E["波次预生成<br/>(提前30分钟)"]:::layer1

    C --> F["OMS 分批消费"]:::layer2
    D --> G["Redis 原子扣减"]:::layer2
    E --> H["预备货至缓存货架"]:::layer2

    F --> I["WMS"]:::core
    G --> I
    H --> I

    I --> J["多波次并行<br/>20条产线齐开"]:::output
    J --> K["临时增设<br/>移动复核台"]:::output

    classDef peak fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
    classDef decision fill:#FFF7E6,stroke:#FA8C16,color:#1F2329
    classDef layer1 fill:#E1EAFF,stroke:#3370FF,color:#1F2329,rx:8,ry:8
    classDef layer2 fill:#E6F4FF,stroke:#1677FF,color:#1F2329,rx:8,ry:8
    classDef core fill:#F0F5FF,stroke:#2F54EB,color:#1F2329,rx:8,ry:8
    classDef output fill:#E8F5E9,stroke:#52C41A,color:#1F2329,rx:8,ry:8
```

</details>

**应对措施：**
- **库存预占**：大促前 24h，热销 SKU 预拉至前置缓存库位（缩短取货距离 70%）
- **波次预生成**：提前生成 200 个空波次模板，订单进来直接填槽
- **柔性产能**：AGV 集群从 80 台动态扩至 150 台，复核台从 20 工位扩至 50 工位
- **降级方案**：超阈值后非急单延后 2 小时拣选，保障 24h 内出库 SLA
- **结果**：峰值 25 万单/小时，履约时效 6 小时内出库率 95%

---

### 案例 3：跨仓拆单（多仓履约）

> **场景**：用户买了 3 件商品：手机（华南仓有货）、手机壳（华东仓有货）、贴膜（华北仓有货）。

**履约决策对比：**

| 决策维度 | 方案 A：等齐发 | 方案 B：拆 3 单 | **采纳方案 C：拆 2 单** |
|---------|--------------|---------------|---------------------|
| 时效 | 慢（要调拨） | 最快 | 快 |
| 成本 | 调拨成本高 | 3 笔运费 | 2 笔运费 |
| 体验 | 一次签收 | 3 次签收 | 2 次签收 |

**最终拆单**：手机壳 + 贴膜从华东仓合发，手机从华南仓单发。OMS 给用户展示统一的"拆 2 个包裹发出"提示。

---

### 案例 4：异常订单恢复（库存差异）

> **场景**：拣选时发现 SKU-A8821 实际只剩 0 件（系统显示 5 件）。

**处理链路：**

![库存差异恢复](images/08-stockout-recovery.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    participant Picker as 拣选员
    participant PDA
    participant EXC as 异常中心
    participant WMS
    participant OMS
    participant User as 客户

    Picker->>PDA: 上报"库位空"
    PDA->>EXC: 异常工单
    EXC->>WMS: 触发紧急盘点
    WMS->>WMS: 全仓搜寻该SKU

    alt 找到货
        WMS->>EXC: 库位修正B-3-7
        EXC->>Picker: 派新拣选任务
    else 全仓缺货
        WMS->>OMS: 上报缺货
        OMS->>OMS: 调拨决策
        alt 邻仓有货
            OMS->>WMS: 转单至杭州仓
        else 全网缺货
            OMS->>User: 短信:缺货可选退款 / 等待补货
        end
    end
```

</details>

---

## 五、关键流程深度剖析

仓库自动化的核心难度集中在两次"业务态 → 物理态"的转换：**波次 → 拣货**、**拣货 → 分拣**。这两个环节最复杂、最容易出错，也是优化收益最高的地方。

### 5.1 从波次到拣货

#### 业务背景

波次（Wave）是 WMS 输出的"作业批次"，但拣选员/AGV 看到的是"拣选任务（PickTask）"。从波次到拣货，系统要在毫秒级内完成 4 件事：拆解、调度、设备协同、执行回写。

#### 全景 Pipeline

![波次到拣货 全景 pipeline](images/10-wave-to-pick-pipeline.png)

<details><summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    background: '#FFFFFF'
    clusterBkg: '#F5F7FA'
    clusterBorder: '#DEE0E3'
---
flowchart LR
    W["📦 波次<br/>500单 / 800 SKU"]:::input

    subgraph S1["① WMS · 任务拆解"]
        direction TB
        A1["按拣选区域拆<br/>B区货到人 / C区人到货"]:::wms
        A2["按设备类型拆<br/>Shuttle / AGV / 人工"]:::wms
        A3["按 SKU 特性拆<br/>冷链 / 大件 / 易碎"]:::wms
        A1 --> A2 --> A3
    end

    P["🗂 PickTask 任务池<br/>1200 个原子任务"]:::pool

    subgraph S2["② WES · 调度优化"]
        direction TB
        B1["路径优化<br/>Savings / S形路径"]:::wes
        B2["工位负载均衡<br/>8工位 × 150任务"]:::wes
        B3["截单时间排序"]:::wes
        B1 --> B2 --> B3
    end

    Q["📋 工位任务队列"]:::pool

    subgraph S3["③ WCS · 设备调度"]
        direction TB
        C1["Shuttle 出货箱"]:::wcs
        C2["AGV 搬料箱"]:::wcs
        C3["PTL 亮灯+显示"]:::wcs
    end

    subgraph S4["④ 执行层"]
        direction TB
        E1["扫码校验"]:::run
        E2["取件投放"]:::run
        E3["按钮确认"]:::run
        E1 --> E2 --> E3
    end

    R["✅ 周转箱满12单<br/>流转分拣线"]:::output

    W --> S1 --> P --> S2 --> Q --> S3 --> S4 --> R

    classDef input fill:#FFF3E0,stroke:#FA8C16,color:#1F2329,rx:8,ry:8
    classDef pool fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
    classDef wms fill:#E1EAFF,stroke:#3370FF,color:#1F2329,rx:8,ry:8
    classDef wes fill:#E6F4FF,stroke:#1677FF,color:#1F2329,rx:8,ry:8
    classDef wcs fill:#F0F5FF,stroke:#2F54EB,color:#1F2329,rx:8,ry:8
    classDef run fill:#E8F5E9,stroke:#52C41A,color:#1F2329,rx:8,ry:8
    classDef output fill:#FFF7E6,stroke:#FA8C16,color:#1F2329,rx:8,ry:8
```

</details>

#### 4 个阶段拆解

| 阶段 | 责任系统 | 核心动作 | 关键算法 / 策略 | 典型耗时 |
|------|--------|---------|---------------|---------|
| ① 任务拆解 | WMS | 1 单订单 → N 个 PickTask（按区域 / 设备 / SKU 特性） | 主备库位选择（FIFO + 距离最短）| ~1s / 波次 |
| ② 调度优化 | WES | 1200 任务 → 8 工位队列 | Savings / S 形路径 / TSP 近似 | 3~5s |
| ③ 设备调度 | WCS | 翻译为 Shuttle / AGV / PTL 指令 | 死锁检测 / 优先级抢占 | 实时 |
| ④ 执行回写 | PTL + 现场 | 扫码、投放、确认、防错 | RFID + 重量双校验 | 15~25s / 件 |

#### 详细交互时序

![波次到拣货 详细时序](images/11-wave-to-pick-sequence.png)

<details><summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    autonumber
    participant WMS
    participant WES as WES 调度
    participant WCS as WCS 设备控制
    participant SHUTTLE as Shuttle货架
    participant AGV
    participant PTL as 拣选工作站
    participant Picker as 拣选员

    Note over WMS: 波次落库 状态READY

    WMS->>WMS: 拆解 PickTask(按区域 设备 SKU特性)
    WMS->>WES: 推送任务集 1200条
    WES->>WES: Savings 路径优化
    WES->>WES: 工位负载均衡

    par 货到人通道
        WES->>WCS: 请求货箱(SKU-001@B-12-3)
        WCS->>SHUTTLE: 出库指令
        SHUTTLE-->>WCS: 已送达工位3
        WCS-->>WES: 工位3 ready
        WES->>PTL: 下发任务(SKU-001 x2)
        PTL->>Picker: 灯亮+屏显
        Picker->>PTL: 扫码 SKU-001
        PTL->>PTL: 防错校验
        Picker->>PTL: 投放周转箱4号
        Picker->>PTL: 按钮确认
        PTL->>WES: 完成回写
        WES->>WCS: 释放货箱
        WCS->>SHUTTLE: 回库
    and 人到货通道
        WES->>PTL: 推送行走路径(B3-7 → B5-2 → B8-1)
        Picker->>PTL: 到达 B3-7
        Picker->>PTL: 扫库位+扫SKU
        PTL->>WES: 拣完 1件
        WES->>AGV: 调度AGV接驳料箱回流
        AGV-->>WES: 已回收
    end

    Note over WES,Picker: 周转箱满12单 触发流转

    WES->>WMS: 满箱信号 (boxId=047)
    WMS->>WMS: 注册到分拣等待池
    WMS-->>WES: 进度上报 拣选完成 100%
```

</details>

#### PickTask 状态机

任务从生成到完成会经历 7 种状态，每种状态都有对应的回滚或补偿路径：

![PickTask 状态机](images/12-pick-task-state.png)

<details><summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    background: '#FFFFFF'
---
stateDiagram-v2
    [*] --> CREATED: WMS 拆解
    CREATED --> ASSIGNED: WES 分配工位
    ASSIGNED --> WAITING_GOODS: 等待货到 / 拣选员到位
    WAITING_GOODS --> PICKING: 货到工位 / 到达库位
    PICKING --> CONFIRMED: 扫码校验通过
    PICKING --> ERROR: 校验失败 / 扫错SKU
    ERROR --> PICKING: 重试
    ERROR --> SHORT_PICK: 库存不足
    CONFIRMED --> COMPLETED: 投放确认 + 重量校验
    SHORT_PICK --> COMPLETED: 部分完成 + 标记缺
    COMPLETED --> [*]

    ASSIGNED --> CANCELED: 订单取消 / 波次回滚
    WAITING_GOODS --> CANCELED
    CANCELED --> [*]
```

</details>

#### 实战案例：500 单波次落地

> **场景**：Wave-2026052601，500 单，800 SKU，截单时间 11:00。

| 时间 | 事件 | 数据 |
|------|------|------|
| 10:05:00.000 | 波次触发 | 500 单进入 WAVE_READY |
| 10:05:00.420 | WMS 拆解完成 | 1200 个 PickTask（货到人 720 / 人到货 480）|
| 10:05:03.100 | WES 路径优化完成 | 平均行走距离从 240m 降到 87m（-64%）|
| 10:05:03.300 | 工位分配完成 | 8 工位 × 平均 150 任务 |
| 10:05:04 ~ 10:22:00 | 并行执行 | Shuttle 出 240 箱、AGV 行驶 9.2 km |
| 10:22:30 | 全部 COMPLETED | 准确率 99.97%（3 个 SKU 因库位空进入 SHORT_PICK，其中 2 个找到备份库位、1 个真缺货）|

**关键优化点**：
- **路径合并**：相邻库位的任务合并到同一拣选员，减少 64% 行走距离
- **货箱共享**：同一波次内 SKU-001 被 87 个订单需要 → 该货箱只调度 1 次，停留工位 4 分钟服务完所有订单
- **回滚兜底**：1 单缺货后 OMS 调拨决策 200ms 内完成，转单到杭州仓继续履约

---

### 5.2 从拣货到分拣

#### 业务背景

拣货完成的周转箱里装的是 **混拣物**（一个箱里有 12 个不同订单的商品）。要让物流车装的是 **以承运商为单位的笼车**，需要经过"拆 → 装 → 分 → 装车"4 步转换。

这一段是仓库的"最后 100 米"——离客户体验最近，也是单件成本最敏感的环节。

#### 全景 Pipeline

![拣货到分拣 全景 pipeline](images/13-pick-to-sort-pipeline.png)

<details><summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    background: '#FFFFFF'
    clusterBkg: '#F5F7FA'
    clusterBorder: '#DEE0E3'
---
flowchart LR
    IN["🗳 周转箱满载<br/>12单 / 31件"]:::input

    subgraph S1["① 复核 (DWS)"]
        direction TB
        CK["视觉识别 + 称重<br/>三向校验"]:::dws
        OK1["通过"]:::ok
        EX1["异常"]:::err
        CK --> OK1
        CK --> EX1
        EX1 --> MAN["人工开箱核查"]:::man
        MAN --> OK1
    end

    subgraph S2["② 拆单 + 打包"]
        direction TB
        SP["按订单拆分<br/>1箱 → N包裹"]:::pack
        BX["箱型决策引擎<br/>A/B/C/D 4种"]:::pack
        FL["填充物 / 防震"]:::pack
        LB["运单号 + 面单"]:::pack
        SP --> BX --> FL --> LB
    end

    subgraph S3["③ 分拣机注入"]
        direction TB
        SC["扫描门读面单"]:::sort
        CL["匹配落格规则<br/>承运商 / 区域 / 时效"]:::sort
        CT["交叉带分拣机<br/>滑落"]:::sort
        SC --> CL --> CT
    end

    subgraph S4["④ 落格 + 装载"]
        direction TB
        G1["顺丰口"]:::carrier
        G2["京东口"]:::carrier
        G3["中通口"]:::carrier
        G4["邮政口"]:::carrier
        G5["自营急送"]:::carrier
    end

    subgraph S5["⑤ 交接出库"]
        direction TB
        CG["笼车满 / 截单到时"]:::out
        HD["扫码交接 + 清单"]:::out
        UP["WMS 回写已发货"]:::out
        CG --> HD --> UP
    end

    IN --> S1 --> S2 --> S3 --> S4 --> S5

    classDef input fill:#FFF7E6,stroke:#FA8C16,color:#1F2329,rx:8,ry:8
    classDef dws fill:#F0F5FF,stroke:#2F54EB,color:#1F2329,rx:8,ry:8
    classDef ok fill:#E8F5E9,stroke:#52C41A,color:#1F2329,rx:8,ry:8
    classDef err fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
    classDef man fill:#FFFBE6,stroke:#FAAD14,color:#1F2329,rx:8,ry:8
    classDef pack fill:#E6F4FF,stroke:#1677FF,color:#1F2329,rx:8,ry:8
    classDef sort fill:#E1EAFF,stroke:#3370FF,color:#1F2329,rx:8,ry:8
    classDef carrier fill:#F9F0FF,stroke:#722ED1,color:#1F2329,rx:8,ry:8
    classDef out fill:#E8F5E9,stroke:#52C41A,color:#1F2329,rx:8,ry:8
```

</details>

#### 5 个阶段拆解

| 阶段 | 设备 / 系统 | 核心动作 | 关键数据 | 典型耗时 |
|------|-----------|---------|---------|---------|
| ① 复核 | DWS（视觉 + 称重）| 三向校验：视觉识别 SKU、实重 vs 理论重、件数核对 | 通过率 95%+、误判率 <0.5% | 5s / 箱 |
| ② 拆单打包 | 半自动打包工位 | 按订单拆、选箱型、填充、贴面单 | 箱型 4 种自动决策、面单 1.2s 打印 | 30~60s / 单 |
| ③ 分拣注入 | 交叉带分拣机 | 扫面单 → 计算落格 | 单线 6000~12000 件/h | 2s / 件 |
| ④ 落格装载 | 笼车 + 装车口 | 同承运商 / 同线路聚集 | 落格准确率 99.99% | 实时 |
| ⑤ 交接出库 | TMS + 司机 | 笼车满载或截单到时间，扫码交接 | 单笼平均 80 件 | 5min / 笼 |

#### 1 → N 分流案例

一个周转箱出来后，它的内容会以"包裹"为单位扇出到多个承运商。这是整个流程的"扇出图"：

![1→N 分流图](images/14-pick-to-sort-fanout.png)

<details><summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 13px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    background: '#FFFFFF'
---
flowchart LR
    T0["🗳 周转箱 #047<br/>12 单 / 31 件"]:::tote

    T0 --> O_A["订单A · 1单<br/>洗发水+面巾"]:::o
    T0 --> O_B["订单B · 1单<br/>手机壳x2"]:::o
    T0 --> O_C["订单C-G · 5单<br/>SKU各异"]:::o
    T0 --> O_H["订单H-K · 4单<br/>小件混装"]:::o
    T0 --> O_L["订单L · 1单<br/>大件家电"]:::oBig

    O_A --> P_A["📦 包裹A<br/>箱型A"]:::pack
    O_B --> P_B["📦 包裹B<br/>箱型A"]:::pack
    O_C --> P_C["📦 包裹C-G<br/>箱型B×3 + C×2"]:::pack
    O_H --> P_H["📦 包裹H-K<br/>箱型A×2 + B×2"]:::pack
    O_L --> P_L["📦 包裹L<br/>箱型D 加固"]:::packBig

    P_A --> SF["🚚 顺丰<br/>5 单"]:::sf
    P_B --> SF
    P_H --> SF
    P_C --> JD["🚚 京东物流<br/>3 单"]:::jd
    P_C --> ZTO["🚚 中通<br/>2 单"]:::zto
    P_H --> EMS["🚚 邮政<br/>1 单"]:::ems
    P_L --> EXP["⚡ 自营急送<br/>1 单"]:::exp

    classDef tote fill:#FFF7E6,stroke:#FA8C16,color:#1F2329,rx:8,ry:8
    classDef o fill:#E1EAFF,stroke:#3370FF,color:#1F2329,rx:8,ry:8
    classDef oBig fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
    classDef pack fill:#F0F5FF,stroke:#2F54EB,color:#1F2329,rx:8,ry:8
    classDef packBig fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
    classDef sf fill:#E8F5E9,stroke:#52C41A,color:#1F2329,rx:8,ry:8
    classDef jd fill:#FFF7E6,stroke:#FA8C16,color:#1F2329,rx:8,ry:8
    classDef zto fill:#F9F0FF,stroke:#722ED1,color:#1F2329,rx:8,ry:8
    classDef ems fill:#E6F4FF,stroke:#1677FF,color:#1F2329,rx:8,ry:8
    classDef exp fill:#FFF1F0,stroke:#F5222D,color:#1F2329,rx:8,ry:8
```

</details>

#### 详细交互时序

![拣货到分拣 详细时序](images/15-pick-to-sort-sequence.png)

<details><summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 14px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    actorBkg: '#E1EAFF'
    actorBorder: '#3370FF'
    actorTextColor: '#1F2329'
    actorLineColor: '#BFBFBF'
    signalColor: '#1F2329'
    signalTextColor: '#1F2329'
    labelBoxBkgColor: '#E1EAFF'
    labelBoxBorderColor: '#3370FF'
    labelTextColor: '#1F2329'
    loopTextColor: '#1F2329'
    activationBorderColor: '#3370FF'
    activationBkgColor: '#F0F4FF'
    noteBkgColor: '#FFFBE6'
    noteTextColor: '#1F2329'
    noteBorderColor: '#FFD666'
---
sequenceDiagram
    autonumber
    participant Tote as 周转箱047
    participant DWS as 复核台 DWS
    participant Packer as 打包工位
    participant TMS
    participant SORTER as 交叉带分拣机
    participant Cage as 笼车
    participant WMS

    Tote->>DWS: 抵达复核台 输送线触发
    DWS->>WMS: 拉取订单明细
    DWS->>DWS: 视觉识别 + 称重三向校验

    alt 通过 (11/12)
        DWS-->>Packer: 放行
    else 异常 1单 重量+0.3kg
        DWS->>Packer: 异常工单 开箱核查
        Packer->>Packer: 发现赠品未登记
        Packer->>WMS: 补登记 SKU-G099
        Packer->>DWS: 复扫通过
    end

    loop 12 个订单逐单打包
        Packer->>TMS: 申请运单号 订单ID
        TMS-->>Packer: waybillNo + 承运商 + 落格号
        Packer->>Packer: 选箱型 + 装箱 + 填充
        Packer->>Packer: 贴面单
        Packer->>SORTER: 注入交叉带 含面单条码
    end

    Note over SORTER: 12 个包裹分散流入主线

    loop 每个包裹
        SORTER->>SORTER: 扫面单 匹配落格规则
        SORTER->>Cage: 滑落对应承运商笼车
    end

    Note over Cage: 5 个承运商口分别归集 顺丰5/京东3/中通2/邮政1/自营1

    Cage->>TMS: 笼车满 / 截单到时 触发交接
    TMS->>TMS: 生成交接清单 扫码核对
    TMS-->>WMS: 出库完成 12单
    WMS->>WMS: 状态 已发货 推送物流信息
```

</details>

#### 实战案例：周转箱 #047 出库

> **场景**：周转箱 #047 装载 12 单（含赠品异常 1 单、大件 1 单、急送 1 单）。

| 时间 | 阶段 | 事件 | 处理 |
|------|------|------|------|
| 10:22:30 | 抵达复核台 | DWS 三向校验 | 11 单通过 |
| 10:22:35 | 异常分流 | 1 单实重 +0.3kg | 转人工开箱核查 |
| 10:23:10 | 异常处置 | 发现赠品 SKU-G099 未上架登记 | 补登记，复扫通过 |
| 10:23:20 ~ 10:25:30 | 拆单打包 | 12 单逐个打包 | 选箱型 A×7 / B×3 / C×1 / D×1 |
| 10:25:30 ~ 10:26:10 | 注入分拣 | 12 包裹陆续上交叉带 | 扫面单计算落格 |
| 10:26:00 ~ 10:26:30 | 落格 | 5 个承运商口分流 | 顺丰5 / 京东3 / 中通2 / 邮政1 / 自营1 |
| 10:35:00 | 自营急送 | 包裹 L 优先单独装车 | 30 分钟内出仓（同城 2h 达 SLA）|
| 11:00:00 | 笼车交接 | 顺丰司机扫码取走笼车 | 80 件 / 笼，出库回写 |

**总耗时**：从满箱到全部出库 ≈ 38 分钟，自动化覆盖率 92%（12 单中 1 单需要人工干预 1 次）。

**关键优化点**：
- **DWS 三向校验**：视觉 + 重量 + 件数任意 1 项异常即转人工，把误差拦截在打包前
- **箱型决策引擎**：根据 SKU 体积 + 易碎度 + 客户偏好，毫秒级输出最优箱型，节省 18% 包材成本
- **落格规则引擎**：以"承运商 × 区域 × 时效"三维匹配，急送单走专属通道避免被普通单堵塞
- **赠品异常**：占异常总量的 35%，通过自动复称识别后人工补登记，解决方案是"赠品在拣选时同步入箱"

---

## 六、数据模型核心实体

![核心数据模型 ER 图](images/09-erd.png)

<details>
<summary>查看 Mermaid 源码</summary>

```mermaid
---
config:
  theme: base
  themeVariables:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: 13px
    primaryColor: '#E1EAFF'
    primaryTextColor: '#1F2329'
    primaryBorderColor: '#3370FF'
    lineColor: '#646A73'
    background: '#FFFFFF'
---
erDiagram
    ORDER ||--o{ ORDER_ITEM : contains
    ORDER ||--|| OUTBOUND_ORDER : generates
    OUTBOUND_ORDER ||--|{ WAVE_ITEM : "归入"
    WAVE ||--|{ WAVE_ITEM : contains
    WAVE_ITEM ||--|| PICK_TASK : generates
    PICK_TASK }o--|| LOCATION : "from"
    PICK_TASK }o--|| TOTE : "into"
    TOTE ||--o{ PACKAGE : "split into"
    PACKAGE ||--|| WAYBILL : "carries"

    ORDER {
        string orderId PK
        string userId
        decimal amount
        string status
        datetime createdAt
    }
    OUTBOUND_ORDER {
        string outboundId PK
        string orderId FK
        string warehouseId
        string waveId FK
        string status
    }
    WAVE {
        string waveId PK
        string strategy
        int orderCount
        datetime cutoffTime
    }
    PICK_TASK {
        string taskId PK
        string sku
        int quantity
        string fromLocation
        string toToteId
        string pickerId
    }
    PACKAGE {
        string packageId PK
        decimal weight
        string carrier
        string waybillNo
    }
```

</details>

---

## 七、技术栈建议

| 层级 | 推荐技术 |
|------|---------|
| 接入层 | Nginx + Spring Cloud Gateway |
| 服务层 | Java (Spring Boot) / Go，DDD 微服务 |
| 消息 | Kafka（订单流）+ RocketMQ（事务消息）|
| 数据库 | MySQL（交易）+ TiDB（库存）+ Redis（缓存）|
| 实时计算 | Flink（波次/库存预警）|
| 设备通信 | OPC UA / Modbus / MQTT |
| 监控 | Prometheus + Grafana + SkyWalking |
| 大屏 | ECharts + WebSocket 推流 |

---

## 八、关键实施建议

1. **从半自动起步**：先上 WMS + PTL，再逐步引入 AGV / Shuttle，避免一次性高投入
2. **数据先行**：SKU 主数据（尺寸、重量、分类）质量决定 60% 的自动化效果
3. **分波次灰度**：新策略先在 5% 流量小波次验证，再全量
4. **应急预案常态化**：每月演练设备宕机、网络中断、断电等场景
5. **ROI 测算**：单仓投资约 3000~8000 万，回收期 2~3 年，需匹配单量规模
