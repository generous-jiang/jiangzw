-- =============================================================================
-- 零售供应链物流 · 核心数据模型参考 DDL
-- 方言: MySQL 8.0 (PostgreSQL 可直接替换 JSON/DATETIME/AUTO_INCREMENT 语法)
-- 说明: 仅含核心字段与关键索引; 审计字段 (created_by/created_at/updated_by/updated_at)
--       与租户字段 (tenant_id) 假定由基础框架统一注入, 此处省略以突出模型本身。
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. 共享内核: 商品 / 单位 / 节点 / 货位
-- -----------------------------------------------------------------------------

CREATE TABLE item (
  sku_id          VARCHAR(32)  NOT NULL,
  sku_code        VARCHAR(64)  NOT NULL,
  gtin            VARCHAR(14),
  name            VARCHAR(256) NOT NULL,
  category_id     VARCHAR(32),
  brand_id        VARCHAR(32),
  temp_zone       VARCHAR(16)  NOT NULL DEFAULT 'AMBIENT',  -- AMBIENT/CHILLED/FROZEN
  is_batch_ctrl   TINYINT(1)   NOT NULL DEFAULT 0,
  is_serial_ctrl  TINYINT(1)   NOT NULL DEFAULT 0,
  shelf_life_days INT,
  hazard_class    VARCHAR(16),
  status          VARCHAR(16)  NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (sku_id),
  UNIQUE KEY uk_item_code (sku_code),
  KEY idx_item_gtin (gtin)
);

CREATE TABLE item_uom (
  sku_id       VARCHAR(32)    NOT NULL,
  uom          VARCHAR(8)     NOT NULL,   -- EA / INR / CS / PL
  base_qty     DECIMAL(18,4)  NOT NULL,   -- 折算到基本单位的数量
  gtin         VARCHAR(14),
  length_mm    INT, width_mm INT, height_mm INT,
  gross_weight_g BIGINT,
  volume_cm3   BIGINT,
  is_base      TINYINT(1)     NOT NULL DEFAULT 0,
  is_order_uom TINYINT(1)     NOT NULL DEFAULT 0,
  PRIMARY KEY (sku_id, uom)
);

CREATE TABLE node (
  node_id        VARCHAR(32) NOT NULL,
  node_type      VARCHAR(16) NOT NULL,  -- WAREHOUSE/STORE/SUPPLIER/CUSTOMER/HUB
  code           VARCHAR(64) NOT NULL,
  name           VARCHAR(256),
  parent_node_id VARCHAR(32),
  region_code    VARCHAR(32),
  address        VARCHAR(512),
  geo_lat        DECIMAL(10,7),
  geo_lng        DECIMAL(10,7),
  contact_name   VARCHAR(64),
  contact_phone  VARCHAR(64),
  time_window    JSON,                  -- [{"dow":1,"start":"08:00","end":"11:00"}]
  unload_capability VARCHAR(64),        -- DOCK/TAILGATE/MANUAL
  temp_zone_support VARCHAR(64),
  status         VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (node_id),
  UNIQUE KEY uk_node_code (node_type, code)
);

CREATE TABLE location (
  location_id     VARCHAR(40) NOT NULL,
  warehouse_id    VARCHAR(32) NOT NULL,
  zone_id         VARCHAR(32),
  code            VARCHAR(64) NOT NULL,
  loc_type        VARCHAR(24) NOT NULL,  -- RECEIVE/STORAGE/PICK/STAGE/DOCK/XDOCK_LANE/QC/DAMAGE/VIRTUAL
  operation_mode  VARCHAR(16),           -- SSTK/XDK/ANY  (物理隔离越库区与存储区)
  x_pos INT, y_pos INT, z_pos INT,
  pick_seq        INT,
  capacity_volume BIGINT,
  capacity_weight BIGINT,
  allow_mix_sku   TINYINT(1) NOT NULL DEFAULT 1,
  allow_mix_lot   TINYINT(1) NOT NULL DEFAULT 1,
  temp_zone       VARCHAR(16),
  status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (location_id),
  UNIQUE KEY uk_loc (warehouse_id, code),
  KEY idx_loc_zone (warehouse_id, zone_id, pick_seq)
);

-- -----------------------------------------------------------------------------
-- 2. 库存: 快照 + 流水账本
-- -----------------------------------------------------------------------------

CREATE TABLE inventory_stock (
  stock_id       BIGINT        NOT NULL AUTO_INCREMENT,
  warehouse_id   VARCHAR(32)   NOT NULL,
  location_id    VARCHAR(40)   NOT NULL,
  sku_id         VARCHAR(32)   NOT NULL,
  lot_no         VARCHAR(64)   NOT NULL DEFAULT '*',   -- 用 '*' 而非 NULL, 保证唯一索引生效
  inv_status     VARCHAR(16)   NOT NULL DEFAULT 'AVAILABLE',
  owner_id       VARCHAR(32)   NOT NULL,
  lpn            VARCHAR(64)   NOT NULL DEFAULT '*',
  serial_no      VARCHAR(64)   NOT NULL DEFAULT '*',
  on_hand_qty    DECIMAL(18,4) NOT NULL DEFAULT 0,
  allocated_qty  DECIMAL(18,4) NOT NULL DEFAULT 0,
  picked_qty     DECIMAL(18,4) NOT NULL DEFAULT 0,
  hold_qty       DECIMAL(18,4) NOT NULL DEFAULT 0,
  in_transit_qty DECIMAL(18,4) NOT NULL DEFAULT 0,
  uom            VARCHAR(8)    NOT NULL,
  expire_date    DATE,
  last_count_at  DATETIME,
  version        BIGINT        NOT NULL DEFAULT 0,
  PRIMARY KEY (stock_id),
  UNIQUE KEY uk_stock_unit (warehouse_id, location_id, sku_id, lot_no, inv_status, owner_id, lpn, serial_no),
  KEY idx_stock_sku (warehouse_id, sku_id, inv_status),
  KEY idx_stock_lpn (lpn),
  KEY idx_stock_fefo (warehouse_id, sku_id, expire_date)
);

-- 唯一真相源: 只追加, 永不 UPDATE / DELETE
CREATE TABLE inventory_ledger (
  ledger_id        BIGINT        NOT NULL AUTO_INCREMENT,
  txn_type         VARCHAR(32)   NOT NULL,
  txn_time         DATETIME(3)   NOT NULL,
  posted_time      DATETIME(3)   NOT NULL,
  ref_doc_type     VARCHAR(32),
  ref_doc_no       VARCHAR(64),
  ref_line_no      INT,
  warehouse_id     VARCHAR(32)   NOT NULL,
  sku_id           VARCHAR(32)   NOT NULL,
  lot_no           VARCHAR(64)   NOT NULL DEFAULT '*',
  owner_id         VARCHAR(32)   NOT NULL,
  serial_no        VARCHAR(64)   NOT NULL DEFAULT '*',
  from_location_id VARCHAR(40),
  to_location_id   VARCHAR(40),
  from_status      VARCHAR(16),
  to_status        VARCHAR(16),
  from_lpn         VARCHAR(64),
  to_lpn           VARCHAR(64),
  qty_delta        DECIMAL(18,4) NOT NULL,   -- 带符号
  uom              VARCHAR(8)    NOT NULL,
  base_qty_delta   DECIMAL(18,4) NOT NULL,
  operator_id      VARCHAR(32),
  device_id        VARCHAR(64),
  reversal_of      BIGINT,                   -- 红字冲正指向原流水
  cost_ref         VARCHAR(64),
  idem_key         VARCHAR(160) NOT NULL,
  PRIMARY KEY (ledger_id),
  UNIQUE KEY uk_ledger_idem (idem_key),
  KEY idx_ledger_unit (warehouse_id, sku_id, lot_no, owner_id, txn_time),
  KEY idx_ledger_doc (ref_doc_type, ref_doc_no),
  KEY idx_ledger_time (posted_time)
);

