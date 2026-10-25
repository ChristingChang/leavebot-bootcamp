---
name: implement
description: 依 LeaveBot 一張疊代票完成一條可測的路徑，協調 TDD、驗證、追溯矩陣與審查。只有使用者指定時啟動。
disable-model-invocation: true
---

# Implement

一次只完成 `issues/` 裡的一張票。此技能是建置編排；測試方法使用本 repo 的 `/tdd`，變更審查使用 `/code-review`。

1. 讀票、其引用的 `docs/` 條款、`AGENTS.md`、`course/STACK.md`、`docs/LESSONS.md` 和相關現有程式。規格衝突或缺少必要決定時停下來問，不改規格去配合程式。
2. 明確列出這張票要做的可觀察行為、TC 與測試接縫。I0 骨架按 `course/STACK.md` 建；需要測試驅動的行為按 `/tdd` 一次做一個紅→綠→重構循環。測試標 `@pytest.mark.req("TC-xx", "AC/FR/NFR 編號")`；模型測試只注入假實作。
3. 完成票的 Done when，跑完整 `.venv/bin/pytest`（Windows 使用 `.venv\Scripts\pytest`），貼出結果。更新 `docs/06-test-plan.md` 追溯矩陣，讓每個本票 TC 對到實際測試檔；偏差與踩坑記 `docs/LESSONS.md`。
4. 依 `/code-review` 的 Standards 與 Spec 兩軸檢查這張票的 diff，修正可確認的問題。回報完成行為、測試結果、未完成項與原因。只有票的條件實際達成且測試結果已貼出，才稱完成。

不自動提交、推送、合併或改動另一張票。原作者技能的 `CONTEXT.md`、`docs/capabilities/` 和自動 commit 慣例不套到這個 repo。改編參考：[luca-skills 的 implement](https://github.com/Zenobia000/luca-skills/blob/main/skills/core/implement/SKILL.md)。
