# LeaveBot —— 4 天規格驅動 × AI 開發實戰營

> 上課用的專案。**只有骨架，沒有請假的業務邏輯** —— 那是你要讓 agent 依規格寫出來的部分。
> 講義（每天的課表、Prompt 魔法書、排解檢索表、檢核表）在講師發的 **OneDrive 講義包**，這個 repo 只放你要動手的東西。

支援 **Claude Code** 與 **Codex**，兩個工具讀同一套技能。

## 這個 repo 裡有什麼

| 位置 | 是什麼 | 什麼時候用 |
|---|---|---|
| `LEAVEBOT.md` | 題目與「好日子科技」的請假規章（課堂假設，不是勞動法規） | Day 1 開始前讀完 |
| `templates/` | 需求、架構模板，`AGENTS.md` 範本，TDD hook | Day 1–3 |
| `app/` `tests/` `fixtures/` | 程式骨架、測試、30 句 eval 起始集 | Day 2 之後 |
| `AGENTS.md` / `CLAUDE.md` | 專案大腦：agent 在這裡要守的規則 | Day 2 改寫成你們的版本 |
| `.claude/` `.agents/` `.codex/` | 技能與護欄。**不用動**，打開工具就生效 | 一直都在 |

## 上課會用到的 6 個技能

| Claude Code | Codex | 做什麼 | 哪天 |
|---|---|---|---|
| `/compass` | `$compass` | 不知道下一步用哪個技能時問它 | 隨時 |
| `/grilling` | `$grilling` | 讓 AI 拷問你的需求，逼出沒想到的情況 | Day 1 |
| `/to-architecture` | `$to-architecture` | 從需求產出 `2_architecture.md` | Day 2 |
| `/to-tickets` | `$to-tickets` | 切成垂直切片票，寫進 `issues/` | Day 2 |
| `/tdd` | `$tdd` | 先紅燈、再綠燈，一張票一張票做 | Day 3、自主期 |
| `/code-review` | `$code-review` | 審查改動是否守規範、是否做到票要求的事 | Day 3 |

就這 6 個。課程結束後想要完整的工具鏈（38 個技能），見
[SDD-agent-coding-beginner 的 `progressive-sdd`](https://github.com/Zenobia000/SDD-agent-coding-beginner/tree/progressive-sdd)。

## 開始

**0. 拿到程式碼**：每組 fork 這個 repo，clone 自己的那一份。Windows 先跑 `git config --global core.symlinks true`，否則 Codex 找不到技能。

**1. 建虛擬環境並安裝**（Python 3.11 以上）：

```bash
python3 --version                  # 先確認 ≥ 3.11。太舊的話 pip 可能卡住不報錯，看起來像當機
python3 -m venv .venv
source .venv/bin/activate          # Windows：.venv\Scripts\activate
pip install -e ".[dev]"
```

**2. 確認一切正常：**

```bash
pytest                             # 全部要是綠的
cp .env.example .env
uvicorn app.main:create_app --factory --reload
```

瀏覽器打開 <http://127.0.0.1:8000/health>，看到 `"status":"ok"` 就完成了。<http://127.0.0.1:8000/docs> 是自動產生的 API 文件。

**3. 確認工具接上了**：在這個資料夾打開 Claude Code（`claude`）或 Codex（`codex`），打 `/compass` 或 `$compass`，看得到上面那張技能表就完成。

**還沒動任何東西之前，測試就要是綠的。** 不是綠的，先找講師。

## 接上真的模型

預設 `LLM_PROVIDER=fake`，不呼叫任何模型，結果固定。單元測試**永遠用假的**，不受下面的設定影響。

要讓 LeaveBot 真的解析句子（Day 4 的 eval 需要），改 `.env`：

| 你有的是 | 設定 | 說明 |
|---|---|---|
| **Claude 訂閱**（Pro / Max），或已登入的 Claude Code | `LLM_PROVIDER=claude-cli` | 借用本機的 `claude` 指令，**不用 API key**。工具全部關閉，只做文字轉文字 |
| Claude API key | `LLM_PROVIDER=anthropic`＋`ANTHROPIC_API_KEY=...` | 走 API 計費 |
| 只有 Codex / ChatGPT 訂閱 | 維持 `fake`，Day 4 跟講師的示範機一起跑 eval | 見下方說明 |

`LLM_MODEL` 留空用預設模型；想省額度可以換成較便宜的模型。

**訂閱管的是兩件不同的事**：你用 Claude Code / Codex 寫程式，用的是訂閱；LeaveBot 程式執行時要解析一句話，也需要一個模型。`claude-cli` 讓後者也能用同一個訂閱。

**為什麼沒有 `codex-cli`**：`codex exec` 找不到關掉 shell 工具的選項（⚠️ 以 codex-cli 0.162.1 查過）。拿它當程式裡的模型，一句被注入的請假句子就可能讓它去讀你電腦上的檔案。這門課在教怎麼擋 prompt injection，不會自己開這個洞。

用其他供應商（例如 OpenAI API）：在 `app/llm.py` 照 `LLMClient` 介面寫一個類別，加進 `build_llm`。可以直接請 agent 做 —— 先寫測試，這本身就是 Day 3 的練習。

## 專案大腦

`AGENTS.md`（Codex 讀）與 `CLAUDE.md`（Claude Code 讀，只是指向 `AGENTS.md`）是起點。
Day 2 會用 `templates/agent-rules/` 的範本把它改成你們自己的版本。

## 護欄

`.claude/hooks/` 的兩支 guard 會擋下 agent 做這些事：一次 `git add` 全部檔案、force push、`reset --hard` 到別的 commit、跳過 git hook、把疑似金鑰 commit 進去。被擋的時候，agent 會看到原因並改用安全的做法 —— 這是設計，不是壞掉。

要改 guard 或技能的話，改完跑 `bash scripts/check.sh`，全綠才算接好。

## 授權

技能與 guard hooks 衍生自 [luca-skills](https://github.com/Luca0x5755/luca-skills)（MIT），見 `THIRD-PARTY-NOTICES.md`。