-- -----------------------------------------------------------------------------
-- 3. 入库域
-- -----------------------------------------------------------------------------

CREATE TABLE asn (
  asn_no           VARCHAR(64) NOT NULL,
  warehouse_id     VARCHAR(32) NOT NULL,
  source_type      VARCHAR(16) NOT NULL,  -- PO/TRANSFER/RETURN/PRODUCTION
  source_doc_no    VARCHAR(64),
  supplier_id      VARCHAR(32),
  carrier_id       VARCHAR(32),
  plate_no         VARCHAR(32),
  transport_ref    VARCHAR(64),   -- 上游 load_no; 由 Load.Departed 事件写入, 引用标记非外键
  expected_arrive  DATETIME,
  appointment_no   VARCHAR(64),
  dock_id          VARCHAR(32),
  total_qty        DECIMAL(18,4),
  total_cases      INT,
  total_pallets    INT,
  temp_zone        VARCHAR(16),
  is_pre_labeled   TINYINT(1) NOT NULL DEFAULT 0,   -- 供应商是否预贴 SSCC
  xdock_flag       TINYINT(1) NOT NULL DEFAULT 0,
  status           VARCHAR(24) NOT NULL,
  PRIMARY KEY (asn_no),
  KEY idx_asn_wh_time (warehouse_id, expected_arrive)
);

CREATE TABLE asn_line (
  asn_no          VARCHAR(64) NOT NULL,
  line_no         INT         NOT NULL,
  sku_id          VARCHAR(32) NOT NULL,
  expected_qty    DECIMAL(18,4) NOT NULL,
  uom             VARCHAR(8)  NOT NULL,
  base_qty        DECIMAL(18,4) NOT NULL,   -- 创建时冻结的换算快照
  lot_no          VARCHAR(64),
  production_date DATE,
  expire_date     DATE,
  operation_mode  VARCHAR(16) NOT NULL DEFAULT 'SSTK',  -- SSTK/XDK/PBYL, 打在行上
  dest_node_id    VARCHAR(32),                          -- XDK 预分配到门店
  pegging_ref     VARCHAR(64),                          -- XDK 一单到底: 下游门店入库单行 ID
  po_line_ref     VARCHAR(64),
  PRIMARY KEY (asn_no, line_no),
  KEY idx_asnline_sku (sku_id),
  KEY idx_asnline_dest (dest_node_id),
  KEY idx_asnline_pegging (pegging_ref)
);

-- 入库单 = 承诺层(应收), 下单时生成, 数量来自调拨量 —— 不是发货事实的镜像
-- 调拨配对锚点是 transfer_no (1:1), 不是 shipment_no:
--   一张入库单可对多个发运凭证(分多车/多天到货), 一个发运凭证也可含多张调拨单的货
--   -> 头层面 M:N, 不做头配对; 关联走 shipment_line.pegging_ref -> inbound_line.line_id
CREATE TABLE inbound_order (
  inbound_no    VARCHAR(64) NOT NULL,
  asn_no        VARCHAR(64),
  transfer_no   VARCHAR(64),           -- 调拨入库的 1:1 锚点
  warehouse_id  VARCHAR(32) NOT NULL,
  inbound_type  VARCHAR(16) NOT NULL,  -- PURCHASE/TRANSFER/RETURN/PRODUCTION/XDOCK
  owner_id      VARCHAR(32) NOT NULL,
  from_node_id  VARCHAR(32),           -- 调拨来源节点(DC)
  dock_id       VARCHAR(32),
  expected_arrive_date DATE,           -- 来自调拨单, 供门店预约排班
  arrive_time   DATETIME,
  start_time    DATETIME,
  finish_time   DATETIME,
  qc_required   TINYINT(1) NOT NULL DEFAULT 0,
  close_status  VARCHAR(16) NOT NULL DEFAULT 'OPEN', -- OPEN/PARTIAL_CLOSED/CLOSED
  status        VARCHAR(24) NOT NULL,
  PRIMARY KEY (inbound_no),
  KEY idx_ib_wh_status (warehouse_id, status),
  KEY idx_ib_transfer (transfer_no),
  KEY idx_ib_open (warehouse_id, close_status, expected_arrive_date)
);

CREATE TABLE inbound_line (
  inbound_no    VARCHAR(64) NOT NULL,
  line_no       INT NOT NULL,
  line_id       VARCHAR(64) NOT NULL,   -- 全局唯一行 ID: 供上游 pegging 引用
                                        -- XDK 编入容器标签 GS1 AI(403); SSTK 由 WHC 写进 shipment_line.pegging_ref
  asn_line_no   INT,
  sku_id        VARCHAR(32) NOT NULL,
  plan_qty      DECIMAL(18,4) NOT NULL, -- = 应收(调拨量), 不是实发量
  open_qty      DECIMAL(18,4) NOT NULL DEFAULT 0,  -- 未收量; 关单时释放
  received_qty  DECIMAL(18,4) NOT NULL DEFAULT 0,
  qualified_qty DECIMAL(18,4) NOT NULL DEFAULT 0,
  rejected_qty  DECIMAL(18,4) NOT NULL DEFAULT 0,
  damaged_qty   DECIMAL(18,4) NOT NULL DEFAULT 0,
  putaway_qty   DECIMAL(18,4) NOT NULL DEFAULT 0,
  lot_no        VARCHAR(64),
  expire_date   DATE,
  uom           VARCHAR(8) NOT NULL,
  base_qty      DECIMAL(18,4) NOT NULL,
  operation_mode VARCHAR(16) NOT NULL DEFAULT 'SSTK',
  -- 行级 pegging: XDK 行须一单到底; SSTK 行按「商品+批次」重建匹配, pegging_ref 为空
  source_mode   VARCHAR(8) NOT NULL DEFAULT 'SSTK',   -- SSTK/XDK
  inv_status    VARCHAR(16) NOT NULL DEFAULT 'AVAILABLE',
  PRIMARY KEY (inbound_no, line_no),
  UNIQUE KEY uk_ibline_id (line_id)
);

-- 调拨主单 (PFC): 出库单与入库单的共同父级, 配对在这里 1:1 完成
-- 关键: 出库单与入库单是同一张调拨单的两侧投影, 两者之间不做直接配对
CREATE TABLE transfer_order (
  transfer_no          VARCHAR(64) NOT NULL,
  from_node_id         VARCHAR(32) NOT NULL,
  to_node_id           VARCHAR(32) NOT NULL,
  owner_id             VARCHAR(32) NOT NULL,
  required_arrive_date DATE,
  close_status         VARCHAR(16) NOT NULL DEFAULT 'OPEN',
  status               VARCHAR(24) NOT NULL,
  PRIMARY KEY (transfer_no),
  KEY idx_to_route (from_node_id, to_node_id, required_arrive_date)
);

