# 原型目录

每个原型一个子目录，含独立 `index.html`。

```
03-prototype/
├── login-flow/
│   └── index.html
└── picking-task/
    └── index.html
```

## 推荐技术
- 纯 HTML + Tailwind CDN（无构建，复制即用）
- 复杂交互可用 Alpine.js（CDN 引入即可）

## 发布到 GitHub Pages
仓库 Settings → Pages → Source 选 `main` → 路径选根或 `/docs`。  
访问：`https://{owner}.github.io/{repo}/projects/{code}/03-prototype/{prototype-name}/`
