# HARNESS —— agent 的設定檔各管什麼

> D1 第一個單元用這個 repo 當解剖標本。Claude Code 和 Codex 不是只有「對話框」：
> 它們每次啟動都會讀一組檔案，決定**要守什麼規則、會什麼技能、哪些動作做不到、能連到哪些外部工具**。
> 後面你要改規則、被 guard 擋下來、讓 agent 開瀏覽器，都要先知道是哪個檔案在作用。

## 一張圖

```text
leavebot-bootcamp/                     ← 一律在這裡（repo 根目錄）啟動 claude / codex
├── AGENTS.md                          ← ① 規則（專案大腦）。Codex 讀這份
├── CLAUDE.md                          ← 只有一行 @AGENTS.md。Claude Code 讀這份，再被導到 AGENTS.md
├── .claude/
│   ├── skills/<名字>/SKILL.md         ← ② 技能。Claude Code 打 /名字
│   │   └── agents/openai.yaml         ←    給 Codex 的「只准使用者觸發」設定
│   ├── hooks/guard-git.sh             ← ③ hook：擋危險的 git 指令
│   ├── hooks/guard-secrets.sh         ←    擋把疑似金鑰 commit 進去
│   └── settings.json                  ←    Claude Code 登記 hooks
├── .mcp.json                          ← ④ MCP：Claude Code 能連的外部工具
├── .agents/skills → ../.claude/skills ← symlink，Codex 從這裡讀同一份技能，打 $名字
├── .codex/
│   ├── hooks.json                     ←    Codex 登記同一對 guard
│   └── config.toml                    ←    Codex 的 MCP 設定（同兩個工具）
├── course/                            ← 課程給的規格與素材，不是設定
└── .maintain/                         ← 維護這個 repo 用的檢查，學員不用管
```

## 四件套

| | 是什麼 | 強度 | 例 |
|---|---|---|---|
| ① **規則**（`AGENTS.md`） | 每次對話都帶著的文字 | agent 大部分時候會遵守，**不是每一次** | 「說完成前要貼測試結果」 |
| ② **技能**（`.claude/skills/`） | 叫了才載入的流程 | 叫了就照流程走 | `/tdd`：先紅燈再綠燈 |
| ③ **hook**（`.claude/hooks/`） | 工具動作前後自動跑的腳本 | **做不到**，agent 繞不過去 | `git add -A` 被擋下 |
| ④ **MCP**（`.mcp.json`） | 讓 agent 多出一組外部工具 | 給它**能力**，不是限制它 | 開瀏覽器點過畫面、查最新版文件 |

判斷口訣：**違反了會有人受傷的，降成 hook；其他寫成規則。缺的是能力，接 MCP。**

## 10 個技能

| Claude Code | Codex | 做什麼 | 什麼時候 |
|---|---|---|---|
| `/compass` | `$compass` | 不知道下一步用哪個技能時問它 | 隨時 |
| `/grilling` | `$grilling` | 讓 AI 拷問你，產出 Brief 與 PRD | D1 |
| `/to-architecture` | `$to-architecture` | 產出 SAD 與 SDS | D1 |
| `/writing-for-agents` | `$writing-for-agents` | 寫專案大腦 `AGENTS.md` 的「本專案」段 | D1 |
| `/to-tickets` | `$to-tickets` | 切成 I0–I4 疊代票，寫進 `issues/` | D1 |
| `/tdd` | `$tdd` | 從票上的測試案例開始，先紅燈再綠燈；收尾更新追溯矩陣與經驗紀錄 | D2 |
| `/diagnosing-bugs` | `$diagnosing-bugs` | 紅燈修不好時：重現、縮小、一次驗一個假說 | D2 |
| `/code-review` | `$code-review` | 審查改動是否守規範、是否做到票要求的事 | D2 |
| `/handoff` | `$handoff` | 換組員或換工具接手前，把狀態寫成一份交接檔 | D2 |
| `/writing-hooks` | `$writing-hooks` | 一條規則被違反了會有人受傷，就把它寫成 hook | 隨時 |

## 這個 repo 接了哪兩個 MCP

兩個都是通用的，不用帳號、不用金鑰，任何專案都用得上：

| MCP | 給 agent 什麼能力 | 這門課用在哪 |
|---|---|---|
| **context7** | 查套件的最新官方文件 | Next.js 16、Anthropic SDK 的寫法和 agent 記得的不一樣時，查了再寫，少一半幻覺 |
| **playwright** | 開一個看不見的瀏覽器，點畫面、讀頁面 | D2 每個疊代結束，請 agent 照 PRD 的 user flow 自己點一遍前端 |