CREATE TABLE transfer_line (
  transfer_no    VARCHAR(64) NOT NULL,
  line_no        INT NOT NULL,
  sku_id         VARCHAR(32) NOT NULL,
  qty            DECIMAL(18,4) NOT NULL,   -- 应收
  uom            VARCHAR(8) NOT NULL,
  base_qty       DECIMAL(18,4) NOT NULL,
  operation_mode VARCHAR(16) NOT NULL DEFAULT 'SSTK',
  shipped_qty    DECIMAL(18,4) NOT NULL DEFAULT 0,  -- 实发; 满足率 = shipped/qty
  received_qty   DECIMAL(18,4) NOT NULL DEFAULT 0,  -- 实收; 损耗率 = received/shipped
  PRIMARY KEY (transfer_no, line_no),
  KEY idx_tl_sku (sku_id)
);

-- 收货流水: 一次扫码一条, append-only
CREATE TABLE receipt_txn (
  receipt_id      BIGINT NOT NULL AUTO_INCREMENT,
  inbound_no      VARCHAR(64) NOT NULL,
  inbound_line_no INT NOT NULL,
  sku_id          VARCHAR(32) NOT NULL,
  qty             DECIMAL(18,4) NOT NULL,
  uom             VARCHAR(8) NOT NULL,
  base_qty        DECIMAL(18,4) NOT NULL,
  lot_no          VARCHAR(64),
  production_date DATE,
  expire_date     DATE,
  lpn             VARCHAR(64),
  to_location_id  VARCHAR(40),
  inv_status      VARCHAR(16) NOT NULL,
  operator_id     VARCHAR(32),
  device_id       VARCHAR(64),
  received_at     DATETIME(3) NOT NULL,
  reversal_of     BIGINT,
  idem_key        VARCHAR(160) NOT NULL,
  PRIMARY KEY (receipt_id),
  UNIQUE KEY uk_receipt_idem (idem_key),
  KEY idx_receipt_doc (inbound_no, inbound_line_no)
);

CREATE TABLE putaway_task (
  task_id      BIGINT NOT NULL AUTO_INCREMENT,
  inbound_no   VARCHAR(64) NOT NULL,
  lpn          VARCHAR(64),
  sku_id       VARCHAR(32) NOT NULL,
  lot_no       VARCHAR(64),
  qty          DECIMAL(18,4) NOT NULL,
  uom          VARCHAR(8) NOT NULL,
  from_location_id VARCHAR(40) NOT NULL,
  to_location_id   VARCHAR(40),
  suggested_location_id VARCHAR(40),
  operator_id  VARCHAR(32),
  status       VARCHAR(16) NOT NULL,
  PRIMARY KEY (task_id),
  KEY idx_putaway_doc (inbound_no, status)
);

-- -----------------------------------------------------------------------------
-- 4. 出库域
-- -----------------------------------------------------------------------------

CREATE TABLE outbound_order (
  outbound_no       VARCHAR(64) NOT NULL,
  warehouse_id      VARCHAR(32) NOT NULL,
  outbound_type     VARCHAR(24) NOT NULL,  -- B2C_SALE/STORE_REPLEN/TRANSFER_OUT/RETURN_TO_VENDOR/XDOCK/SCRAP
  source_type       VARCHAR(16),
  source_doc_no     VARCHAR(64),           -- OMS 履约单号
  owner_id          VARCHAR(32) NOT NULL,
  ship_to_node_id   VARCHAR(32) NOT NULL,
  consignee_enc     VARBINARY(1024),       -- B2C 收件人加密存储
  required_ship_time    DATETIME,
  promised_delivery_time DATETIME,
  service_level     VARCHAR(24),
  carrier_pref      VARCHAR(32),
  temp_zone         VARCHAR(16),
  priority          INT NOT NULL DEFAULT 100,
  wave_no           VARCHAR(64),
  shipment_no       VARCHAR(64),
  status            VARCHAR(24) NOT NULL,
  PRIMARY KEY (outbound_no),
  KEY idx_ob_wh_status (warehouse_id, status, priority),
  KEY idx_ob_wave (wave_no),
  KEY idx_ob_shipment (shipment_no),
  KEY idx_ob_src (source_type, source_doc_no)
);

CREATE TABLE outbound_line (
  outbound_no   VARCHAR(64) NOT NULL,
  line_no       INT NOT NULL,
  sku_id        VARCHAR(32) NOT NULL,
  order_qty     DECIMAL(18,4) NOT NULL,
  allocated_qty DECIMAL(18,4) NOT NULL DEFAULT 0,
  picked_qty    DECIMAL(18,4) NOT NULL DEFAULT 0,
  shipped_qty   DECIMAL(18,4) NOT NULL DEFAULT 0,
  short_qty     DECIMAL(18,4) NOT NULL DEFAULT 0,
  uom           VARCHAR(8) NOT NULL,
  base_qty      DECIMAL(18,4) NOT NULL,
  lot_strategy  VARCHAR(16) NOT NULL DEFAULT 'FEFO',
  operation_mode VARCHAR(16) NOT NULL DEFAULT 'SSTK',  -- 混发的前提: mode 打在行上
  pegging_ref   VARCHAR(64),            -- XDK 一单到底: 下游门店入库单行 ID
  source_line_ref VARCHAR(64),
  PRIMARY KEY (outbound_no, line_no),
  KEY idx_obline_sku (sku_id),
  KEY idx_obline_pegging (pegging_ref)
);

CREATE TABLE allocation (
  alloc_id     BIGINT NOT NULL AUTO_INCREMENT,
  outbound_no  VARCHAR(64) NOT NULL,
  line_no      INT NOT NULL,
  sku_id       VARCHAR(32) NOT NULL,
  warehouse_id VARCHAR(32) NOT NULL,
  location_id  VARCHAR(40),               -- SOFT 分配时可空
  lot_no       VARCHAR(64) NOT NULL DEFAULT '*',
  inv_status   VARCHAR(16) NOT NULL DEFAULT 'AVAILABLE',
  owner_id     VARCHAR(32) NOT NULL,
  lpn          VARCHAR(64) NOT NULL DEFAULT '*',
  alloc_qty    DECIMAL(18,4) NOT NULL,
  picked_qty   DECIMAL(18,4) NOT NULL DEFAULT 0,
  alloc_type   VARCHAR(8) NOT NULL,       -- SOFT/HARD
  alloc_time   DATETIME(3) NOT NULL,
  status       VARCHAR(16) NOT NULL,
  PRIMARY KEY (alloc_id),
  KEY idx_alloc_doc (outbound_no, line_no),
  KEY idx_alloc_stock (warehouse_id, sku_id, location_id, lot_no)
);

CREATE TABLE wave (
  wave_no      VARCHAR(64) NOT NULL,
  warehouse_id VARCHAR(32) NOT NULL,
  wave_type    VARCHAR(24) NOT NULL,   -- SINGLE/BATCH/SORT_WHILE_PICK/PUT_TO_LIGHT/CASE/PIECE
  strategy_id  VARCHAR(32),
  order_count  INT, line_count INT,
  cutoff_time  DATETIME,
  carrier_cutoff DATETIME,
  status       VARCHAR(16) NOT NULL,
  PRIMARY KEY (wave_no),
  KEY idx_wave_wh (warehouse_id, status)
);

