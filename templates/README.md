# 全局模板库

复制下列模板到对应项目目录使用。所有模板均已遵循 [`.kiro/steering/writing-style.md`](../.kiro/steering/writing-style.md) 业务化写作规范。

| 模板 | 用途 | 放置位置 |
|---|---|---|
| [solution-template.md](solution-template.md) | 系统解决方案（业务版） | `projects/{code}/01-solution/` |
| [prd-template.md](prd-template.md) | 产品需求文档 | `projects/{code}/02-prd/` |
| [biz-report-slidev.md](biz-report-slidev.md) | 业务汇报幻灯片（Slidev 格式） | `projects/{code}/04-reports/` 或 `reports/` |
| [weekly-update.md](weekly-update.md) | 跨项目周报 | `reports/weekly/` |

## 使用方式

直接告诉 Kiro：

> "用 `templates/solution-template.md` 模板，把 `这份纪要内容` 套进去做成 wms-platform 的方案 v0.1 草稿。"

Kiro 会自动套结构、补 Mermaid 图、按业务语言行文，并放到对应项目目录。