第一次在這個 repo 啟動 Claude Code，它會問要不要啟用專案的 MCP，選同意。之後用 `/mcp` 看連線狀態。

> ⚠️ **安全**：MCP 給的是能力，能力越大，被注入攻擊時能做的事越多。這兩個都在你自己的電腦上跑、不碰你的帳號。**不要**隨便加來路不明的 MCP，加之前先看它能做什麼。

## 原廠設定 vs 專案設定

| | 原廠設定（課程給的，不要改） | 專案設定（你們長出來的） |
|---|---|---|
| 規則 | `AGENTS.md` 上半段「原廠規則」 | `AGENTS.md` 下半段「本專案」 |
| 經驗 | — | `docs/LESSONS.md` |
| 流程 | `.claude/skills/` | — |
| 擋什麼 | `.claude/hooks/`、`settings.json`、`.codex/hooks.json` | 想加自己的 hook，見 `course/templates/hooks/` |
| 能力 | `.mcp.json`、`.codex/config.toml` | `.env`（你自己的 API key） |

**經驗為什麼放 `docs/LESSONS.md`，不靠 agent 自己的記憶**：Claude Code 的記憶存在你家目錄，只有你看得到，組員和 Codex 都讀不到，換電腦就沒了。寫進 repo 才會跟著版控走、全組共用。

## 使用者層 vs 專案層

| | 位置 | 誰看得到 |
|---|---|---|
| 專案層 | repo 裡的 `AGENTS.md`、`.claude/`、`.mcp.json`、`docs/` | 所有 clone 這個 repo 的人，跟著版控走 |
| 使用者層 | 你家目錄的 `~/.claude/`、`~/.codex/` | 只有你自己，換電腦就沒了 |

**全組要一致的東西放專案層。** 你個人習慣（例如回覆語氣）放使用者層，不要 commit 進來。

## 三個新手最常踩的坑

1. **在子目錄啟動。** 實測：在 `frontend/` 或 `backend/` 裡啟動 Claude Code，技能讀得到，但**專案根目錄的 hooks 不會生效**。一律在 repo 根目錄啟動。
2. **跑 `/init` 蓋掉專案大腦。** 這個 repo 已經有 `CLAUDE.md` 和 `AGENTS.md` 了。要讓 agent 讀懂專案，請它讀 `AGENTS.md` 和 `docs/`，不要 `/init`。
3. **把規則寫在對話裡。** 對話會被 `/clear`、`/compact` 清掉，檔案不會。規則寫進 `AGENTS.md`，經驗寫進 `docs/LESSONS.md`，規格寫進 `docs/`。

## 常用操作

| 想做 | Claude Code | Codex |
|---|---|---|
| 指定一個檔案給它讀 | `@docs/02-prd.md` | `@docs/02-prd.md` |
| 叫技能 | `/grilling` | `$grilling` |
| 清空對話（換下一張票） | `/clear` | `/clear` 或 `/new` |
| 換人或換工具接手（輪到下一位組員開車） | `/handoff`，新對話貼上它給的那一行 | `$handoff` |
| 先討論計畫、不准動手 | Shift+Tab 切到 plan mode | `/plan` |
| 壓縮對話（同一個階段太長） | `/compact` | `/compact` |
| 看 MCP 連線 | `/mcp` | `/mcp` |
| 不知道下一步 | `/compass` | `$compass` |

## 已知落差

- ⚠️ Codex 的 guard：`.codex/hooks.json` 已登記，但以 `codex exec` 實測時 guard 沒有觸發，擋下 `git add -A` 的是 Codex 自己的 sandbox（它讓 `.git` 唯讀）。互動模式未驗證。
- ⚠️ Codex 的 MCP：`.codex/config.toml` 已寫好同兩個 MCP，但 Codex 只在**信任的專案**載入專案層設定，第一次開啟時要選信任。以 `codex exec` 實測時沒有載入成功，互動模式未驗證。Claude Code 的兩個 MCP 都實測可用。
- Antigravity、Copilot 不認「只准使用者觸發」，`/compass`、`/to-architecture`、`/to-tickets` 可能被 agent 自己啟動。這門課只支援 Claude Code 與 Codex。

## 單元 1 的通過訊號

- [ ] 請 agent 跑 `git add -A`，它被擋下。你說得出是**哪個檔案**擋的、在哪裡登記的
- [ ] 你說得出 `AGENTS.md` 和 `.claude/hooks/` 的差別：哪一個 agent 可以違反、哪一個不行
- [ ] 請 agent 用 playwright 打開任一網頁、回報標題；用 context7 查 Next.js 的文件。兩個都回得出來
