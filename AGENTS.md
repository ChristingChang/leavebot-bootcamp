# LeaveBot —— agent 工作規則

> 這是上課 repo 附的**起點**。D1 最後一個單元會用 `templates/agent-rules/` 的範本改寫它，加上你們自己的紅線。
> Claude Code 透過 `CLAUDE.md`（只有一行 `@AGENTS.md`）讀這一份。每個檔案各管什麼，見 `HARNESS.md`。

## 規格在哪

| 文件 | 回答 |
|---|---|
| `docs/01-brief.md` | 為什麼做：goal、non-goal |
| `docs/02-prd.md` | 為誰做、做什麼：persona、user flow、story、驗收條件（AC） |
| `docs/03-srs.md` | 什麼叫做好了：use case、FR、NFR |
| `docs/04-sad.md` | 怎麼組起來：C4、資訊流、誰負責什麼、ADR |
| `docs/05-sds.md` | 每一塊怎麼做：ER、API、畫面、模組 |
| `docs/06-test-plan.md` | 怎麼驗：每個測試案例（TC）對到哪條需求 |
| `issues/` | D2 的疊代票 I0–I4 |
| `LEAVEBOT.md` | 題目、公司規章（課堂假設，不是勞動法規）、MVP 範圍 |
| `STACK.md` | 固定的技術棧、目錄、唯一定死的 API |

文件之間衝突、或規格沒寫到的行為：**停下來問**，不要自己決定。

## 怎麼跑

```bash
.venv/bin/pytest                          # 全部測試：kit、工具、backend/tests
bash scripts/dev.sh                       # 同時起 backend 與 frontend
.venv/bin/python scripts/trace.py         # 需求 → 測試案例 → 測試，哪裡斷了
.venv/bin/python scripts/run_eval.py      # 用 eval 集打 POST /api/parse，算準確率
```

**一律用 `.venv/bin/python`、`.venv/bin/pytest`**（Windows：`.venv\Scripts\python`）。agent 的 shell 不會自動啟用 venv，很多機器上也沒有 `python` 這個指令，只有 `python3`。

說「完成」之前，必須跑過 `pytest` 並貼出結果；有改到需求或測試時，也貼 `trace.py` 的缺口。

## 紅線

- **照 `STACK.md`。** 不換框架、不加套件、不開 CORS、不在前端寫死後端位址。要例外，先問。
- **只透過 `kit/llm.py` 呼叫模型**（`build_llm(load_llm_settings())`）。不自己 import 模型 SDK、不打開模型的工具。
- 測試**不准呼叫真的 LLM**，一律注入 `kit.llm.FakeLLM`。
- 剩餘天數、撞期檢查、核准，**一律由程式碼或人決定**，不採用 LLM 給的任何數字或狀態。
- LLM 的輸出必須通過格式驗證才能存進資料庫。
- 每個測試標註它實作的 TC 與驗的需求：`@pytest.mark.req("TC-03", "AC-01.1")`。
- 不准修改或刪除測試來讓測試通過。
- API key 只放 `.env`，不准寫進任何其他檔案。
