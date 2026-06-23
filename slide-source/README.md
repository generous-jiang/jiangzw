# 武汉 FC 料箱到人系统方案 — 单页 PPTX 源文件

本目录用于生成 `../武汉FC料箱到人系统方案.pptx`（16:9 宽屏，单页，所有元素均为 PowerPoint 原生可编辑对象）。

## 文件说明

| 文件 | 作用 |
|------|------|
| `slide.js`   | 唯一数据源：调色板、字体、画布尺寸与全部版面元素（与渲染器无关的 op 列表） |
| `build.js`   | 由 `slide.js` 生成 `.pptx`（pptxgenjs，原生形状 / 文本框 / 连线 / 图标） |
| `preview.js` | 由同一份 `slide.js` 生成 SVG→PNG 预览，用于版面校对（坐标与 PPTX 完全一致） |
| `icons.js`   | 图标光栅化（react-icons / Font Awesome），build 与 preview 共用 |
| `preview.png`| 版面预览图 |

## 重新生成

```bash
npm install -g pptxgenjs react-icons react react-dom sharp
export NODE_PATH=$(npm root -g)

node build.js                       # 生成 .pptx
python /path/to/pptx/scripts/rezip.py 武汉FC料箱到人系统方案.pptx   # 压缩瘦身
node preview.js                     # 生成 preview.png（核对版面）
node preview.js debug               # 额外输出文本框边界，用于排查溢出
```

## 设计要点

- **字体**：中文 Microsoft YaHei、拉丁/数字 Arial。
- **配色**：以深蓝 / 品牌蓝为主，青色为辅，橙色为强调色。
- **版面**：标题区 → 端到端作业流程（5 步）→ 系统组成（软件 / 设备 / 工作站）→ 核心效能指标。
- 内容依据总体系统方案图（A71-L-E1-H-CN ×150、HRC-3000-E4-CN ×25、In_01~06、out_01~22、5 组×6=30、17 个接口等），
  并结合海柔 HaiPick / 闪攀料箱到人方案的典型效能指标（已在脚注标注为参考值）。
