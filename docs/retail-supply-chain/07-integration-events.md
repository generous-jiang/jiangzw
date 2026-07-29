# 07 · 集成契约与领域事件

## 1. 事件清单（跨域最小必要集）

| 事件 | 生产者 | 主要消费者 | 载荷要点 |
| --- | --- | --- | --- |
| `Purchase.OrderReleased` | ERP | WMS | PO 头行、预计到货、越库标识 |
| `ASN.Created` / `ASN.Updated` | 供应商门户 / ERP | WMS | 车次、预计到货、SSCC 清单 |
| `Inbound.Received` | WMS | ERP, OMS, 库存中心 | 收货实收/差异/批次效期 |
| `Inbound.PutawayCompleted` | WMS | 库存中心 | 可用库存新增 |
| `Inventory.Changed` | WMS | 库存中心 → OMS | 增量变更（推荐**增量事件 + 定时全量对齐**） |
| `Inventory.Adjusted` | WMS | ERP | 盘盈亏、报废、状态变更（触发财务调整） |
| `Fulfillment.Created` | OMS | WMS | 出库单（含时效、服务等级、承运偏好） |
| `Outbound.Allocated` | WMS | OMS | 分配结果、缺货短单 |
| `Outbound.Packed` | WMS | TMS | 箱/托、重量体积（触发配载） |
| `Shipment.Ready` | WMS | TMS | 发运需求（仓运边界契约） |
| `Load.Planned` | TMS | WMS, DMS | 车次、月台、装车顺序 |
| `Load.Departed` | WMS/TMS | OMS, DMS | 发车时间、铅封、LPN 清单 |
| `Outbound.Shipped` | WMS | ERP, OMS | 发货过账（触发收入确认/在途库存） |
| `Waybill.TrackUpdated` | TMS | OMS（仅里程碑） | 统一 event_code |
| `Delivery.PODConfirmed` | DMS | TMS, OMS, ERP | 签收人、差异、照片 |
| `Delivery.Exception` | DMS | OMS, 客服 | 拒收/破损/改约 |
| `Return.Initiated` | OMS | WMS | 逆向单 |
| `Return.Received` | WMS | OMS, ERP | 退货实收与质检结论 |
| `Asset.Movement` | DMS | TMS/资产 | 器具借还 |
| `Freight.BillGenerated` | TMS/BMS | ERP | 应付运费 |

---

## 2. 事件信封（统一格式）

```json
{
  "event_id": "01J8X...ULID",
  "event_type": "Outbound.Shipped",
  "event_version": "v2",
  "occurred_at": "2026-07-29T10:22:31.412+08:00",
  "producer": "wms-rdc-sh",
  "tenant_id": "retail-cn",
  "aggregate_type": "outbound_order",
  "aggregate_id": "OB2026072900012345",
  "aggregate_version": 7,
  "idem_key": "wms-rdc-sh:OB2026072900012345:7:Outbound.Shipped",
  "trace_id": "...",
  "payload": { }
}
```

### 三条硬性约束

1. **幂等键** `idem_key = producer:aggregate_id:aggregate_version:event_type`，
   消费端建唯一索引，重复直接丢弃。
2. **单调版本** `aggregate_version` 严格递增，消费端丢弃小于已处理版本的事件（乱序防护）。
3. **事件不可变、可重放**：生产端落 `domain_event` 表（Outbox），
   业务事务与事件写入同一本地事务，异步投递（Transactional Outbox 模式）。

```sql
domain_event (
  event_id, event_type, event_version, aggregate_type, aggregate_id, aggregate_version,
  payload JSON, occurred_at, published_at, publish_status, retry_count, idem_key UNIQUE
)
```

---

## 3. 对账机制（事件之外的兜底）

事件必丢、必乱序、必重复。**只靠事件的库存系统一定会飘。** 必须配三层兜底：

| 层 | 频率 | 内容 |
| --- | --- | --- |
| **增量事件** | 实时 | 秒级同步，保证体验 |
| **增量对账** | 每 5~15 分钟 | 按 `(仓, SKU)` 比对上下游变更量差异，自动补发 |
| **全量快照对齐** | 每日凌晨 | WMS 库存快照 vs 库存中心 vs ERP 财务库存，出差异报表并告警 |

对账断言（见 [02](02-core-data-model.md#4-库存三视图与对账)）：

```
1) Σ inventory_ledger.qty_delta  ==  inventory_stock.on_hand_qty      (仓内自洽)
2) WMS 物理量 == ERP 财务量 + 在途未过账 ± 待处理差异池              (仓财一致)
3) 库存中心可售量 ≤ WMS 可用量                                        (不超卖)
4) Σ load_detail.lpn == Σ shipment 的 LPN 集合                        (装车不漏)
5) Σ pod.delivered - Σ pod_diff == Σ load_detail.unloaded             (签收闭环)
```

---

## 4. 反腐层（ACL）落点

| 边界 | 上游原始概念 | 内部规范概念 | 映射要点 |
| --- | --- | --- | --- |
| ERP → WMS | 采购单行 + 交货计划行 | ASN 行 | 屏蔽 ERP 的税/价/科目字段 |
| WMS → TMS | 出库单 + 包裹 + 托盘 | Shipment | 只暴露地址/时效/体积重量/温层/件数 |
| 承运商 → TMS | 各家轨迹码（几十种） | 统一 `event_code` 字典 | 映射表 + 未识别码兜底为 `EXCEPTION` 并告警 |
| 承运商 → TMS | 各家运单结构 | `waybill` | 计费重口径统一（体积重系数按承运商配置） |
| POS → 库存中心 | 门店销售流水 | `Inventory.Changed` | 门店库存扣减节流（避免每笔 POS 打穿库存中心） |

---

## 5. 多仓/多承运的路由决策（放在哪一层）

| 决策 | 归属 | 输入 |
| --- | --- | --- |
| **寻源**（哪个仓发货） | OMS | 库存可用性、距离/时效、履约成本、仓产能、拆单惩罚 |
| **拆单**（一单拆几个仓） | OMS | 单仓满足率、运费增量、客户体验权重 |
| **承运商选择** | TMS | 服务等级、区域覆盖、时效达成率、单价、承运商配额、黑名单 |
| **线路/车型** | TMS | 门店时间窗、载重容积、装载率、司机工时 |
| **作业模式**（SSTK/XDK） | 补货/计划 | 见 [06 §5.4](06-sstk-xdk.md#5-混合仓的建模建议现实中最常见) |

> 这四类决策**都不属于 WMS**。WMS 只接收决策结果并执行 —— 这是保持 WMS 可复用于多仓型的前提。

---

## 6. 实施顺序建议

1. **先建 `inventory_ledger` 与库存单元键**，其余一切都建立在它之上。
2. **再建容器（LPN）模型**，即使初期只用 `PALLET` 一种类型。
3. 单据层按「入库 → 出库 → 发运」顺序落地，每层严格区分 L2 单据 / L3 流水。
4. TMS 从 `shipment` 契约切入，先做「装车单 + POD」，配载与计费后置。
5. 事件与对账**与第一个业务功能同期上线**，不要留到「以后补」——
   补的时候历史流水已经没法重建了。