CREATE TABLE pick_task (
  task_id          BIGINT NOT NULL AUTO_INCREMENT,
  wave_no          VARCHAR(64),
  outbound_no      VARCHAR(64) NOT NULL,
  line_no          INT NOT NULL,
  sku_id           VARCHAR(32) NOT NULL,
  from_location_id VARCHAR(40) NOT NULL,
  lot_no           VARCHAR(64),
  plan_qty         DECIMAL(18,4) NOT NULL,
  picked_qty       DECIMAL(18,4) NOT NULL DEFAULT 0,
  uom              VARCHAR(8) NOT NULL,
  to_lpn           VARCHAR(64),
  pick_seq         INT,
  task_type        VARCHAR(16) NOT NULL,   -- PALLET_PICK/CASE_PICK/PIECE_PICK/REPLEN
  picker_id        VARCHAR(32),
  status           VARCHAR(16) NOT NULL,
  PRIMARY KEY (task_id),
  KEY idx_pick_wave (wave_no, status, pick_seq),
  KEY idx_pick_doc (outbound_no, line_no)
);

CREATE TABLE pick_txn (
  pick_txn_id      BIGINT NOT NULL AUTO_INCREMENT,
  task_id          BIGINT NOT NULL,
  outbound_no      VARCHAR(64) NOT NULL,
  line_no          INT NOT NULL,
  sku_id           VARCHAR(32) NOT NULL,
  lot_no           VARCHAR(64),
  from_location_id VARCHAR(40) NOT NULL,
  to_lpn           VARCHAR(64),
  qty              DECIMAL(18,4) NOT NULL,
  uom              VARCHAR(8) NOT NULL,
  base_qty         DECIMAL(18,4) NOT NULL,
  short_reason     VARCHAR(32),
  operator_id      VARCHAR(32),
  picked_at        DATETIME(3) NOT NULL,
  reversal_of      BIGINT,
  idem_key         VARCHAR(160) NOT NULL,
  PRIMARY KEY (pick_txn_id),
  UNIQUE KEY uk_pick_idem (idem_key),
  KEY idx_picktxn_task (task_id)
);

CREATE TABLE package (
  package_no   VARCHAR(64) NOT NULL,
  outbound_no  VARCHAR(64) NOT NULL,
  shipment_no  VARCHAR(64),
  waybill_no   VARCHAR(64),
  box_spec     VARCHAR(32),
  weight_g     BIGINT,
  dim_l_mm INT, dim_w_mm INT, dim_h_mm INT,
  packer_id    VARCHAR(32),
  packed_at    DATETIME(3),
  status       VARCHAR(16) NOT NULL,
  PRIMARY KEY (package_no),
  KEY idx_pkg_ob (outbound_no),
  KEY idx_pkg_wb (waybill_no)
);

-- shipment = 一批货的一次位移承诺 (需求侧/货的视角)
-- 货主企业视角: shipment 是必选对象; load 与 waybill 均可为空
-- (快递发C端无 load; 自提/直送/自有车队无 waybill)
CREATE TABLE shipment (
  shipment_no        VARCHAR(64) NOT NULL,
  warehouse_id       VARCHAR(32) NOT NULL,
  ship_from_node_id  VARCHAR(32) NOT NULL,
  ship_to_node_id    VARCHAR(32) NOT NULL,
  -- 货权与在途库存 (企业视角核心, 4PL 模型没有)
  owner_id             VARCHAR(32) NOT NULL,
  title_transfer_point VARCHAR(16) NOT NULL DEFAULT 'RECEIPT', -- SHIP/RECEIPT/POD
  inventory_bucket     VARCHAR(24) NOT NULL DEFAULT 'FROM_NODE', -- FROM_NODE/TO_NODE/IN_TRANSIT_POOL
  -- 计划态 vs 实际态
  plan_source        VARCHAR(16) NOT NULL DEFAULT 'ESTIMATED',  -- ESTIMATED/ACTUAL
  est_weight_g       BIGINT, est_volume_cm3 BIGINT,
  total_packages     INT, total_cases INT, total_pallets INT,
  gross_weight_g     BIGINT, volume_cm3 BIGINT,
  temp_zone          VARCHAR(16),
  required_pickup_time   DATETIME,
  promised_delivery_time DATETIME,
  service_level      VARCHAR(24),
  carrier_id         VARCHAR(32),          -- 可空: load 阶段才决定, 不提前绑定
  waybill_no         VARCHAR(64),          -- 冗余便捷字段; 权威关系见 waybill_shipment
  load_no            VARCHAR(64),          -- 「先装车后过账」下 shipment 不跨车, 此处为合法单值
  stop_seq           INT,
  is_reverse         TINYINT(1) NOT NULL DEFAULT 0,  -- 正向/逆向不同票
  -- ERP 过账 (shipment = 一批出库单的发货流水, 是记账凭证)
  -- 过账由 Load.Departed 触发; shipment_line 按实装容器反算而非抄 outbound_line
  posting_status     VARCHAR(16) NOT NULL DEFAULT 'PENDING', -- PENDING/POSTING/POSTED/FAILED
  posted_at          DATETIME(3),
  posting_date       DATE,                 -- 账期归属: 按仓库作业日(有cutoff), 不按自然时间
  erp_doc_no         VARCHAR(64),          -- ERP 凭证号
  posting_batch      VARCHAR(64),
  posting_error      VARCHAR(512),
  reversal_of        VARCHAR(64),          -- 红字冲销指向原 shipment_no
  special_req        JSON,
  status             VARCHAR(24) NOT NULL,
  PRIMARY KEY (shipment_no),
  KEY idx_shp_load (load_no),
  KEY idx_shp_wh_status (warehouse_id, status),
  KEY idx_shp_owner (owner_id, inventory_bucket, status),
  KEY idx_shp_route (ship_from_node_id, ship_to_node_id, required_pickup_time),
  KEY idx_shp_posting (posting_status, posted_at)
);

-- 发货凭证明细: ERP 过账载体 (SKU x 批次 x 数量 x 货主 x 成本参照)
-- POSTED 之后不可变, 纠错走 reversal
CREATE TABLE shipment_line (
  shipment_no      VARCHAR(64) NOT NULL,
  line_no          INT NOT NULL,
  -- 来源: SSTK 行来自出库单, XDK 行来自越库 ASN -> 用通用引用而非写死 outbound
  ref_doc_type     VARCHAR(16) NOT NULL,   -- OUTBOUND/ASN
  ref_doc_no       VARCHAR(64) NOT NULL,
  ref_line_no      INT NOT NULL,
  sku_id           VARCHAR(32) NOT NULL,
  lot_no           VARCHAR(64) NOT NULL DEFAULT '*',
  qty              DECIMAL(18,4) NOT NULL,
  uom              VARCHAR(8) NOT NULL,
  base_qty         DECIMAL(18,4) NOT NULL,
  owner_id         VARCHAR(32) NOT NULL,
  inv_status       VARCHAR(16) NOT NULL,
  -- 行级 pegging: 报文结构统一, 语义按 source_mode 分支
  source_mode      VARCHAR(8) NOT NULL DEFAULT 'SSTK',  -- SSTK/XDK
  pegging_type     VARCHAR(16) NOT NULL DEFAULT 'NONE', -- NONE/INBOUND_LINE
  pegging_ref      VARCHAR(64),            -- XDK 必填: 下游入库单行 ID
  cost_ref         VARCHAR(64),
  PRIMARY KEY (shipment_no, line_no),
  KEY idx_shpline_ref (ref_doc_type, ref_doc_no, ref_line_no),
  KEY idx_shpline_sku (sku_id, lot_no),
  KEY idx_shpline_pegging (pegging_ref)
);

