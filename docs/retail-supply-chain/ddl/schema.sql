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
  po_line_ref     VARCHAR(64),
  PRIMARY KEY (asn_no, line_no),
  KEY idx_asnline_sku (sku_id)
);

CREATE TABLE inbound_order (
  inbound_no    VARCHAR(64) NOT NULL,
  asn_no        VARCHAR(64),
  warehouse_id  VARCHAR(32) NOT NULL,
  inbound_type  VARCHAR(16) NOT NULL,  -- PURCHASE/TRANSFER/RETURN/PRODUCTION/XDOCK
  owner_id      VARCHAR(32) NOT NULL,
  dock_id       VARCHAR(32),
  arrive_time   DATETIME,
  start_time    DATETIME,
  finish_time   DATETIME,
  qc_required   TINYINT(1) NOT NULL DEFAULT 0,
  status        VARCHAR(24) NOT NULL,
  PRIMARY KEY (inbound_no),
  KEY idx_ib_wh_status (warehouse_id, status)
);

CREATE TABLE inbound_line (
  inbound_no    VARCHAR(64) NOT NULL,
  line_no       INT NOT NULL,
  asn_line_no   INT,
  sku_id        VARCHAR(32) NOT NULL,
  plan_qty      DECIMAL(18,4) NOT NULL,
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
  inv_status    VARCHAR(16) NOT NULL DEFAULT 'AVAILABLE',
  PRIMARY KEY (inbound_no, line_no)
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
  operation_mode VARCHAR(16) NOT NULL DEFAULT 'SSTK',
  source_line_ref VARCHAR(64),
  PRIMARY KEY (outbound_no, line_no),
  KEY idx_obline_sku (sku_id)
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

CREATE TABLE shipment (
  shipment_no        VARCHAR(64) NOT NULL,
  warehouse_id       VARCHAR(32) NOT NULL,
  ship_from_node_id  VARCHAR(32) NOT NULL,
  ship_to_node_id    VARCHAR(32) NOT NULL,
  total_packages     INT, total_cases INT, total_pallets INT,
  gross_weight_g     BIGINT, volume_cm3 BIGINT,
  temp_zone          VARCHAR(16),
  required_pickup_time   DATETIME,
  promised_delivery_time DATETIME,
  service_level      VARCHAR(24),
  carrier_id         VARCHAR(32),
  waybill_no         VARCHAR(64),
  load_no            VARCHAR(64),
  special_req        JSON,
  status             VARCHAR(24) NOT NULL,
  PRIMARY KEY (shipment_no),
  KEY idx_shp_load (load_no),
  KEY idx_shp_wh_status (warehouse_id, status)
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

CREATE TABLE container_content (
  lpn          VARCHAR(64) NOT NULL,
  line_no      INT NOT NULL,
  sku_id       VARCHAR(32) NOT NULL,
  lot_no       VARCHAR(64) NOT NULL DEFAULT '*',
  expire_date  DATE,
  qty          DECIMAL(18,4) NOT NULL,
  uom          VARCHAR(8) NOT NULL,
  base_qty     DECIMAL(18,4) NOT NULL,
  inv_status   VARCHAR(16) NOT NULL,
  owner_id     VARCHAR(32) NOT NULL,
  dest_node_id VARCHAR(32),
  ref_doc_no   VARCHAR(64),
  ref_line_no  INT,
  PRIMARY KEY (lpn, line_no),
  KEY idx_ctc_sku (sku_id, lot_no)
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

CREATE TABLE `load` (
  load_no          VARCHAR(64) NOT NULL,
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
  seal_no          VARCHAR(64),
  rate_card_version VARCHAR(32),   -- 发车时冻结的计费版本
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

CREATE TABLE load_detail (
  load_no     VARCHAR(64) NOT NULL,
  stop_seq    INT NOT NULL,
  shipment_no VARCHAR(64) NOT NULL,
  lpn         VARCHAR(64),
  package_no  VARCHAR(64),
  load_seq    INT,                 -- 装车顺序: 先送的后装
  scan_time   DATETIME(3),
  operator_id VARCHAR(32),
  unloaded_at DATETIME(3),
  PRIMARY KEY (load_no, stop_seq, shipment_no, lpn, package_no),
  KEY idx_lddet_lpn (lpn),
  KEY idx_lddet_shp (shipment_no)
);

CREATE TABLE waybill (
  waybill_no       VARCHAR(64) NOT NULL,
  internal_ref     VARCHAR(64),
  carrier_id       VARCHAR(32) NOT NULL,
  service_product  VARCHAR(32),
  load_no          VARCHAR(64),
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
