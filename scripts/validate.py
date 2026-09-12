#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校验当日精读 HTML 的完整性。发布前必须通过。
用法: python3 scripts/validate.py articles/YYYY-MM-DD.html
返回码 0 = 通过, 1 = 失败
"""
import re
import sys
import pathlib

OK, FAIL = "[PASS]", "[FAIL]"
problems = []


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/validate.py articles/YYYY-MM-DD.html")
        return 1

    p = pathlib.Path(sys.argv[1])
    if not p.exists():
        print(f"{FAIL} 文件不存在: {p}")
        return 1

    h = p.read_text(encoding="utf-8")

    # 1) 占位符必须全部替换
    left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", h)))
    if left:
        problems.append(f"仍有未替换占位符: {left}")
    else:
        print(f"{OK} 占位符已全部替换")

    # 2) 正文高亮与词条定义必须一一对应
    marks = set(re.findall(r'data-w="([a-z0-9]+)"', h))
    keys = set(re.findall(r"^  ([a-z0-9]+):\{t:", h, re.M))
    missing, unused = marks - keys, keys - marks
    if missing:
        problems.append(f"高亮词缺定义: {sorted(missing)}")
    if unused:
        problems.append(f"词条未在正文使用: {sorted(unused)}")
    if not missing and not unused:
        print(f"{OK} 词条映射完整（正文 {len(marks)} 个高亮 / {len(keys)} 条定义）")

    # 3) 词条字段完整性（注意模板里是 JS 对象字面量，key 可带引号也可不带）
    def has_field(body, f):
        return re.search(rf'(?:^|[{{,]\s*)"?{f}"?\s*:', body) is not None

    entries = re.findall(r"^  ([a-z0-9]+):\{(.*?)\},?\s*$", h, re.M)
    bad = []
    for k, body in entries:
        for field in ("t", "w", "ipa", "pos", "cn", "ex"):
            if not has_field(body, field):
                bad.append(f"{k} 缺 {field}")
        if not re.search(r'(?:^|[{{,]\s*)"?t"?\s*:\s*"([vt])"', body):
            bad.append(f"{k} 的 t 值不是 v/t")
    if bad:
        problems.append("词条字段不完整: " + "; ".join(bad[:8]))
    else:
        print(f"{OK} {len(entries)} 条词条字段齐全")

    # 4) 词数标注核对
    m = re.search(r"<b>([\d,]+)</b><span>词数 WORDS</span>", h)
    if m:
        n = int(m.group(1).replace(",", ""))
        if 1000 <= n <= 2000:
            print(f"{OK} 标注词数 {n}，在 1000–2000 区间内")
        else:
            problems.append(f"标注词数 {n} 超出 1000–2000 区间")
    else:
        problems.append("未找到词数标注位")

    # 5) 分类计数是否为 0（说明 JS 没接管）
    for cid, label in (("vcount", "生词"), ("tcount", "术语")):
        mm = re.search(rf'id="{cid}">(\d+)<', h)
        if mm and mm.group(1) == "0":
            print(f"     （{label} 计数由 JS 运行时填充，静态为 0 属正常）")

    print("-" * 46)
    if problems:
        for x in problems:
            print(f"{FAIL} {x}")
        return 1
    print(f"{OK} 全部校验通过，可以发布")
    return 0


if __name__ == "__main__":
    sys.exit(main())