-- 运输段: 仅用于「中转点不是企业库存节点」的情况 (承运商分拨场/快递网点)
-- 中转点若是自有 RDC, 应拆成两个 shipment, 中间一次入库或越库
CREATE TABLE shipment_leg (
  shipment_no   VARCHAR(64) NOT NULL,
  leg_seq       INT NOT NULL,
  leg_type      VARCHAR(16) NOT NULL,  -- PICKUP/LINEHAUL/TRANSFER/DELIVERY
  from_node_id  VARCHAR(32) NOT NULL,
  to_node_id    VARCHAR(32) NOT NULL,
  carrier_id    VARCHAR(32),
  load_no       VARCHAR(64),
  waybill_no    VARCHAR(64),
  plan_depart   DATETIME, plan_arrive  DATETIME,
  actual_depart DATETIME, actual_arrive DATETIME,
  status        VARCHAR(24) NOT NULL,
  PRIMARY KEY (shipment_no, leg_seq),
  KEY idx_leg_load (load_no)
);

-- 发货流水: 按 LPN / package 逐件扫码, append-only
CREATE TABLE ship_txn (
  ship_txn_id      BIGINT NOT NULL AUTO_INCREMENT,
  shipment_no      VARCHAR(64) NOT NULL,
  load_no          VARCHAR(64),
  lpn              VARCHAR(64),
  package_no       VARCHAR(64),
  outbound_no      VARCHAR(64) NOT NULL,
  line_no          INT NOT NULL,
  sku_id           VARCHAR(32) NOT NULL,
  lot_no           VARCHAR(64),
  qty              DECIMAL(18,4) NOT NULL,
  uom              VARCHAR(8) NOT NULL,
  base_qty         DECIMAL(18,4) NOT NULL,
  from_location_id VARCHAR(40),
  to_location_id   VARCHAR(40),   -- 虚拟位 ON_VEHICLE-{load_no} / IN_TRANSIT
  operator_id      VARCHAR(32),
  shipped_at       DATETIME(3) NOT NULL,
  reversal_of      BIGINT,
  idem_key         VARCHAR(160) NOT NULL,
  PRIMARY KEY (ship_txn_id),
  UNIQUE KEY uk_ship_idem (idem_key),
  KEY idx_shiptxn_shp (shipment_no),
  KEY idx_shiptxn_lpn (lpn)
);

-- -----------------------------------------------------------------------------
-- 5. 容器 (LPN)
-- -----------------------------------------------------------------------------

CREATE TABLE container (
  lpn              VARCHAR(64) NOT NULL,
  lpn_type         VARCHAR(16) NOT NULL DEFAULT 'INTERNAL',  -- SSCC/INTERNAL
  container_type   VARCHAR(16) NOT NULL,  -- PALLET/CASE/TOTE/CAGE/ROLL_CAGE/COLD_BOX
  parent_lpn       VARCHAR(64),
  root_lpn         VARCHAR(64),
  nest_level       INT NOT NULL DEFAULT 0,
  warehouse_id     VARCHAR(32),
  current_location_id VARCHAR(40),
  status           VARCHAR(16) NOT NULL,  -- EMPTY/BUILDING/CLOSED/STAGED/LOADED/SHIPPED/DELIVERED/CONSUMED/LOST
  owner_id         VARCHAR(32),
  ref_doc_type     VARCHAR(32),
  ref_doc_no       VARCHAR(64),
  dest_node_id     VARCHAR(32),           -- 目的门店 (XDK 必填)
  route_id         VARCHAR(32),
  gross_weight_g   BIGINT,
  volume_cm3       BIGINT,
  case_count       INT,
  piece_count      DECIMAL(18,4),
  is_homogeneous   TINYINT(1) NOT NULL DEFAULT 0,
  seal_no          VARCHAR(64),
  sealed_by        VARCHAR(32),
  sealed_at        DATETIME,
  asset_no         VARCHAR(64),           -- 物理器具编号 (与一次性 LPN 解耦)
  PRIMARY KEY (lpn),
  KEY idx_ctn_parent (parent_lpn),
  KEY idx_ctn_root (root_lpn),
  KEY idx_ctn_loc (warehouse_id, current_location_id),
  KEY idx_ctn_dest (dest_node_id, status),
  KEY idx_ctn_asset (asset_no)
);

-- 「容器与单据解耦」的正确落地: 容器头不绑单据, 内容行绑
-- ref_doc_* + source_mode + pegging_ref 是跨节点溯源与 XDK 一单到底的载体
CREATE TABLE container_content (
  lpn          VARCHAR(64) NOT NULL,
  line_no      INT NOT NULL,
  sku_id       VARCHAR(32) NOT NULL,
  lot_no       VARCHAR(64) NOT NULL DEFAULT '*',   -- 批次由 WMS 收发货时产生
  expire_date  DATE,
  qty          DECIMAL(18,4) NOT NULL,
  uom          VARCHAR(8) NOT NULL,
  base_qty     DECIMAL(18,4) NOT NULL,
  inv_status   VARCHAR(16) NOT NULL,
  owner_id     VARCHAR(32) NOT NULL,
  dest_node_id VARCHAR(32),                        -- 混装托盘时行级带目的门店
  ref_doc_type VARCHAR(16),                        -- OUTBOUND/ASN
  ref_doc_no   VARCHAR(64),
  ref_line_no  INT,
  source_mode  VARCHAR(8) NOT NULL DEFAULT 'SSTK', -- SSTK/XDK
  pegging_ref  VARCHAR(64),                        -- XDK 必填: 下游入库单行 ID (一单到底)
  PRIMARY KEY (lpn, line_no),
  KEY idx_ctc_sku (sku_id, lot_no),
  KEY idx_ctc_ref (ref_doc_type, ref_doc_no, ref_line_no),
  KEY idx_ctc_pegging (pegging_ref)
);

CREATE TABLE container_txn (
  txn_id          BIGINT NOT NULL AUTO_INCREMENT,
  lpn             VARCHAR(64) NOT NULL,
  txn_type        VARCHAR(16) NOT NULL,  -- CREATE/ADD_ITEM/REMOVE_ITEM/NEST/UNNEST/MOVE/CLOSE/OPEN/SPLIT/MERGE/SHIP/RECEIVE/CONSUME
  from_location_id VARCHAR(40),
  to_location_id   VARCHAR(40),
  from_parent_lpn  VARCHAR(64),
  to_parent_lpn    VARCHAR(64),
  sku_id          VARCHAR(32),
  qty_delta       DECIMAL(18,4),
  ref_doc_no      VARCHAR(64),
  operator_id     VARCHAR(32),
  occurred_at     DATETIME(3) NOT NULL,
  idem_key        VARCHAR(160) NOT NULL,
  PRIMARY KEY (txn_id),
  UNIQUE KEY uk_ctntxn_idem (idem_key),
  KEY idx_ctntxn_lpn (lpn, occurred_at)
);

-- -----------------------------------------------------------------------------
-- 6. 越库 (XDK) 供需配对
-- -----------------------------------------------------------------------------

