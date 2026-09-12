# 每日英文精读

每天从主流外刊（Scientific American / The Economist / The Washington Post / The New York Times 等）
选一篇 **1000–2000 词**的英语原文，标注通用生词与专业术语，做成手机端可读的单页 HTML。

> 在线阅读：<https://binbinao.github.io/english-reading/>

---

## 每日产物长什么样

- **单文件 HTML**，420px 手机视口，正文 Georgia 衬线体，首字下沉，阅读进度条
- **双色高亮**：蓝色虚线 = 通用生词；金色实线 = 专业术语 / 专有名词
- **点击任意高亮词** → 底部弹层释义卡（音标 · 词性 · 中文释义 · 改写例句）
- 支持「标记已掌握」（划线变灰，词汇表同步）、字号 A−/A＋
- 文末分 Tab 词汇表，与正文共用同一份词库，保证不漏不错

## 目录结构

```
english-reading/
├── index.html              # 归档首页（GitHub Pages 入口，由脚本生成）
├── README.md               # 本文件（索引表由脚本自动更新）
├── data/
│   └── index.json          # 唯一数据源：每篇的日期/来源/标题/词数/生词数
├── articles/
│   ├── YYYY-MM-DD.html     # 当日精读页
│   └── YYYY-MM-DD.txt      # 当日纯英文原文（便于复制到其它阅读器）
├── template/
│   └── reading-template.html   # 版式模板（17 个 {{占位符}}）
└── scripts/
    ├── build_index.py      # 由 index.json 重建 index.html 与 README 索引表
    └── publish.sh          # 重建索引 → commit → push
```

## 每期索引

<!-- INDEX:START -->
| 期号 | 推送日 | 原文日 | 来源 | 标题 | 词数 | 生词 | 术语 | 链接 |
|---|---|---|---|---|---:|---:|---:|---|
| 第 002 期 | 2026-09-12 | 2026-09-11 | Scientific American | 25 years after 9/11, survivors are still getting sick—here are the numbers | 1112 | 27 | 12 | [HTML](articles/2026-09-12-002.html) · [TXT](articles/2026-09-12-002.txt) |
| 第 001 期 | 2026-09-12 | 2026-09-08 | Scientific American | AI may have just solved a million-dollar math problem. The field will never be the same | 1136 | 29 | 8 | [HTML](articles/2026-09-12.html) · [TXT](articles/2026-09-12.txt) |
<!-- INDEX:END -->

## 怎么新增一期

1. 把当天的 HTML 存为 `articles/YYYY-MM-DD.html`，纯原文存为 `articles/YYYY-MM-DD.txt`
2. 在 `data/index.json` 的 `articles` 数组**头部**追加一条记录
3. 执行发布：

```bash
bash scripts/publish.sh 2026-09-13
```

脚本会：重建 `index.html` 和上面的索引表 → `git add -A` → `git commit -m "reading: 日期"` → `git push origin main`。
推送失败不会丢数据，本地提交已完成，稍后手动 `git push origin HEAD` 即可。

## 版式模板

`template/reading-template.html` 是从已确认的成品反向抽出的模板，占位符：

`{{PAGE_TITLE}} {{EPISODE}} {{SOURCE}} {{CATEGORY}} {{DATE}} {{LEVEL}} {{TITLE}} {{SUBTITLE}} {{BYLINE}} {{WORDS}} {{MINUTES}} {{BODY_HTML}} {{VOCAB_JSON}} {{SOURCE_FULL}} {{SOURCE_URL}} {{SOURCE_URL_TEXT}} {{NEXT_HINT}}`

其中 `{{BODY_HTML}}` 是正文段落（高亮写成 `<span class="m v" data-w="键名">词</span>`，`t` 表示术语），
`{{VOCAB_JSON}}` 是对应的词条对象。**两个 key 必须严格一一对应** —— 生成后请校验：

```bash
python3 - <<'PY'
import re
h = open('articles/YYYY-MM-DD.html').read()
marks = set(re.findall(r'data-w="([a-z]+)"', h))
keys  = set(re.findall(r'^  ([a-z]+):\{t:', h, re.M))
print("正文标记:", len(marks), "词条:", len(keys), "缺定义:", marks - keys, "未使用:", keys - marks)
PY
```

要求输出 `缺定义: set() 未用: set()`。

## 授权

仅作个人语言学习用途，版权归原作者与出版方所有。生词释义为编辑整理，例句均为改写示例句。
