# HARNESS —— agent 的設定檔各管什麼

> D1 第一個單元用這個 repo 當解剖標本。Claude Code 和 Codex 不是只有「對話框」：
> 它們每次啟動都會讀一組檔案，決定**要守什麼規則、會什麼技能、哪些動作做不到**。
> 後面你要改規則、裝 hook、被 guard 擋下來，都要先知道是哪個檔案在作用。

## 一張圖

```text
leavebot-bootcamp/                     ← 一律在這裡（repo 根目錄）啟動 claude / codex
├── AGENTS.md                          ← 規則（專案大腦）。Codex 讀這份
├── CLAUDE.md                          ← 只有一行 @AGENTS.md。Claude Code 讀這份，再被導到 AGENTS.md
├── .claude/
│   ├── settings.json                  ← Claude Code 的專案設定：登記 hooks
│   ├── hooks/guard-git.sh             ← 擋危險的 git 指令
│   ├── hooks/guard-secrets.sh         ← 擋把疑似金鑰 commit 進去
│   └── skills/<名字>/SKILL.md         ← 技能。Claude Code 打 /名字
│       └── agents/openai.yaml         ← 給 Codex 的「只准使用者觸發」設定
├── .agents/skills → ../.claude/skills ← symlink，Codex 從這裡讀同一份技能，打 $名字
├── .codex/hooks.json                  ← Codex 登記同一對 guard
└── frontend/AGENTS.md                 ← I0 時 create-next-app 產生，提醒 agent 新版 Next.js 的寫法
```

## 每個檔案管什麼

| 檔案 | 誰讀 | 管什麼 | 改它的時機 |
|---|---|---|---|
| `AGENTS.md` | Codex；Claude Code 經由 `CLAUDE.md` | 規則：規格在哪、怎麼跑測試、紅線 | D1-8 用 `templates/agent-rules/` 改寫 |
| `CLAUDE.md` | Claude Code | 只做指向，**不要在這裡加規則**，兩份要同步維護不值得 | 不改 |
| `.claude/settings.json` | Claude Code | 哪些 hook 在什麼時機跑 | 加 hook 時，**併進去，不要整份覆蓋** |
| `.claude/hooks/*.sh` | 被 hook 呼叫 | 真的擋下動作：不是請 agent 不要做，是讓它做不到 | 很少改；改完跑 `bash scripts/check.sh` |
| `.claude/skills/*/SKILL.md` | 兩者 | 一段固定流程（拷問、拆票、TDD…），用 `/名字` 或 `$名字` 叫出來 | 想改流程時 |
| `.codex/hooks.json` | Codex | 同一對 guard 的 Codex 版登記 | 和 `settings.json` 一起改 |

## 規則 vs 技能 vs hook

| | 是什麼 | 強度 | 例 |
|---|---|---|---|
| **規則**（`AGENTS.md`） | 每次對話都帶著的文字 | agent 大部分時候會遵守，**不是每一次** | 「說完成前要貼測試結果」 |
| **技能**（`skills/`） | 叫了才載入的流程 | 叫了就照流程走 | `/tdd`：先紅燈再綠燈 |
| **hook**（`hooks/`） | 工具動作前後自動跑的腳本 | **做不到**，agent 繞不過去 | `git add -A` 被擋下 |

判斷口訣：**違反了會有人受傷的，降成 hook；其他寫成規則。**

## 使用者層 vs 專案層

| | 位置 | 誰看得到 |
|---|---|---|
| 專案層 | repo 裡的 `AGENTS.md`、`.claude/` | 所有 clone 這個 repo 的人，跟著版控走 |
| 使用者層 | 你家目錄的 `~/.claude/`、`~/.codex/` | 只有你自己，換電腦就沒了 |

**全組要一致的東西放專案層。** 你個人習慣（例如回覆語氣）放使用者層，不要 commit 進來。

## 三個新手最常踩的坑

1. **在子目錄啟動。** 實測：在 `frontend/` 或 `backend/` 裡啟動 Claude Code，技能讀得到，但**專案根目錄的 hooks 不會生效**。一律在 repo 根目錄啟動。
2. **跑 `/init` 蓋掉專案大腦。** 這個 repo 已經有 `CLAUDE.md` 和 `AGENTS.md` 了（Claude Code 的 `/init` 產生前者、Codex 的產生後者）。要讓 agent 讀懂專案，請它讀 `AGENTS.md` 和 `docs/`，不要 `/init`。
3. **把規則寫在對話裡。** 對話會被 `/clear`、`/compact` 清掉，檔案不會。規則一律寫進 `AGENTS.md`，規格一律寫進 `docs/`。

## 常用操作

| 想做 | Claude Code | Codex |
|---|---|---|
| 指定一個檔案給它讀 | `@docs/02-prd.md` | `@docs/02-prd.md` |
| 叫技能 | `/grilling` | `$grilling` |
| 清空對話（換下一張票） | `/clear` | `/clear` 或 `/new` |
| 先討論計畫、不准動手 | Shift+Tab 切到 plan mode | `/plan` |
| 壓縮對話（同一個階段太長） | `/compact` | `/compact` |
| 不知道下一步 | `/compass` | `$compass` |

## 已知落差

- ⚠️ Codex 的 guard：`.codex/hooks.json` 已登記，但以 `codex exec` 實測時 guard 沒有觸發，擋下 `git add -A` 的是 Codex 自己的 sandbox（它讓 `.git` 唯讀）。互動模式未驗證。
- Antigravity、Copilot 不認「只准使用者觸發」，`/compass`、`/to-architecture`、`/to-tickets` 可能被 agent 自己啟動。這門課只支援 Claude Code 與 Codex。

## 單元 1 的通過訊號

- [ ] 請 agent 跑 `git add -A`，它被擋下。你說得出是**哪個檔案**擋的、在哪裡登記的
- [ ] 你說得出 `AGENTS.md` 和 `.claude/hooks/` 的差別：哪一個 agent 可以違反、哪一個不行