CREATE TABLE cross_dock_alloc (
  xdk_alloc_id     BIGINT NOT NULL AUTO_INCREMENT,
  mode             VARCHAR(16) NOT NULL,  -- PRE_ALLOCATED/POST_ALLOCATED/PBYL
  warehouse_id     VARCHAR(32) NOT NULL,
  asn_no           VARCHAR(64),
  asn_line_no      INT,
  inbound_no       VARCHAR(64),
  inbound_line_no  INT,
  supplier_lpn     VARCHAR(64),           -- 供应商预贴 SSCC
  outbound_no      VARCHAR(64),
  outbound_line_no INT,
  dest_node_id     VARCHAR(32) NOT NULL,
  route_id         VARCHAR(32),
  sku_id           VARCHAR(32) NOT NULL,
  lot_no           VARCHAR(64),
  planned_qty      DECIMAL(18,4) NOT NULL,
  received_qty     DECIMAL(18,4) NOT NULL DEFAULT 0,
  sorted_qty       DECIMAL(18,4) NOT NULL DEFAULT 0,
  staged_qty       DECIMAL(18,4) NOT NULL DEFAULT 0,
  short_qty        DECIMAL(18,4) NOT NULL DEFAULT 0,
  lane_id          VARCHAR(32),
  dock_door        VARCHAR(16),
  status           VARCHAR(24) NOT NULL,
  PRIMARY KEY (xdk_alloc_id),
  KEY idx_xdk_in (asn_no, asn_line_no),
  KEY idx_xdk_out (outbound_no, outbound_line_no),
  KEY idx_xdk_dest (warehouse_id, dest_node_id, status),
  KEY idx_xdk_lpn (supplier_lpn)
);

CREATE TABLE xdk_reallocation_log (
  log_id        BIGINT NOT NULL AUTO_INCREMENT,
  warehouse_id  VARCHAR(32) NOT NULL,
  asn_no        VARCHAR(64),
  sku_id        VARCHAR(32) NOT NULL,
  trigger_type  VARCHAR(24) NOT NULL,   -- SHORT_RECEIPT/OVERAGE/LATE_ARRIVAL
  rule_code     VARCHAR(32),            -- 分摊规则
  before_json   JSON,
  after_json    JSON,
  operator_id   VARCHAR(32),
  occurred_at   DATETIME(3) NOT NULL,
  PRIMARY KEY (log_id),
  KEY idx_xdkre_asn (asn_no)
);

-- -----------------------------------------------------------------------------
-- 7. 运输 (TMS)
-- -----------------------------------------------------------------------------

-- load = 一台车的一次行程 (供给侧/运力的视角)
-- load_source=SHADOW: 外包场景看不到真实车次, 仅作成本与时效归集锚点
CREATE TABLE `load` (
  load_no          VARCHAR(64) NOT NULL,
  load_source      VARCHAR(8) NOT NULL DEFAULT 'REAL',  -- REAL/SHADOW
  carrier_id       VARCHAR(32),
  carrier_type     VARCHAR(16),   -- OWN/CONTRACT/PLATFORM
  vehicle_id       VARCHAR(32),
  plate_no         VARCHAR(32),
  vehicle_type     VARCHAR(32),
  driver_id        VARCHAR(32),
  driver_name      VARCHAR(64),
  driver_phone     VARCHAR(64),
  route_id         VARCHAR(32),
  origin_node_id   VARCHAR(32) NOT NULL,
  dock_id          VARCHAR(32),
  plan_depart_time DATETIME, actual_depart_time DATETIME,
  plan_arrive_time DATETIME, actual_arrive_time DATETIME,
  total_stops      INT, total_shipments INT, total_pallets INT, total_cases INT,
  plan_weight_g    BIGINT, plan_volume_cm3 BIGINT,
  load_rate_weight DECIMAL(5,4), load_rate_volume DECIMAL(5,4),
  temp_zone        VARCHAR(16),
  compartment_config JSON,         -- 多温区车厢分仓: [{"id":"C1","temp_zone":"FROZEN","volume_cm3":...}]
  seal_no          VARCHAR(64),    -- 冗余首封号; 完整记录见 load_seal
  rate_card_version VARCHAR(32),   -- 发车时冻结的计费版本
  -- 自有车队成本核算基础 (企业视角; 4PL 记的是收入, 企业记的是成本)
  mileage_m        BIGINT,
  duration_min     INT,
  stop_count       INT,
  actual_cost      DECIMAL(18,2),  -- 自有车: 折旧+油+过路+人工; 外包: 账单金额
  primary_waybill_no VARCHAR(64),  -- 整车场景的派生冗余字段, 非外键, 不参与业务判断
  status           VARCHAR(24) NOT NULL,
  PRIMARY KEY (load_no),
  KEY idx_load_status (status, plan_depart_time),
  KEY idx_load_route (route_id, plan_depart_time)
);

CREATE TABLE load_stop (
  load_no       VARCHAR(64) NOT NULL,
  stop_seq      INT NOT NULL,
  node_id       VARCHAR(32) NOT NULL,
  stop_type     VARCHAR(16) NOT NULL,  -- PICKUP/DELIVERY/CROSS_DOCK
  plan_eta      DATETIME,
  actual_arrive DATETIME,
  actual_depart DATETIME,
  time_window_start DATETIME,
  time_window_end   DATETIME,
  pallet_count  INT, case_count INT,
  status        VARCHAR(16) NOT NULL,
  exception_code VARCHAR(32),
  PRIMARY KEY (load_no, stop_seq),
  KEY idx_stop_node (node_id, plan_eta)
);

-- 车 x 票 关联汇总
-- 采用「先装车后过账」(见 10-goods-issue-timing.md): 一次发车 = 一次发货事实 = 一个 shipment
--   -> shipment 永远不跨车, load : shipment = 1 : N, 无需 split_flag / split_ratio
--   -> 若将来改为「先过账后装车」, 必须恢复 M:N 与 split 逻辑
-- 保留本表的理由: 计划 vs 实装份额对比 / POD 锚点 / 避免对 load_detail 做 DISTINCT
CREATE TABLE load_shipment (
  load_no             VARCHAR(64) NOT NULL,
  shipment_no         VARCHAR(64) NOT NULL,
  stop_seq            INT NOT NULL,
  planned_pallets     INT, planned_cases INT,
  planned_weight_g    BIGINT, planned_volume_cm3 BIGINT,
  loaded_pallets      INT, loaded_cases INT,
  loaded_weight_g     BIGINT, loaded_volume_cm3 BIGINT,
  status              VARCHAR(24) NOT NULL,
  PRIMARY KEY (load_no, shipment_no),
  KEY idx_ldshp_shp (shipment_no),
  KEY idx_ldshp_stop (load_no, stop_seq)
);

