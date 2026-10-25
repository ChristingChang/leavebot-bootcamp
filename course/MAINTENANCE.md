# 2026-10-25 課程整合與舊分支

新版以 `fb70f38` 的通用 skills 為基礎，選取 `refactor/form-slice-course` 的 Archify 工具，重寫課程專屬規格。沒有以舊分支覆蓋通用技能。

| 舊分支 | 原始 SHA | 保存 tag | 狀態 |
|---|---|---|---|
| refactor/form-slice-course | 7e80822355bb29a523f0fcba6441bfc77e82f4bb | archive/form-slice-course-20261025 | 已被新版課程取代 |
| refactor/barren-land | 41b350eefa181567c7ba9c30eba0daf21f1b065b | archive/barren-land-20261025 | 歷史設計參考 |

整合前 main 保存在 `archive/pre-unified-course-20261025`。舊分支不再作學生起點；已確認上述 tags 同步遠端，並退役兩個舊分支名稱；以原 SHA 的條件檢查防止刪到同時更新的分支。Tags 保留原始歷史。

通用 skills 的能力描述不放課表、固定票數或 LeaveBot 功能。課程改動從 `WORKFLOW.md`、`PLAN.json`、提示詞與模板開始，最後同步講義並跑 `.maintain/check-course.py`。
