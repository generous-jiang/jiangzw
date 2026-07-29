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

> **货主企业视角的追加结论**：**`shipment` 是必选对象，`load` 与 `waybill` 都是可选对象。**
> 快递发 C 端没有 load（承运商内部行为，企业不可见）；门店自提、供应商直送、
> 自有车队日配没有 waybill。4PL 模型拿 waybill 当主键，照搬会让这些高频场景无处安放。
> 详见 [08 §3](08-shipment-vs-load.md#3-load-的边界)。

---

## 2. `load` 装车单 / 车次

### 2.0 三级结构：为什么必须是三层

| 层 | 表 | 维度 | 回答的问题 |
| --- | --- | --- | --- |
| 车次 | `load` | **资源** | 什么车、谁开、几点发、装载率多少、多少钱 |
| 经停 | `load_stop` | **时空** | 到哪、几点到、时间窗、卸多少、点位异常 |
| 明细 | `load_detail` | **货物** | 哪个 LPN、在第几个 stop 卸、谁什么时候扫的 |

- 没有 `load_stop`：ETA、门店收货时间窗、实际到离时间、点位费、单点异常码全都无处安放 ——
  多点配送场景直接残废。
- `load_detail` 不挂 `stop_seq`：无法做「装车顺序 = 卸货逆序」校验，
  到 A 店卸货时也不知道该卸哪几板。

### 2.1 `load`（头）

| 组 | 字段 | 说明 |
| --- | --- | --- |
| 标识 | `load_no`, `route_id`, `origin_node_id`, `dock_id` | 车次号、固定线路、起运仓与月台 |
| 承运 | `carrier_id`, `carrier_type`, `vehicle_id`, `plate_no`, `vehicle_type` | 自有/外协/平台运力；车型 4.2m/9.6m/冷藏 |
| 司机 | `driver_id`, `driver_name`, `driver_phone` | |
| 时间 | `plan_depart_time`/`actual_depart_time`, `plan_arrive_time`/`actual_arrive_time` | 计划与实际必须双列 |
| 量 | `total_stops`, `total_shipments`, `total_pallets`, `total_cases`, `plan_weight`, `plan_volume` | |
| 效率 | `load_rate_weight`, `load_rate_volume` | 装载率，配载考核核心指标 |
| 合规 | `temp_zone`, `seal_no`, `compartment_config` | 温层、铅封；多温区车需车厢分仓 |
| 计费 | `rate_card_version` | **发车时冻结**，否则历史账算不回来 |
| 状态 | `status` | 见 §2.4 |

### 2.2 `load_stop` 经停点

`load_no`, `stop_seq`, `node_id`(门店/客户/中转场), `stop_type`(**PICKUP** / DELIVERY / CROSS_DOCK),
`plan_eta`, `actual_arrive`, `actual_depart`, `time_window_start/end`,
`pallet_count`, `case_count`, `status`, `exception_code`

> `stop_type` 支持 `PICKUP` 很关键 —— 多仓拼车、供应商循环取货（Milk-run）、
> 中转场接驳都靠它表达，否则得为提货另建一套模型。

### 2.3 `load_detail` 装车明细（按物理件扫码）

`load_no`, `stop_seq`, `shipment_no`, `lpn` / `package_no`, `load_seq`,
`compartment_id`, `scan_time`, `operator_id`, `unloaded_at`, `bump_reason`

- **必须到 LPN 粒度**。只到 shipment 粒度的话，「少了一板」「送错门店」这类日常纠纷
  永远查不清 —— 这是判断一个 TMS 模型能否落地的分水岭。
- `load_seq` 是装车顺序：**逆序装车（LIFO），先送的后装**，与 `stop_seq` 反向。

### 2.4 装车单状态机与落库副作用

```
PLANNING(配载中) → PLANNED(已配载) → DISPATCHED(已派车)
→ ARRIVED_DOCK(到月台) → LOADING(装车中) → LOADED(装车完成)
→ SEALED(施封) → DEPARTED(发车) → IN_TRANSIT
→ [ARRIVED_STOP → UNLOADING → POD_STOP] × N
→ COMPLETED → SETTLED(已结算)
       ↘ CANCELLED / ABORTED(中途异常)
```

| 状态跃迁 | 副作用（必须落库的事实） |
| --- | --- |
| `→ PLANNED` | 占用运力、锁定 shipment、生成 `load_detail` 计划行 |
| `→ DISPATCHED` | 推任务给 DMS / 司机 App |
| `→ LOADING` | 月台占用，开放扫码 |
| `→ LOADED` | 计划行 vs 实扫行差集必须清空，或走甩货流程 |
| `→ SEALED` | 写 `load_seal`；冷链/药品的强制合规节点 |
| `→ DEPARTED` | **写库存流水**（集货位 → `ON_VEHICLE-{load_no}`）；冻结 `rate_card_version`；发 `Load.Departed` 事件 |
| `→ POD_STOP` | 回写 `load_detail.unloaded_at`、生成 `pod` 与 `pod_diff` |
| `→ COMPLETED` | 触发计费；器具回收对账 |
| `→ CANCELLED/ABORTED` | shipment 退回待配载池，不可静默丢弃 |

### 2.5 装车扫码校验规则（模型好坏的试金石）

| # | 校验 | 级别 | 防的事故 |
| --- | --- | --- | --- |
| 1 | LPN 是否在本车 `load_detail` 计划内 | 硬拦截 | 错装他车货 |
| 2 | LPN 的 `dest_node_id` 与当前 `stop.node_id` 是否一致 | 硬拦截 | 送错门店 |
| 3 | `container.status` 是否 `CLOSED`/`STAGED` | 硬拦截 | 未封板装车 |
| 4 | 温层匹配（货 `temp_zone` vs 车厢 `compartment.temp_zone`） | 硬拦截 | 冷链断链 |
| 5 | 累计重量/体积是否超载 | 硬拦截 | 超载法规风险 |
| 6 | `load_seq` 是否违反 LIFO | 软告警 | 卸货翻整车 |
| 7 | 发车前计划 vs 实扫差集 | 硬拦截或转甩货 | 漏装 |

### 2.6 `load_seal` 铅封记录（食品/药品/高值品必备）

`load_no`, `seal_no`, `seal_type`(DEPART/MIDWAY/RESEAL), `compartment_id`, `stop_seq`,
`applied_at`, `applied_by`, `broken_at`, `broken_by`, `photo_urls`

> 一车多门、多点卸货会多次开封重封，**铅封必须是子表不是头字段**，
> 否则中途开封无法追溯，食品药品的合规审计过不了。

### 2.7 变更场景（最容易漏建的部分）

| 场景 | 正确处理 | 错误做法 |
| --- | --- | --- |
| **甩货 / Bump**（计划装但没装上：装不下、货未到集货区） | 写 `load_detail.bump_reason`，对应 shipment 退回待配载池 | **删行**（配载准确率指标直接失真） |
| **追加 / 改配** | `PLANNED` 之后的变更进 `load_change_log`（前后快照 + 原因 + 操作人） | 直接改 detail |
| **换车** | 新建 load 继承 detail，原 load 置 `ABORTED` | 改 `plate_no` |
| **返仓**（未送达货返回） | 走**入库流程**，产生 `RETURN_IN` 流水，从 `ON_VEHICLE` 回实体货位 | 直接改库存数字 |
| **发车后纠错** | 红字冲正 `ship_txn` 或开异常单 | 修改已有 `load_detail` |

### 2.8 与库存的关系

发车不是「改个状态」，是**一次库存移动**：

```
ship_txn  →  inventory_ledger(txn_type = SHIP)
  STAGE-{door}  →  ON_VEHICLE-{load_no}   (虚拟位)
```

有了 `ON_VEHICLE` 虚拟位，「货在车上」才在账内。
**调拨场景下在途库存所有权仍属发货方**，直到收货方 `RECEIPT` 才转移 ——
这一点直接决定调拨差异能不能查清。

### 2.9 三种业务形态下的差异

| | 电商快递揽收 | 大仓 → 门店城配 | 干线整车 FTL |
| --- | --- | --- | --- |
| stop 数 | 1（发到快递网点/分拨） | 5~20 个门店 | 1 |
| detail 粒度 | `package_no` | 托盘 `lpn` | 托盘 `lpn` |
| waybill 数 | 一车几百张 | 1 张（整车） | 1 张 |
| 装载率 | 不关心 | 核心 KPI | 核心 KPI |
| 器具回收 | 无 | **必须**（周转筐/托盘同车带回） | 托盘 |
| 计费 | 按票（在 waybill 上） | 按车 + 点位数 | 按车/按公里 |

### 2.10 常见建模错误

1. **load 与 waybill 合并** —— 多点配送运费算不清，快递场景一车几百单直接撑爆
2. **detail 只到 shipment 不到 LPN** —— 少一板、送错店永远查不清
3. **没有 stop 表**，用 detail 里的 node_id 凑 —— ETA、时间窗、点位费无处安放
4. **装车/发车不写库存流水** —— 货在车上成账外库存
5. **发车后允许改 `load_detail`** —— 审计链断裂
6. **甩货靠删行** —— 配载准确率与承运商考核全部失真
7. **`rate_card` 不冻结版本** —— 三个月后账对不回来

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
