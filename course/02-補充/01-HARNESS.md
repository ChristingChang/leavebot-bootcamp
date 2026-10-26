# HARNESS — 在本課使用通用 Agent 工具

先能完成當前任務，再需要時展開工具細節。技能是工作方法；本課階段、輸入與產出由 [WORKFLOW](../01-上課/02-WORKFLOW.md) 指定。

## 開始前只確認四件事

| 項目 | 位置 | 課堂怎麼用 |
|---|---|---|
| 專案規則 | `AGENTS.md`；Claude Code 經 `CLAUDE.md` 引用 | 技術邊界、決策與完成條件 |
| Skills | `.claude/skills/`；Codex 經 `.agents/skills` 連結 | 指定方法，再給當前任務與資料 |
| Hooks | `.claude/hooks/`、`.claude/settings.json`、`.codex/hooks.json` | 在已登記且匹配的工具事件檢查動作，不是完整安全隔離 |
| MCP | `.mcp.json`、`.codex/config.toml` | context7 查文件，playwright 操作瀏覽器 |

一律從 repo 根目錄開始課程，減少相對路徑與設定來源混淆。設定檔存在不代表連線成功；請實際讀取檔案、呼叫技能與操作工具確認。

## 當前階段使用的技能

目前共 16 支（15 支通用技能加 Archify）。全清單在 [技能說明](../../.claude/skills/README.md)；不用一次記完。

| 情境 | Claude Code | Codex |
|---|---|---|
| 不確定下一步 | `/compass`＋目前目標與 WORKFLOW | `$compass`＋相同上下文 |
| 訪談／已有文件再討論 | `/grilling`、`/grill-with-docs` | `$grilling`、`$grill-with-docs` |
| 收斂需求／系統設計 | `/to-spec`、`/to-architecture` | `$to-spec`、`$to-architecture` |
| 測試計畫／拆票 | `/to-test-plan`、`/to-tickets` | `$to-test-plan`、`$to-tickets` |
| 實作與紅綠循環 | `/implement`、`/tdd` | `$implement`、`$tdd` |
| 原因不明的錯誤／審查 | `/diagnosing-bugs`、`/code-review` | `$diagnosing-bugs`、`$code-review` |
| 換人／換工具 | `/handoff` | `$handoff` |
| 畫流程 | `/archify` | `$archify` |

`compass` 是依當前問題選路，並不保證列出完整技能清單。課前請它讀 WORKFLOW 後建議第一步，能指出正確資料與產出才算接上。

## 對話怎麼接

同一階段的訪談與寫檔留在同一對話。要換階段前先把已確認決策寫入檔案；新對話明確讀那些路徑。實作每張票另開一個對話。同一工作太長可使用工具的壓縮功能；換人用 handoff，並確認交接檔實際能被下一位讀取。不要為換卡而丟失尚未寫下的決策。

## 工具的能力與限制

- `AGENTS.md` 與 skill 是指令，不保證每次遵守。人仍要驗收。
- 現有 git／secret guards 針對匹配的 Bash 事件與命令檢查，不能宣稱所有工具、所有繞行方式都被擋住。
- Claude Code 的專案 MCP 與 hooks 要在課前實際試。Codex 專案設定可能受信任狀態、平台與版本影響；本 repo 過去的非互動驗證有落差，不能以 Claude 的結果代替 Codex。兩種工具各自跑開場檢查，未接通項目記為未驗證。
- 無瀏覽器工具時由小組人工操作；無文件工具時用官方文件；無 Archify 時在 SRS/SAD 寫 Mermaid。能力不足不假裝成功。
- `pytest-on-stop.sh` 是**選用 Claude Code 範本**，預設未啟用。先完成骨架、測試可跑後才由講師示範。它不能保證先紅後綠，也不代替人工檢查。

開場檢查是唯讀探索、技能導航、MCP 操作；不要在有成果的工作目錄刻意執行危險命令來測試 guard。維護者回歸檢查在 `.maintain/check.sh`，與學生 app 測試不同。
