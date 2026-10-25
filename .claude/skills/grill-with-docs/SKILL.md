---
name: grill-with-docs
description: 針對已有文件的專案訪談需求與決策，邊查既有規格邊整理已定事項，避免跨對話重問。只有使用者指定時啟動。
disable-model-invocation: true
---

# Grill With Docs

在這個 repo 已有規格或架構文件時，以現有文件為背景進行 `/grilling` 式訪談。沒有 codebase 或文件時，直接用 `/grilling` 即可。

1. 先讀 `AGENTS.md`、相關的 `docs/01-brief.md` 至 `docs/05-sds.md`、`docs/LESSONS.md` 和 `course/LEAVEBOT.md`；不存在的檔案略過。把已寫定的事當成既有決定，不重新問。文件矛盾或缺少必要決定時，依 `AGENTS.md` 停下來問。
2. 用 `/grilling` 的問題樹與一輪一層訪談方法。查得到的專案事實自行查；產品決策請使用者定案。每輪說明問題所依據的文件與目前已定的條件。
3. 共識確認後，只更新承載該決定的文件：範圍與目標在 01、使用者行為與 AC 在 02、系統要求在 03、持久技術決策與 ADR 在 04、細節合約在 05。新規格使用 `course/templates/`，沿用 `course/templates/TRACEABILITY.md` 的編號，不另建 `CONTEXT.md`、`docs/adr/` 或決策總帳。
4. 偏差、誤解、踩坑才記 `docs/LESSONS.md`。列出已定事項、仍待決問題、改動的文件與接下來需要的規格工作。訪談不會自動啟動實作。

此技能改編自 [luca-skills 的 grill-with-docs](https://github.com/Zenobia000/luca-skills/blob/main/skills/core/grill-with-docs/SKILL.md)；本專案文件位置與追溯編號以課程規格為準。
