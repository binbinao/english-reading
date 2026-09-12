#!/usr/bin/env bash
# 提交并推送当日精读材料到 GitHub
# 用法: bash scripts/publish.sh [YYYY-MM-DD]
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
DATE="${1:-$(date +%F)}"

# 1) 先重建索引，保证首页与 README 同步
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/build_index.py || echo "[warn] 索引重建失败，继续推送"
fi

# 2) 暂存
git add -A
if git diff --cached --quiet; then
  echo "[skip] 没有变更需要提交"
  exit 0
fi

# 3) 提交
git commit -q -m "reading: ${DATE}" || { echo "[error] commit 失败"; exit 1; }
echo "[ok] 已提交 reading: ${DATE}"

# 4) 推送（远端未配置或网络不通时不阻塞，材料已落地本地）
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "[warn] 未配置 origin 远端，跳过推送"
  exit 0
fi

if git push -q origin HEAD 2>/dev/null; then
  echo "[ok] 已推送到 origin/$(git rev-parse --abbrev-ref HEAD)"
else
  echo "[warn] 推送失败（网络或权限问题）。本地已提交，可稍后手动执行: git push origin HEAD"
  exit 0
fi
