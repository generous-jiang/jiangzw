---
inclusion: always
---

# 仓库结构与多项目协作规范

本仓库用于管理多个并行的零售供应链产品项目（仓储平台化、ERP 等）的非代码交付物：系统方案、PRD、原型、汇报材料。

## 一、目录结构（不可随意变更）

```
jiangzw/
├── .kiro/steering/        # Kiro 自动遵循的规范（领域术语、写作风格、本文件）
├── README.md              # 项目组合看板（Portfolio Dashboard）—— 所有项目入口
├── projects/              # 每个项目一个独立子目录
│   ├── _template/         # 新项目模板，复制即用
│   ├── wms-platform/      # 示例：仓储平台化
│   └── erp-master-data/   # 示例：ERP 主数据治理
├── templates/             # 全局可复用模板（方案/PRD/汇报/周报）
├── reports/               # 跨项目汇报（周报/月报/季度汇报）
│   ├── weekly/
│   ├── monthly/
│   └── quarterly/
└── shared/                # 跨项目共享资源（图标、术语扩展、行业数据）
    └── assets/
```

## 二、单项目内部结构

每个 `projects/{project-code}/` 下必须包含：

```
{project-code}/
├── README.md              # 项目概况卡（元信息+导航）
├── meta.yaml              # 结构化元数据，用于看板聚合
├── 01-solution/           # 系统解决方案（每版一个文件）
├── 02-prd/                # 产品需求文档
├── 03-prototype/          # HTML 静态原型（可发 GitHub Pages）
├── 04-reports/            # 本项目专属汇报材料
└── 05-meeting-notes/      # 评审/对齐会议纪要
```

## 三、项目代号规范

- 格式：`{域}-{业务关键词}`，全小写连字符
- 域：`wms`（仓储）/ `erp`（ERP）/ `oms`（订单）/ `tms`（运输）/ `scp`（计划）
- 例：`wms-platform`、`wms-picking-optimization`、`erp-master-data`、`erp-ap-reconciliation`

## 四、meta.yaml 必填字段（用于看板聚合）

```yaml
code: wms-platform              # 项目代号
name: 仓储平台化                # 中文名
domain: WMS                     # 域
owner: 江某某                   # 项目负责人
stakeholders:                   # 关键干系人
  - 业务: 某业务总监
  - 财务: 某财务负责人
stage: 设计中                   # 立项中/调研中/设计中/开发中/试点中/已上线/已暂停
priority: P0                    # P0/P1/P2
start_date: 2026-04-01
target_launch: 2026-09-30
last_update: 2026-05-26
key_metrics:                    # 项目要改善的业务指标
  - 库存周转天数: 45→35
  - 人效: 80单/h → 100单/h
risks:
  - 三方仓接入标准未统一
dependencies:
  - erp-master-data            # 依赖的其他项目代号
```

## 五、新建项目流程

1. 复制 `projects/_template/` 整个目录，重命名为新项目代号
2. 填写 `meta.yaml`
3. 在顶层 `README.md` 的项目矩阵中追加一行
4. 创建分支 `init/{project-code}` 提交，开 PR 由相关方确认

## 六、跨项目协作约定

- **依赖追踪**：在 `meta.yaml` 的 `dependencies` 中显式列出，看板会自动展示依赖图
- **共享术语**：领域术语统一维护在 `.kiro/steering/domain-glossary.md`，不要在单项目里重复定义
- **跨项目汇报**：放在 `reports/` 下，按时间组织（如 `reports/weekly/2026-W22.md`）
- **冲突解决**：当多个项目对同一业务概念有不同设计时，必须在月度汇报里专门列章节"跨项目对齐"

## 七、Git 工作流

- 主分支：`main`，任何改动必须通过 PR 合入
- 分支命名：
  - `init/{project-code}` —— 新项目初始化
  - `update/{project-code}/{topic}` —— 项目内更新
  - `report/{period}` —— 跨项目汇报，如 `report/2026-w22`
- PR 标题：`[{project-code}] 简短描述` 或 `[report] 简短描述`
- 重大评审通过后打 Tag：`{project-code}-v1.0-approved`
