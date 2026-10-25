---
name: to-spec
description: 將已定案的 LeaveBot 討論收斂到課程 Brief、PRD、SRS 範本與追溯編號。只有使用者指定時啟動。
disable-model-invocation: true
---

# To Spec

把已確認的需求寫進 `docs/01-brief.md`、`docs/02-prd.md`、`docs/03-srs.md`。這支技能負責收斂與追溯，不重新訪談；尚未定案的必要選擇先回 `/grilling` 或 `/grill-with-docs`。

1. 讀 `AGENTS.md`、`course/LEAVEBOT.md`、`course/STACK.md`、三份對應的 `course/templates/`，以及 `course/templates/TRACEABILITY.md`。讀現有 01–03 與相關 04–06；既有文件是修訂基礎，不重建另一份規格。
2. 從對話中逐項整理目標、非目標、角色、流程、AC、FR、NFR。每項區分「已定案」「可由資料查得」「待決」。遇到規格相互衝突或必要決定未定，依 `AGENTS.md` 問清楚，不猜測。
3. 依模板寫或修 01–03，保留已有編號與引用。新編號按 `TRACEABILITY.md` 發出；作廢編號保留並標示，不重用。檢查 Brief → PRD → SRS 的引用能追到來源。
4. 列出下游可能受影響的 SAD、SDS、測試計畫與票；若這次修訂已使其內容不一致，同步修正或明確指出待決阻礙。規格偏差記到 `docs/LESSONS.md`。

輸出是 repo 的 `docs/` 文件，不建立原作者的 issue tracker、`docs/agents/` 或第二套 promise ID。後續可用 `/to-architecture`，測試規劃用 `/to-test-plan`，多張票用 `/to-tickets`。

改編參考：[luca-skills 的 to-spec](https://github.com/Zenobia000/luca-skills/blob/main/skills/core/to-spec/SKILL.md)。
