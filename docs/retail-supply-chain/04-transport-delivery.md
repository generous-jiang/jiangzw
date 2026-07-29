# 04 · 运输与配送模型（TMS / DMS）

## 1. 四层聚合关系（最容易搞错的地方）

```
outbound_order (出库单, N)
      ↓  按 目的地 + 时效 + 温层 合并
shipment (发运单, 1)          ← WMS 与 TMS 的边界对象
      ↓  按 车 + 线路 配载
load (装车单 / 车次, 1 车 N 个 stop)
      ↓  按 承运商计费与追踪口径
waybill (运单, 1..N)
      ↓
package / lpn (物理件, N)
```

**不同业务形态下，这四层的基数关系不同 —— 这是模型必须能同时表达的：**

| 场景 | 关系 |
| --- | --- |
| 电商快递 | 1 package = 1 waybill；1 load(揽收车) 含成百上千 waybill |
| 大仓 → 门店城配 | 1 load = 1 waybill（整车/一次行程），载 N 个 shipment，途经 N 个 store stop |
| 干线整车 FTL | 1 load = 1 waybill，1 个 stop |
| 零担 LTL | 1 shipment = 1 waybill，多个 shipment 拼一个 load |
| 越库直发 | shipment 由 XDK 分拣结果生成，不经存储 |

> 结论：**`load` 与 `waybill` 必须是两张表、多对多桥接**，不能合并。
> `load` 是「车的事实」，`waybill` 是「承运合同与计费的事实」。

---

## 2. `load` 装车单 / 车次

**Header**

| 字段 | 说明 |
| --- | --- |
| `load_no` | 车次号 |
| `carrier_id`, `carrier_type` | 承运商；自有/外协/平台运力 |
| `vehicle_id`, `plate_no`, `vehicle_type` | 车型（4.2m/9.6m/冷藏/常温） |
| `driver_id`, `driver_name`, `driver_phone` | |
| `route_id`, `route_name` | 固定线路（门店配送常见） |
| `origin_node_id`, `dock_id` | 起运仓与月台 |
| `plan_depart_time`, `actual_depart_time` | |
| `plan_arrive_time`, `actual_arrive_time` | |
| `total_stops`, `total_shipments`, `total_pallets`, `total_cases` | |
| `plan_weight`, `plan_volume`, `load_rate_weight`, `load_rate_volume` | 装载率 |
| `temp_zone`, `seal_no` | 温层、铅封号（食品/药品必备） |
| `status` | 见状态机 |

**`load_stop` 经停点**

`load_no`, `stop_seq`, `node_id`(门店/客户/中转场), `stop_type`(PICKUP/DELIVERY/CROSS_DOCK),
`plan_eta`, `actual_arrive`, `actual_depart`, `time_window_start/end`,
`shipment_no_list`, `pallet_count`, `case_count`, `status`, `exception_code`

**`load_detail` 装车明细（按物理件扫码）**

`load_no`, `stop_seq`, `shipment_no`, `lpn` 或 `package_no`, `scan_time`, `operator_id`,
`load_seq`(装车顺序 —— 逆序装车，先送的后装), `unloaded_at`

> 装车明细必须到 **LPN 粒度**。这是后续「少了一板」「送错门店」唯一能查清的依据。

### 2.1 装车单状态机

```
PLANNING(配载中) → PLANNED(已配载) → DISPATCHED(已派车)
→ ARRIVED_DOCK(到月台) → LOADING(装车中) → LOADED(装车完成)
→ SEALED(施封) → DEPARTED(发车) → IN_TRANSIT
→ [ARRIVED_STOP → UNLOADING → POD_STOP] × N
→ COMPLETED → SETTLED(已结算)
       ↘ CANCELLED / ABORTED(中途异常)
```

---

## 3. `waybill` 运单

`waybill_no`(承运商单号), `internal_ref`, `carrier_id`, `service_product`(次日达/陆运/冷链),
`load_no`, `shipment_no_list`, `ship_from`, `ship_to`, `consignee_snapshot`(收件人快照,加密),
`package_count`, `gross_weight`, `charged_weight`(计费重 = max(实重, 体积重)), `volume`,
`declared_value`, `cod_amount`(代收货款), `insurance_amount`,
`freight_amount`, `fuel_surcharge`, `extra_charges`(装卸/上楼/等待/返仓),
`pickup_time`, `estimated_delivery`, `actual_delivery`, `status`, `pod_id`