-- 装车物理明细: 只存顶层容器 (root LPN), 不展开子箱
-- ref_doc_type 支持 DELIVERY stop 挂 SHIPMENT / PICKUP stop 挂 ASN / 返仓挂 RETURN_ORDER
CREATE TABLE load_detail (
  load_no       VARCHAR(64) NOT NULL,
  stop_seq      INT NOT NULL,
  ref_doc_type  VARCHAR(16) NOT NULL,  -- SHIPMENT/ASN/RETURN_ORDER
  ref_doc_no    VARCHAR(64) NOT NULL DEFAULT '*',  -- 混装托盘留 '*', 归属下沉到 container_content
  lpn           VARCHAR(64) NOT NULL DEFAULT '*',  -- root LPN; 散货为 '*'
  package_no    VARCHAR(64) NOT NULL DEFAULT '*',
  is_bulk       TINYINT(1) NOT NULL DEFAULT 0,     -- 散货装车 (零担散箱/大件/生鲜筐)
  sku_id        VARCHAR(32),          -- 仅 is_bulk=1 时使用
  lot_no        VARCHAR(64),
  qty           DECIMAL(18,4),
  uom           VARCHAR(8),
  load_seq      INT,                  -- 装车顺序: LIFO, 先送的后装, 与 stop_seq 反向
  compartment_id VARCHAR(16),         -- 多温区车厢
  plan_flag     TINYINT(1) NOT NULL DEFAULT 1,  -- 计划行(1) vs 临时追加(0)
  scan_time     DATETIME(3),          -- NULL = 计划了但未扫 -> 发车前必须清空或转甩货
  operator_id   VARCHAR(32),
  unloaded_at   DATETIME(3),
  bump_reason   VARCHAR(32),          -- 甩货原因: NO_SPACE/NOT_STAGED/DAMAGED/CUTOFF
  PRIMARY KEY (load_no, stop_seq, ref_doc_type, ref_doc_no, lpn, package_no),
  KEY idx_lddet_lpn (lpn),
  KEY idx_lddet_ref (ref_doc_type, ref_doc_no),
  KEY idx_lddet_unscanned (load_no, scan_time)
);

-- 铅封记录: 一车多门/多点卸货会多次开封重封, 必须是子表
CREATE TABLE load_seal (
  seal_id       BIGINT NOT NULL AUTO_INCREMENT,
  load_no       VARCHAR(64) NOT NULL,
  seal_no       VARCHAR(64) NOT NULL,
  seal_type     VARCHAR(16) NOT NULL,  -- DEPART/MIDWAY/RESEAL
  compartment_id VARCHAR(16),
  stop_seq      INT,
  applied_at    DATETIME(3), applied_by VARCHAR(32),
  broken_at     DATETIME(3), broken_by  VARCHAR(32),
  photo_urls    JSON,
  PRIMARY KEY (seal_id),
  KEY idx_seal_load (load_no, stop_seq)
);

-- 配载变更留痕: PLANNED 之后的任何改动都进这里
CREATE TABLE load_change_log (
  log_id      BIGINT NOT NULL AUTO_INCREMENT,
  load_no     VARCHAR(64) NOT NULL,
  change_type VARCHAR(24) NOT NULL,  -- ADD_SHIPMENT/REMOVE_SHIPMENT/BUMP/RESEQUENCE/VEHICLE_SWAP/DRIVER_SWAP/CANCEL
  before_json JSON,
  after_json  JSON,
  reason_code VARCHAR(32),
  operator_id VARCHAR(32),
  occurred_at DATETIME(3) NOT NULL,
  PRIMARY KEY (log_id),
  KEY idx_ldchg_load (load_no, occurred_at)
);

-- 运单 = 承运合同与计费的事实
-- 粒度由承运商决定(按票/按车/按包裹), 不稳定 -> 不做 load 的外键, 通过 shipment 关联
CREATE TABLE waybill (
  waybill_no       VARCHAR(64) NOT NULL,
  internal_ref     VARCHAR(64),
  carrier_id       VARCHAR(32) NOT NULL,
  service_product  VARCHAR(32),
  load_no          VARCHAR(64),      -- 仅整车自营场景的冗余查询字段, 非外键
  ship_from_node_id VARCHAR(32),
  ship_to_node_id   VARCHAR(32),
  consignee_enc    VARBINARY(1024),
  package_count    INT,
  gross_weight_g   BIGINT,
  charged_weight_g BIGINT,          -- max(实重, 体积重)
  volume_cm3       BIGINT,
  declared_value   DECIMAL(18,2),
  cod_amount       DECIMAL(18,2),
  insurance_amount DECIMAL(18,2),
  freight_amount   DECIMAL(18,2),
  fuel_surcharge   DECIMAL(18,2),
  extra_charges    JSON,
  pickup_time      DATETIME,
  estimated_delivery DATETIME,
  actual_delivery  DATETIME,
  status           VARCHAR(24) NOT NULL,
  PRIMARY KEY (waybill_no),
  KEY idx_wb_load (load_no),
  KEY idx_wb_carrier (carrier_id, pickup_time)
);

-- waybill 与 shipment 多对多桥接
CREATE TABLE waybill_shipment (
  waybill_no  VARCHAR(64) NOT NULL,
  shipment_no VARCHAR(64) NOT NULL,
  PRIMARY KEY (waybill_no, shipment_no),
  KEY idx_wbshp_shp (shipment_no)
);

CREATE TABLE tracking_event (
  event_id    BIGINT NOT NULL AUTO_INCREMENT,
  waybill_no  VARCHAR(64),
  load_no     VARCHAR(64),
  event_code  VARCHAR(32) NOT NULL,   -- 内部统一码, 承运商码在 ACL 层映射
  event_desc  VARCHAR(512),
  occurred_at DATETIME(3) NOT NULL,
  received_at DATETIME(3) NOT NULL,
  node_id     VARCHAR(32),
  geo_lat DECIMAL(10,7), geo_lng DECIMAL(10,7),
  operator    VARCHAR(64),
  source      VARCHAR(16) NOT NULL,   -- CARRIER_API/DRIVER_APP/GPS/MANUAL
  raw_payload JSON,
  PRIMARY KEY (event_id, occurred_at),
  KEY idx_trk_wb (waybill_no, occurred_at),
  KEY idx_trk_load (load_no, occurred_at)
) PARTITION BY RANGE COLUMNS(occurred_at) ( /* 按天/月分区, 冷热分离 */
  PARTITION p_max VALUES LESS THAN (MAXVALUE)
);

-- -----------------------------------------------------------------------------
-- 8. 配送与签收 (DMS)
-- -----------------------------------------------------------------------------

CREATE TABLE delivery_route (
  route_id      VARCHAR(32) NOT NULL,
  route_code    VARCHAR(64) NOT NULL,
  warehouse_id  VARCHAR(32) NOT NULL,
  frequency     VARCHAR(24),   -- DAILY/EVERY_OTHER_DAY/WEEKLY
  standard_mileage_m BIGINT,
  standard_duration_min INT,
  status        VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (route_id),
  UNIQUE KEY uk_route_code (warehouse_id, route_code)
);

CREATE TABLE delivery_task (
  task_id      BIGINT NOT NULL AUTO_INCREMENT,
  load_no      VARCHAR(64) NOT NULL,
  stop_seq     INT NOT NULL,
  driver_id    VARCHAR(32),
  node_id      VARCHAR(32) NOT NULL,
  plan_arrive  DATETIME,
  actual_arrive DATETIME,
  handover_no  VARCHAR(64),
  status       VARCHAR(24) NOT NULL,
  PRIMARY KEY (task_id),
  KEY idx_dtask_load (load_no, stop_seq),
  KEY idx_dtask_driver (driver_id, plan_arrive)
);

