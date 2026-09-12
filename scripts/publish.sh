#!/usr/bin/env bash
# 提交并推送当日精读材料到 GitHub
# 用法: bash scripts/publish.sh [YYYY-MM-DD]
# 退出码: 0 = 成功推送或无需提交; 1 = 推送失败（云沙箱下等于当天产物丢失，必须重试/排查）
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

# 4) 推送。本地跑失败可稍后补推；云端沙箱是一次性的，失败即丢数据，
#    所以这里重试 3 次、暴露真实错误，最后以非零码退出。
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "[warn] 未配置 origin 远端，跳过推送"
  exit 0
fi

out=""
for attempt in 1 2 3; do
  if out=$(git push origin HEAD 2>&1); then
    echo "[ok] 已推送到 origin/$(git rev-parse --abbrev-ref HEAD)"
    exit 0
  fi
  echo "[retry $attempt/3] 推送失败：$(printf '%s' "$out" | tail -2 | tr '\n' ' ')"
  [ "$attempt" -lt 3 ] && sleep 5
done

echo "[error] 推送失败（已重试 3 次）"
echo "[error] 真实错误：$(printf '%s' "$out" | tail -5 | tr '\n' ' ')"
echo "[warn] 材料已在本地提交：git log --oneline -1 → $(git log --oneline -1 2>/dev/null)"
echo "[warn] 本地环境可稍后手动补推；云沙箱环境请让任务报告失败并重跑。"
exit 1
