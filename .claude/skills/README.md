# Skills

這裡的技能描述**可重用的工作方法**，不替專案決定文件數量、票數、技術棧或測試工具。本 repo 的具體要求在根目錄 `AGENTS.md`、`course/` 與已定的專案規格；技能執行時讀取並遵守它們。Claude Code 用 `/名稱`，Codex 用 `$名稱`。

`.agents/skills` 是指向此目錄的 symlink，兩個工具讀的是同一份 `SKILL.md`。

| 技能 | 何時用 | 啟動方式 |
| --- | --- | --- |
| [archify](archify/SKILL.md) | 依需求建立可檢查的流程與系統圖 | 使用者或 agent |
| [compass](compass/SKILL.md) | 不確定接下來該做什麼 | 使用者指定 |
| [grilling](grilling/SKILL.md) | 需要釐清或挑戰一個決策 | 使用者或 agent |
| [grill-with-docs](grill-with-docs/SKILL.md) | 已有文件，要接著訪談 | 使用者指定 |
| [feasibility](feasibility/SKILL.md) | 評估想法、方案或關鍵風險是否可行 | 使用者或 agent |
| [to-spec](to-spec/SKILL.md) | 把已定決策寫成規格 | 使用者指定 |
| [to-architecture](to-architecture/SKILL.md) | 設計元件、資料、介面與取捨 | 使用者指定 |
| [to-test-plan](to-test-plan/SKILL.md) | 安排驗證案例、門檻與追溯 | 使用者指定 |
| [writing-for-agents](writing-for-agents/SKILL.md) | 建立或修改 agent 讀的文件 | 使用者或 agent |
| [to-tickets](to-tickets/SKILL.md) | 依成果與依賴拆工作票 | 使用者指定 |
| [implement](implement/SKILL.md) | 完成一張票或小型規格 | 使用者指定 |
| [tdd](tdd/SKILL.md) | 用紅燈、綠燈、重構實作可測行為 | 使用者或 agent |
| [diagnosing-bugs](diagnosing-bugs/SKILL.md) | 失敗原因不明或時好時壞 | 使用者或 agent |
| [code-review](code-review/SKILL.md) | 對照規範與要求審查變更 | 使用者或 agent |
| [handoff](handoff/SKILL.md) | 換人、換工具或換對話接手 | 使用者指定 |
| [writing-hooks](writing-hooks/SKILL.md) | 需要工具層守衛或排查 hook | 使用者或 agent |

這是一份**選擇清單**，不是固定流程。`to-tickets` 依目標、規格、工作大小與使用者的取捨決定票數；`to-spec`、`to-architecture` 和 `to-test-plan` 沿用各專案既有的文件位置與編號。本 repo 共 16 支技能。LeaveBot 課程的階段與提示詞見 [`course/01-上課/02-WORKFLOW.md`](../../course/01-上課/02-WORKFLOW.md)，工具操作說明見 [`course/02-補充/01-HARNESS.md`](../../course/02-補充/01-HARNESS.md)。
