# LeaveBot —— 2 天 SDD agentic coding 實戰營

> **D1 寫規格，D2 從 0 做出 app。** 題目是「一句話請假」：員工打一句話，AI 轉成假單，規則由程式檢查，主管核准。
> 這個 repo 裡**沒有 app 程式碼** —— 那是 D2 你們依自己的規格，讓 agent 一個疊代一個疊代生出來的。
> 講義（課表、Prompt 魔法書、排解檢索表、檢核表）在講師發的 **OneDrive 講義包**。

支援 **Claude Code** 與 **Codex**，兩個工具讀同一套技能。

## 這個 repo 裡有什麼

| 位置 | 是什麼 | 什麼時候用 |
|---|---|---|
| `LEAVEBOT.md` | 題目、公司規章（課堂假設）、MVP 範圍 | 課前讀完 |
| `HARNESS.md` | agent 的設定檔各管什麼 | D1 第一個單元 |
| `templates/` | 六份規格文件模板、追溯規則、`AGENTS.md` 範本、TDD hook | D1 |
| `examples/it-asset/` | 另一個題目寫好的六份文件，看「寫完長什麼樣」 | D1 |
| `STACK.md` | 固定的技術棧（Next.js＋FastAPI）、I0 骨架怎麼生 | D2 |
| `kit/` | LLM client（假的、Claude 訂閱、Claude API），**app 只能透過它呼叫模型** | D2 |
| `scripts/` | `dev.sh` 起前後端、`trace.py` 追溯檢查、`run_eval.py` 量 AI 準確率 | D2 |
| `fixtures/` | 30 句 eval 起始集 | D1 寫測試計畫、D2 I4 |
| `AGENTS.md` / `CLAUDE.md` | 專案大腦：agent 在這裡要守的規則 | D1 改寫成你們的版本 |
| `.claude/` `.agents/` `.codex/` | 技能與護欄。**不用動**，打開工具就生效 | 一直都在 |

你們會產出的：`docs/`（六份規格）、`issues/`（疊代票）、`backend/`、`frontend/`。

## 上課會用到的 6 個技能

| Claude Code | Codex | 做什麼 | 什麼時候 |
|---|---|---|---|
| `/compass` | `$compass` | 不知道下一步用哪個技能時問它 | 隨時 |
| `/grilling` | `$grilling` | 讓 AI 拷問你，產出 Brief 與 PRD | D1 |
| `/to-architecture` | `$to-architecture` | 產出 SAD 與 SDS | D1 |
| `/to-tickets` | `$to-tickets` | 切成 I0–I4 疊代票，寫進 `issues/` | D1 |
| `/tdd` | `$tdd` | 從票上的測試案例開始，先紅燈再綠燈 | D2 |
| `/code-review` | `$code-review` | 審查改動是否守規範、是否做到票要求的事 | D2 |

就這 6 個。課程結束後想要完整的工具鏈（38 個技能），見
模板 repo [`agent-skills-starter`](https://github.com/Zenobia000/agent-skills-starter)，按 Use this template 就能開一個新專案。

## 開始（課前完成）

**0. 拿到程式碼**：每組 fork 這個 repo，clone 自己的那一份。Windows 先跑 `git config --global core.symlinks true`，否則 Codex 找不到技能。

**1. Python**（3.11 以上）：

```bash
python3 --version                  # 先確認 ≥ 3.11。太舊的話 pip 可能卡住不報錯，看起來像當機
python3 -m venv .venv
source .venv/bin/activate          # Windows：.venv\Scripts\activate
pip install -e ".[dev]"
pytest                             # 全部要是綠的
```

**2. Node**：`node --version`。講師實測的是 Node 24；更舊的版本能不能跑 Next.js 16 ⚠️ 未驗證，課前請裝 24。D2 的 I0 會用 `STACK.md` 裡固定版本的 `create-next-app` 建前端。

**3. 確認工具接上了**：在 repo 根目錄打開 Claude Code（`claude`）或 Codex（`codex`），打 `/compass` 或 `$compass`，看得到上面那張技能表就完成。**一律在 repo 根目錄啟動**，在子目錄啟動 hooks 不會生效（見 `HARNESS.md`）。

**還沒動任何東西之前，`pytest` 就要是綠的。** 不是綠的，先找講師。

## 接上真的模型

預設 `LLM_PROVIDER=fake`，不呼叫任何模型，結果固定。單元測試**永遠用假的**，不受下面的設定影響。

要讓 LeaveBot 真的解析句子（D2 的 I4 跑 eval 需要），先 `cp .env.example .env`，再改：

| 你有的是 | 設定 | 說明 |
|---|---|---|
| **Claude 訂閱**（Pro / Max），或已登入的 Claude Code | `LLM_PROVIDER=claude-cli` | 借用本機的 `claude` 指令，**不用 API key**。工具全部關閉，只做文字轉文字 |
| Claude API key | `LLM_PROVIDER=anthropic`＋`ANTHROPIC_API_KEY=...` | 走 API 計費 |
| 只有 Codex / ChatGPT 訂閱 | 維持 `fake`，I4 跟講師的示範機一起跑 eval | 見下方說明 |

`LLM_MODEL` 留空用預設模型；想省額度可以換成較便宜的模型。

**訂閱管的是兩件不同的事**：你用 Claude Code / Codex 寫程式，用的是訂閱；LeaveBot 程式執行時要解析一句話，也需要一個模型。`claude-cli` 讓後者也能用同一個訂閱。

**為什麼沒有 `codex-cli`**：`codex exec` 找不到關掉 shell 工具的選項（⚠️ 以 codex-cli 0.162.1 查過）。拿它當程式裡的模型，一句被注入的請假句子就可能讓它去讀你電腦上的檔案。這門課在教怎麼擋 prompt injection，不會自己開這個洞。

用其他供應商（例如 OpenAI API）：在 `kit/llm.py` 照 `LLMClient` 介面寫一個類別，加進 `build_llm`。先問講師 —— `kit/` 是安全關鍵的程式，改了要補測試。

## 專案大腦

`AGENTS.md`（Codex 讀）與 `CLAUDE.md`（Claude Code 讀，只是指向 `AGENTS.md`）是起點。
D1 最後一個單元會用 `templates/agent-rules/` 的範本把它改成你們自己的版本。

## 護欄

`.claude/hooks/` 的兩支 guard 會擋下 agent 做這些事：一次 `git add` 全部檔案、force push、`reset --hard` 到別的 commit、跳過 git hook、把疑似金鑰 commit 進去。被擋的時候，agent 會看到原因並改用安全的做法 —— 這是設計，不是壞掉。

要改 guard 或技能的話，改完跑 `bash scripts/check.sh`，全綠才算接好。

## 授權

技能與 guard hooks 衍生自 [luca-skills](https://github.com/Luca0x5755/luca-skills)（MIT），見 `THIRD-PARTY-NOTICES.md`。
