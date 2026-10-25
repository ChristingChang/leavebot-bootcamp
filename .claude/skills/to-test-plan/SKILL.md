---
name: to-test-plan
description: 依 PRD、SRS、SAD、SDS 與課程範本產出或修訂 docs/06-test-plan.md，含 TC、AI eval、退出條件與追溯矩陣。只有使用者指定時啟動。
disable-model-invocation: true
---

# To Test Plan

為 LeaveBot 建立課程唯一的測試計畫 `docs/06-test-plan.md`。原作者的 `/test-blueprint` 管測試層級、接縫、追溯；`/uat-cases` 管驗收案例與凍結 TC。本技能把這兩種判斷放進課程 06 範本，不建立平行的測試藍圖或 UAT 總帳。

1. 讀 `AGENTS.md`、`course/templates/06-test-plan.md`、`course/templates/TRACEABILITY.md`、`docs/02-prd.md` 至 `docs/05-sds.md`、`course/STACK.md`、`course/LEAVEBOT.md` 和 `course/fixtures/`。不存在的必要規格或互相矛盾的條款，先依 `AGENTS.md` 問清楚。
2. 逐條盤點 AC、FR、NFR 與 SAD／SDS 接縫。依模板安排驗收、系統／eval、整合、單元層級；每個測試案例寫可觀察情境與預期結果。先提出候選情境，再由人篩選，最終 TC 不超過模板的 30 個上限；至少列出三個刪掉的情境及理由。
3. 使用既有 `TC-xx` 編號；新增時接續編號，作廢號保留而不重用。每條 AC／FR／NFR 都要有 TC，或在「不測什麼」寫理由。追溯矩陣在建置前填需求、TC、層級；測試檔與狀態由每張票的實作更新。不要因為尚未寫測試而把狀態標為已通過。
4. 按 06 範本訂 AI eval 的 fixture、逐欄比對規則、逾時、注入案例、數值門檻與門檻理由。區分兩種執行：一般 `pytest` 測試以 `@pytest.mark.req("TC-xx", "...")` 對應 TC，模型依 `AGENTS.md` 注入假實作；I4 另生成 eval 腳本，逐句呼叫 `POST /api/parse` 量 AI 解析準確率，依課程固定比對規則與計畫門檻判定。eval 的 fixture 句子不是另一套 TC 編號。寫出退出條件並檢查追溯缺口。
5. 修訂現有 06 時做差異更新，保留已發編號與人工篩選理由。若規格或已實作內容偏離，依 `AGENTS.md` 修正來源或記錄偏差，不為了讓矩陣好看而改需求。

參考原作者的 [test-blueprint](https://github.com/Zenobia000/luca-skills/blob/main/skills/core/test-blueprint/SKILL.md) 與 [uat-cases](https://github.com/Zenobia000/luca-skills/blob/main/skills/core/uat-cases/SKILL.md)；此 repo 以 `course/templates/06-test-plan.md` 為輸出合約。