### 3.1 `waybill_package` 运单包裹明细

`waybill_no`, `package_no`/`lpn`, `weight`, `dim`, `sub_tracking_no`(子母件)

### 3.2 `tracking_event` 轨迹（append-only）

`event_id`, `waybill_no`, `load_no`, `event_code`, `event_desc`, `occurred_at`, `received_at`,
`node_id`, `geo_lat/lng`, `operator`, `source`(CARRIER_API/DRIVER_APP/GPS/MANUAL), `raw_payload`

**建议统一 event_code 字典**（各承运商码值必须在 ACL 层映射到内部码）：

`ORDER_ACCEPTED / PICKED_UP / DEPARTED / ARRIVED_HUB / IN_TRANSIT / OUT_FOR_DELIVERY /
DELIVERED / SIGNED / REJECTED / DAMAGED / LOST / RETURNING / RETURNED / EXCEPTION`

> 轨迹表是全系统最大的表之一。做好：分区（按天）、冷热分离、只把**里程碑**投影给 OMS。

---

## 4. `pod` 签收回单

`pod_id`, `waybill_no`/`load_no`, `stop_seq`, `shipment_no`, `node_id`,
`sign_time`, `signer_name`, `signer_relation`, `sign_type`(本人/代收/自提柜/无接触),
`signature_img`, `photo_urls`, `geo_lat/lng`, `geo_deviation`(与门店坐标偏差, 防虚假签收),
`delivered_pallets/cases`, `diff_flag`, `pod_no`(纸质回单号), `upload_by`, `status`

**`pod_diff` 签收差异明细**（对账扣款依据）

`pod_id`, `sku_id`/`lpn`, `expect_qty`, `actual_qty`, `diff_type`(SHORT/OVER/DAMAGE/WRONG_ITEM/REJECT),
`reason_code`, `liable_party`(仓/承运/门店/供应商), `photo_urls`, `claim_amount`, `settle_status`

---

## 5. DMS 末端配送模型

| 表 | 关键字段 |
| --- | --- |
| `delivery_route` | `route_id`, `route_code`, `warehouse_id`, `store_list`, `frequency`(日配/隔日/周配), `time_windows`, `standard_mileage`, `standard_duration` |
| `delivery_task` | `task_id`, `load_no`, `stop_seq`, `driver_id`, `node_id`, `plan_arrive`, `actual_arrive`, `task_status`, `handover_no` |
| `handover`（交接单） | `handover_no`, `from_party`, `to_party`, `scan_lpn_list`, `expect_count`, `actual_count`, `handover_time`, `signature` |
| `delivery_exception` | `exc_id`, `task_id`, `exc_type`(拒收/改约/无人/地址错/破损/超时), `reason_code`, `photo`, `resolution`, `resolved_at` |
| `driver` / `vehicle` | 资质、准驾、温控设备、保险有效期、载重容积 |
| `driver_position` | 高频 GPS 点位（独立时序库，不入业务库） |

### 5.1 器具/周转资产账 `asset_ledger`（门店配送必备）

周转箱、塑料托盘、笼车、保温箱是**有价资产**，且大部分时间在仓外。必须单独记账：

`asset_txn_id`, `asset_type`(TOTE/PALLET/CAGE/COLD_BOX), `asset_no`(可为 RFID/条码),
`txn_type`(ISSUE 借出 / RETURN 归还 / TRANSFER / LOST / SCRAP),
`from_party`, `to_party`(仓/门店/承运商/司机), `qty`, `ref_doc_no`(load_no/handover_no),
`occurred_at`, `operator`

> 派生出「各门店在册器具余额表」，配送时同车带回，差额按协议扣款。
> 不建这个账的项目，一年内托盘丢失率通常在 15%~30%。

---

## 6. 计费模型（BMS）要点

`rate_card`(报价单): `carrier_id`, `route_pattern`(起止区域), `vehicle_type`, `charge_mode`
(按车 / 按公斤 / 按方 / 按件 / 按托 / 按公里 / 按点位), `tier_rules`(阶梯), `min_charge`,
`valid_from/to`

`freight_bill`: `bill_no`, `carrier_id`, `period`, `load_no_list`, `base_amount`,
`accessorial`(等待费/上楼费/返仓费/装卸费), `deduction`(POD 差异扣款/超时扣款),
`payable_amount`, `recon_status`(对账状态), `invoice_no`

> 计费必须**在发车时冻结 rate_card 快照版本**写入 load，否则历史账永远算不回来。
