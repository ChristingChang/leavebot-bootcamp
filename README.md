# LeaveBot — 第二天的空白學生專案

第一天在獨立資料夾體驗 Vibe Coding、比較結果並練習 PRD；第二天用這個 repo，學習如何用規格、通用 skills、測試與人工驗收穩定交付。

**今天做一條完整路徑：選員工 → 填請假單 → 驗證 → 存檔 → 我的假單顯示待審核。** 主管核准、額度與一句話 AI 解析是延伸。

## 從這裡開始

1. Fork 本 repo 的 `main`，clone 自己的 fork。只複製 main 即可；checkpoint 從講師 upstream 取得。
2. 準備 Git、Python 3.12、能正常登入的 Claude Code 或 Codex，以及瀏覽器。Archify 使用 Node（套件最低 18；課前用受支援版本試跑），應用程式主線不需要 Node 或 LLM API key。
3. 在 repo 根目錄開工具，讀 [`course/WORKFLOW.md`](course/WORKFLOW.md) 的開場提示。Claude Code 用 `/技能`，Codex 用 `$技能`。
4. 依工作流程逐步產出文件、票與程式，不先複製空模板占位。需要同組已完成決策時先讀文件。

Windows 使用 Codex 共用技能前，確認 `.agents/skills` 是指向 `../.claude/skills` 的連結；無法建立連結時請講師協助，不能只以設定檔存在當成工具已接通。

| 要做什麼 | 讀哪裡 |
|---|---|
| 今天每一步、對應技能與提示詞 | [WORKFLOW](course/WORKFLOW.md) |
| 題目與基本／延伸範圍 | [LEAVEBOT](course/LEAVEBOT.md) |
| 技術棧、安裝、啟動與測試 | [STACK](course/STACK.md) |
| 規則、skills、hooks、MCP | [HARNESS](course/HARNESS.md) |
| 文件的最小格式 | [templates](course/templates/README.md) |
| 落後時接續 | [CHECKPOINTS](course/CHECKPOINTS.md) |
| 通用技能選擇清單 | [Skills](.claude/skills/README.md) |

`main` 只有教材與工具設定；`docs/`、`issues/`、`backend/`、`pyproject.toml` 由學生產生。checkpoint 是另外的教學快照。舊分支整合紀錄見 [維護紀錄](course/MAINTENANCE.md)。

講義與講師教材在 [ai-vibe-coding-beginner](https://github.com/Zenobia000/SDD-agent-coding-beginner)。技能與 guard 的來源及授權見 [THIRD-PARTY-NOTICES](.claude/THIRD-PARTY-NOTICES.md)。
