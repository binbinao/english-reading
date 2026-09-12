#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 data/index.json 生成:
  1) index.html  —— 归档首页（GitHub Pages 入口，手机友好）
  2) README.md 中 INDEX 标记区内的索引表格
用法: python3 scripts/build_index.py
"""
import json
import pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "index.json"
README = ROOT / "README.md"


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load():
    if not DATA.exists():
        return {"articles": []}
    return json.loads(DATA.read_text(encoding="utf-8"))


def render_index_html(items):
    items = sorted(items, key=lambda x: x["date"], reverse=True)
    cards = []
    for a in items:
        cards.append(
            f'''      <a class="card" href="{esc(a['url'])}">
        <div class="c-top">
          <span class="c-date">{esc(a['date'])}</span>
          <span class="c-src">{esc(a['source'])}</span>
          <span class="c-cat">{esc(a.get('category',''))}</span>
        </div>
        <div class="c-title">{esc(a['title'])}</div>
        <div class="c-meta">{a.get('words','')} 词 · 生词 {a.get('vocabCount','')} · 术语 {a.get('termCount','')} · {esc(a.get('level',''))}</div>
      </a>''')

    total_words = sum(int(a.get("words") or 0) for a in items)
    span = ""
    if items:
        span = f"{items[-1]['date']} → {items[0]['date']}"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>每日英文精读 · 归档</title>
<style>
  *{{box-sizing:border-box;}}
  body{{margin:0;background:#F2F2F4;color:#1C1C1E;
    font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
    font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased;}}
  .wrap{{max-width:560px;margin:0 auto;background:#fff;min-height:100vh;
    box-shadow:0 0 0 1px rgba(0,0,0,.04);}}
  header{{padding:26px 20px 20px;background:linear-gradient(168deg,#FFFDF8 0%,#FFFFFF 60%);
    border-bottom:1px solid #E6E6EA;}}
  h1{{margin:0 0 6px;font-size:22px;font-weight:800;letter-spacing:-.3px;}}
  .tagline{{margin:0;font-size:13px;color:#8E8E93;line-height:1.7;}}
  .kpis{{display:flex;gap:0;margin:18px -20px -20px;border-top:1px solid #E6E6EA;}}
  .kpi{{flex:1;text-align:center;padding:13px 4px;border-right:1px solid #E6E6EA;}}
  .kpi:last-child{{border-right:none;}}
  .kpi b{{display:block;font-size:18px;font-weight:800;letter-spacing:-.3px;}}
  .kpi span{{display:block;font-size:10.5px;color:#8E8E93;margin-top:2px;}}
  main{{padding:16px 16px 40px;}}
  .sec{{font-size:11px;font-weight:700;letter-spacing:1.6px;color:#8E8E93;margin:6px 0 11px;}}
  .card{{display:block;text-decoration:none;color:inherit;border:1px solid #E6E6EA;
    border-radius:13px;padding:13px 14px;margin-bottom:9px;background:#fff;transition:background .15s;}}
  .card:active{{background:#F7F7F9;}}
  .c-top{{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:8px;}}
  .c-date{{font-size:11px;font-weight:700;color:#fff;background:#1C1C1E;padding:4px 8px;border-radius:6px;line-height:1;}}
  .c-src{{font-size:11px;font-weight:600;color:#C97B0A;background:#FDF4E3;border:1px solid #E7C88A;
    padding:3px 8px;border-radius:999px;line-height:1.2;}}
  .c-cat{{font-size:11px;font-weight:600;color:#2C5FD6;background:#EDF2FE;border:1px solid #A9C0EE;
    padding:3px 8px;border-radius:999px;line-height:1.2;}}
  .c-title{{font-size:15px;font-weight:700;line-height:1.45;letter-spacing:-.2px;margin-bottom:6px;
    font-family:Georgia,"Times New Roman",serif;}}
  .c-meta{{font-size:11.5px;color:#8E8E93;}}
  .empty{{padding:40px 20px;text-align:center;color:#8E8E93;font-size:13px;}}
  footer{{padding:16px 20px 30px;border-top:1px solid #E6E6EA;font-size:11.5px;color:#8E8E93;line-height:1.8;}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>每日英文精读</h1>
    <p class="tagline">每天一篇 1000–2000 词主流外刊原文<br>生词与专业术语逐条标注 · 点击即看释义</p>
    <div class="kpis">
      <div class="kpi"><b>{len(items)}</b><span>已读篇数</span></div>
      <div class="kpi"><b>{total_words:,}</b><span>累计词数</span></div>
      <div class="kpi"><b>1000–2000</b><span>单篇词数</span></div>
    </div>
  </header>
  <main>
    <div class="sec">ARCHIVE{(' · ' + esc(span)) if span else ''}</div>
    {chr(10).join(cards) if cards else '<div class="empty">还没有文章，等第一期推送。</div>'}
  </main>
  <footer>
    来源：Scientific American · The Economist · The Washington Post · The New York Times 等<br>
    仅作语言学习用途，版权归原作者与出版方所有。
  </footer>
</div>
</body>
</html>
'''


def render_readme_table(items):
    items = sorted(items, key=lambda x: x["date"], reverse=True)
    if not items:
        return "| 日期 | 来源 | 标题 | 词数 | 生词 | 术语 |\n|---|---|---|---|---|---|\n| — | — | 暂无 | — | — | — |"
    lines = ["| 日期 | 来源 | 标题 | 词数 | 生词 | 术语 | 链接 |",
             "|---|---|---|---:|---:|---:|---|"]
    for a in items:
        lines.append(
            f"| {a['date']} | {a['source']} | [{a['title']}]({a['url']}) | "
            f"{a.get('words','')} | {a.get('vocabCount','')} | {a.get('termCount','')} | "
            f"[HTML]({a['url']}) · [TXT]({a.get('txt', a['url'])}) |"
        )
    return "\n".join(lines)


def main():
    data = load()
    items = data.get("articles", [])

    (ROOT / "index.html").write_text(render_index_html(items), encoding="utf-8")
    print(f"index.html 已生成，共 {len(items)} 篇")

    if README.exists():
        text = README.read_text(encoding="utf-8")
        start, end = "<!-- INDEX:START -->", "<!-- INDEX:END -->"
        if start in text and end in text:
            pre = text.split(start)[0]
            post = text.split(end)[1]
            new = pre + start + "\n" + render_readme_table(items) + "\n" + end + post
            README.write_text(new, encoding="utf-8")
            print("README.md 索引已更新")
        else:
            print("!! README.md 缺少 INDEX 标记，已跳过")
    else:
        print("!! README.md 不存在，已跳过")


if __name__ == "__main__":
    main()
