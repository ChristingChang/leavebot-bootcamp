#!/usr/bin/env bash
# 技能的三條規矩，加上一條「不准指向不存在的技能」。
#   1. frontmatter 前不能有任何字元（多一個空行，整個技能會被靜默略過）
#   2. name 必須等於資料夾名
#   3. SKILL.md 裡寫到的 `/名字`，必須是這裡有的技能，或是工具的內建指令
#
# 第 3 條是因為這個 repo 只留了上課用的技能：從完整版搬過來時，
# 引用到沒帶過來的技能，學員照著打就會撲空。
#
# 無輸出 = 全部通過。有輸出時 exit 1。

set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1

SKILLS_DIR=${SKILLS_DIR:-.claude/skills}
BUILTINS=" clear compact init review diff help model hooks plan new "

found=0

for skill in "$SKILLS_DIR"/*/SKILL.md; do
  [ -f "$skill" ] || continue
  dir=$(basename "$(dirname "$skill")")

  [ "$(head -c 3 "$skill")" = "---" ] || { echo "壞 frontmatter  $skill（第一行必須是 ---）"; found=1; }

  name=$(sed -n '2,/^---$/{s/^name:[[:space:]]*//p}' "$skill" | head -1)
  [ "$name" = "$dir" ] || { echo "名字不符  $skill：name=$name，資料夾=$dir"; found=1; }

  # `/名字` 後面接反引號或空白才算技能；接 / 的是路徑（例：`/api/health`）
  for ref in $(grep -oE '`/[a-z][a-z0-9-]*[` ]' "$skill" | sed 's/^`\///; s/[` ]$//' | sort -u); do
    [ -f "$SKILLS_DIR/$ref/SKILL.md" ] && continue
    case "$BUILTINS" in *" $ref "*) continue ;; esac
    echo "懸空引用  $skill → /$ref（沒有這個技能，也不是內建指令）"
    found=1
  done
done

exit $found
