#!/usr/bin/env bash
# 這個 repo 的全部檢查，一個入口。給維護者用：改了技能、hook、MCP 設定或 fixtures 之後跑這支。
# 學員用不到 —— 上課 repo 裡沒有任何程式，學員的測試是自己的 .venv/bin/pytest。
#
# 檢查項目用找的，不用列的 —— 新增一支 .maintain/check-*.sh 或一支
# test-*.sh，它自己就會被跑到。
#
# 全綠 exit 0；任何一項紅了 exit 1，且會把每一項的判決列出來。

set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
source .maintain/python.sh || exit 1

fail=0

run() {
  local name=$1; shift
  local out status
  out=$("$@" 2>&1); status=$?
  if [ $status -eq 0 ]; then
    printf '✓ %s\n' "$name"
  else
    printf '✗ %s\n' "$name"
    printf '%s\n' "$out" | sed 's/^/    /'
    fail=1
  fi
}

# --- 技能與 hook 的接線 -----------------------------------------------------
for s in .maintain/check-*.sh; do
  [ -f "$s" ] || continue
  run "$(basename "$s")" bash "$s"
done

# --- 回歸規格：檢查腳本、guard hook、範本 hook ------------------------------
for t in .maintain/test-*.sh course/02-補充/templates/hooks/test-*.sh; do
  [ -f "$t" ] || continue
  run "$t" bash "$t"
done

if command -v jq >/dev/null 2>&1; then
  for t in .claude/hooks/test-*.sh; do
    [ -f "$t" ] || continue
    run "$t" bash "$t"
  done
else
  printf '! 略過 guard 測試：找不到 jq\n'
fi

# --- eval 句子的標準答案 ----------------------------------------------------
run "check-fixtures.py" "$COURSE_PYTHON" .maintain/check-fixtures.py

exit $fail
