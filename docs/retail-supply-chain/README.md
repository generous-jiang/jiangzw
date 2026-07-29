# 零售供应链物流领域参考架构

面向「多仓（大仓 / 电商仓 / 门店全渠道仓）+ 多配（干线 TMS / 末端 DMS）」的零售供应链，
给出 **领域边界划分** 与 **核心数据模型**。

## 文档索引

| 文档 | 内容 |
| --- | --- |
| [01-领域边界](01-domain-boundaries.md) | ERP / OMS / WMS / TMS / DMS 的职责、SOR 归属、上下文映射、边界争议裁决 |
| [02-核心数据模型](02-core-data-model.md) | 主数据、库存单元键、库存三视图、库存流水账本（Inventory Ledger） |
| [03-出入库单据与收发货流水](03-inbound-outbound.md) | ASN / 入库单 / 收货流水 / 出库单 / 波次 / 拣货 / 发货流水，含状态机 |
| [04-运输与配送模型](04-transport-delivery.md) | 装车单（Load）/ 运单（Waybill）/ 经停 / 轨迹 / POD / 器具回收 |
| [05-容器与标签体系](05-container-label.md) | LPN / SSCC / GS1-128、容器层级、各环节标签清单 |
| [06-SSTK 与 XDK 作业模式](06-sstk-xdk.md) | 存储型 / 越库型（预分配 & 后分配）、Pegging 模型、PBYL / DSD |
| [07-集成契约与领域事件](07-integration-events.md) | 跨域事件清单、幂等与对账、反腐层设计 |
| [ddl/schema.sql](ddl/schema.sql) | 全部核心表的参考 DDL |

## 六条贯穿全篇的设计原则

1. **按「事实归属（System of Record）」划边界，不按功能菜单划边界。**
   同一个词在不同域里是不同的事实：ERP 的库存是「钱」，WMS 的库存是「货位上的物」，OMS 的库存是「能不能卖」。
2. **单据（Document）与流水（Transaction）分离。**
   单据可改、可撤、有状态机；流水只追加（append-only），冲正用红字记录，永不物理删除。
3. **一切数量变化必须落 Inventory Ledger。** 它是 WMS 与 ERP 对账的唯一真相源。
4. **LPN（容器号）是贯穿仓 → 运 → 配的物理主键。** 装车扫 LPN、签收扫 LPN、异常追溯靠 LPN。
5. **数量必须三元组：`qty + uom + base_qty`。** 箱/托/件的换算基准必须随单据冻结快照，不能实时查主数据。
6. **跨域只走事件 + 幂等键。** 幂等键 = `业务单号 + 单据版本 + 事件类型`。
