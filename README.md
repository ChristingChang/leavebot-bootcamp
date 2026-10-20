# LeaveBot —— 2 天 SDD agentic coding 實戰營

> **這是一片空地。** D1 你們寫規格，D2 讓 agent 照規格把 app 從 0 長出來。
> 題目是「一句話請假」：員工打一句話，AI 轉成假單，規則由程式檢查，主管核准。
> 講義在課程網站（講師會給網址）。

```text
leavebot-bootcamp/
├── README.md  AGENTS.md  CLAUDE.md   ← 你在這裡；AGENTS.md 是 agent 的規則
├── course/                           ← 課程給的：題目、技術棧、模板、範例、eval 句子
└── .claude/ .agents/ .codex/ .mcp.json   ← agent 的設定，打開工具就生效，不用動
```

你們會長出來的：`docs/`（六份規格＋經驗紀錄）、`issues/`（疊代票）、`backend/`、`frontend/`、`pyproject.toml`、`dev.sh`。

## 課前（開課前一週做完）

1. **拿到 repo**：每組 fork，clone 自己的那一份。Windows 先跑 `git config --global core.symlinks true`，否則 Codex 找不到技能。
2. **裝工具**：Python 3.12、Node 24、Claude Code 或 Codex。細節照講義的「課前準備」。
3. **申請 Anthropic API key**，確認帳戶有額度。D2 你們的 app 要用它呼叫模型。
4. **讀題目**：[`course/LEAVEBOT.md`](./course/LEAVEBOT.md)。
5. **確認接上了**：在 repo 根目錄打開 `claude` 或 `codex`，打 `/compass`（Codex：`$compass`），看得到技能表就完成。第一次開會問要不要啟用專案的 MCP，選同意。

**一律在 repo 根目錄啟動 agent**。在子目錄啟動，護欄不會生效。

## 想知道更多

| 想知道 | 看 |
|---|---|
| agent 的設定檔各管什麼、10 個技能、2 個 MCP | [`course/HARNESS.md`](./course/HARNESS.md) |
| 技術棧、紅線、I0 骨架怎麼生 | [`course/STACK.md`](./course/STACK.md) |
| 六份規格怎麼寫 | [`course/templates/`](./course/templates/) |

課程結束後想要完整的工具鏈（38 個技能），用模板 repo [`agent-skills-starter`](https://github.com/Zenobia000/agent-skills-starter) 開新專案。

技能與 guard hooks 衍生自 [luca-skills](https://github.com/Luca0x5755/luca-skills)（MIT），聲明見 [`.claude/THIRD-PARTY-NOTICES.md`](./.claude/THIRD-PARTY-NOTICES.md)。
