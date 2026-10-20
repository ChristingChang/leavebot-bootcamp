#!/usr/bin/env bash
# check-skills.sh 的回歸規格。每個案例蓋一個臨時的假技能目錄，跑一次腳本，比對判決。
# 執行：bash .maintain/test-check-skills.sh（.maintain/check.sh 會跑）
set -u
GUARD=$(cd "$(dirname "$0")" && pwd)/check-skills.sh
fail=0

skill() {  # skill <dir> <name> <body>
  mkdir -p "$ROOT/s/$1"
  printf -- '---\nname: %s\ndescription: x\n---\n\n%s\n' "$2" "$3" > "$ROOT/s/$1/SKILL.md"
}

check() {  # check <want> <label>
  if (cd "$ROOT" && SKILLS_DIR=s bash "$GUARD" >/dev/null 2>&1); then got=PASS; else got=FAIL; fi
  if [ "$got" = "$1" ]; then printf '  ✓ %-4s %s\n' "$1" "$2"; else printf '  ✗ want=%s got=%s  %s\n' "$1" "$got" "$2"; fail=1; fi
  rm -rf "$ROOT"
}

ROOT=$(mktemp -d); skill a a 'Next: `/b`, then `/clear`.'; skill b b 'ok'
check PASS "引用存在的技能與內建指令"

ROOT=$(mktemp -d); skill a a 'Next: `/implement`.'
check FAIL "引用不存在的技能"

ROOT=$(mktemp -d); skill a wrong 'ok'
check FAIL "name 不等於資料夾名"

ROOT=$(mktemp -d); skill a a 'ok'; sed -i '1i\\' "$ROOT/s/a/SKILL.md"
check FAIL "frontmatter 前有空行"

ROOT=$(mktemp -d); skill a a 'Path like docs/x/y and `/compact` are fine.'
check PASS "非反引號開頭的路徑不算引用"

ROOT=$(mktemp -d); skill a a 'Call `/api/health` and keep everything under `/api/`.'
check PASS "API 路徑不算技能引用"

ROOT=$(mktemp -d); skill a a 'Then `/compact next we build ticket 002`.'
check PASS "內建指令後面帶參數"

ROOT=$(mktemp -d); skill a a 'Then `/ghost now`.'
check FAIL "不存在的技能後面帶參數仍然擋"


exit $fail