CREATE TABLE pod (
  pod_id           BIGINT NOT NULL AUTO_INCREMENT,
  waybill_no       VARCHAR(64),
  load_no          VARCHAR(64),
  stop_seq         INT,
  shipment_no      VARCHAR(64),
  node_id          VARCHAR(32) NOT NULL,
  sign_time        DATETIME(3) NOT NULL,
  signer_name      VARCHAR(64),
  signer_relation  VARCHAR(32),
  sign_type        VARCHAR(24),   -- SELF/PROXY/LOCKER/CONTACTLESS
  signature_img    VARCHAR(512),
  photo_urls       JSON,
  geo_lat DECIMAL(10,7), geo_lng DECIMAL(10,7),
  geo_deviation_m  INT,           -- 与门店坐标偏差, 防虚假签收
  delivered_pallets INT, delivered_cases INT,
  diff_flag        TINYINT(1) NOT NULL DEFAULT 0,
  pod_no           VARCHAR(64),   -- 纸质回单号
  upload_by        VARCHAR(32),
  status           VARCHAR(16) NOT NULL,
  PRIMARY KEY (pod_id),
  KEY idx_pod_load (load_no, stop_seq),
  KEY idx_pod_wb (waybill_no)
);

CREATE TABLE pod_diff (
  diff_id      BIGINT NOT NULL AUTO_INCREMENT,
  pod_id       BIGINT NOT NULL,
  sku_id       VARCHAR(32),
  lpn          VARCHAR(64),
  expect_qty   DECIMAL(18,4),
  actual_qty   DECIMAL(18,4),
  diff_type    VARCHAR(16) NOT NULL,  -- SHORT/OVER/DAMAGE/WRONG_ITEM/REJECT
  reason_code  VARCHAR(32),
  liable_party VARCHAR(16),           -- WAREHOUSE/CARRIER/STORE/SUPPLIER
  photo_urls   JSON,
  claim_amount DECIMAL(18,2),
  settle_status VARCHAR(16),
  PRIMARY KEY (diff_id),
  KEY idx_poddiff_pod (pod_id)
);

CREATE TABLE delivery_exception (
  exc_id      BIGINT NOT NULL AUTO_INCREMENT,
  task_id     BIGINT NOT NULL,
  exc_type    VARCHAR(24) NOT NULL,  -- REJECT/RESCHEDULE/NO_ONE/WRONG_ADDR/DAMAGE/TIMEOUT
  reason_code VARCHAR(32),
  photo_urls  JSON,
  resolution  VARCHAR(512),
  resolved_at DATETIME,
  PRIMARY KEY (exc_id),
  KEY idx_exc_task (task_id)
);

-- 器具 (周转箱/托盘/笼车) 借还账
CREATE TABLE asset_ledger (
  asset_txn_id BIGINT NOT NULL AUTO_INCREMENT,
  asset_type   VARCHAR(16) NOT NULL,  -- TOTE/PALLET/CAGE/COLD_BOX
  asset_no     VARCHAR(64),
  txn_type     VARCHAR(16) NOT NULL,  -- ISSUE/RETURN/TRANSFER/LOST/SCRAP
  from_party   VARCHAR(32),
  to_party     VARCHAR(32),
  qty          INT NOT NULL,
  ref_doc_type VARCHAR(32),
  ref_doc_no   VARCHAR(64),
  operator_id  VARCHAR(32),
  occurred_at  DATETIME(3) NOT NULL,
  idem_key     VARCHAR(160) NOT NULL,
  PRIMARY KEY (asset_txn_id),
  UNIQUE KEY uk_asset_idem (idem_key),
  KEY idx_asset_party (to_party, asset_type, occurred_at),
  KEY idx_asset_no (asset_no)
);

-- -----------------------------------------------------------------------------
-- 9. 计费 (BMS)
-- -----------------------------------------------------------------------------

CREATE TABLE rate_card (
  rate_card_id  VARCHAR(32) NOT NULL,
  version       VARCHAR(32) NOT NULL,
  carrier_id    VARCHAR(32) NOT NULL,
  origin_region VARCHAR(32),
  dest_region   VARCHAR(32),
  vehicle_type  VARCHAR(32),
  charge_mode   VARCHAR(16) NOT NULL,  -- PER_TRIP/PER_KG/PER_CBM/PER_PIECE/PER_PALLET/PER_KM/PER_STOP
  tier_rules    JSON,
  min_charge    DECIMAL(18,2),
  valid_from    DATE, valid_to DATE,
  PRIMARY KEY (rate_card_id, version),
  KEY idx_rate_carrier (carrier_id, valid_from)
);

-- 成本归集: 把 load / 运费账单摊回 shipment -> 出库行 -> SKU / 门店
-- 这是货主企业特有的能力; 4PL 算的是「收客户多少」, 企业算的是「花了多少、摊给谁」
CREATE TABLE cost_allocation (
  alloc_id     BIGINT NOT NULL AUTO_INCREMENT,
  period       VARCHAR(16) NOT NULL,
  source_type  VARCHAR(16) NOT NULL,  -- LOAD/WAYBILL/FREIGHT_BILL
  source_no    VARCHAR(64) NOT NULL,
  target_type  VARCHAR(24) NOT NULL,  -- SHIPMENT/OUTBOUND_LINE/SKU/STORE/CATEGORY
  target_no    VARCHAR(64) NOT NULL,
  cost_element VARCHAR(24) NOT NULL,  -- FREIGHT/FUEL/WAITING/UNLOAD/RETURN/DETENTION
  driver       VARCHAR(16) NOT NULL,  -- 分摊动因: WEIGHT/VOLUME/CASE/STOP/EQUAL
  driver_value DECIMAL(18,4),
  amount       DECIMAL(18,4) NOT NULL,
  PRIMARY KEY (alloc_id),
  KEY idx_ca_source (source_type, source_no),
  KEY idx_ca_target (target_type, target_no, period),
  KEY idx_ca_period (period, cost_element)
);

CREATE TABLE freight_bill (
  bill_no        VARCHAR(64) NOT NULL,
  carrier_id     VARCHAR(32) NOT NULL,
  period         VARCHAR(16) NOT NULL,
  base_amount    DECIMAL(18,2),
  accessorial    DECIMAL(18,2),
  deduction      DECIMAL(18,2),
  payable_amount DECIMAL(18,2),
  recon_status   VARCHAR(16) NOT NULL,
  invoice_no     VARCHAR(64),
  PRIMARY KEY (bill_no),
  KEY idx_bill_carrier (carrier_id, period)
);

-- -----------------------------------------------------------------------------
-- 10. 集成: 事务性发件箱
-- -----------------------------------------------------------------------------

CREATE TABLE domain_event (
  event_id          VARCHAR(40) NOT NULL,   -- ULID
  event_type        VARCHAR(64) NOT NULL,
  event_version     VARCHAR(8)  NOT NULL,
  aggregate_type    VARCHAR(32) NOT NULL,
  aggregate_id      VARCHAR(64) NOT NULL,
  aggregate_version BIGINT      NOT NULL,
  payload           JSON        NOT NULL,
  occurred_at       DATETIME(3) NOT NULL,
  published_at      DATETIME(3),
  publish_status    VARCHAR(16) NOT NULL DEFAULT 'PENDING',
  retry_count       INT NOT NULL DEFAULT 0,
  idem_key          VARCHAR(200) NOT NULL,
  PRIMARY KEY (event_id),
  UNIQUE KEY uk_evt_idem (idem_key),
  KEY idx_evt_pending (publish_status, occurred_at),
  KEY idx_evt_agg (aggregate_type, aggregate_id, aggregate_version)
);
