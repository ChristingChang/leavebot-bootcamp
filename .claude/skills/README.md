# Skills

叫了才載入的流程。規則在 `AGENTS.md`（建議），hook 在 `.claude/hooks/`（做不到）。技能介在中間：你打 `/名字`（Codex 是 `$名字`），它就照那份 `SKILL.md` 走。

總覽在 `course/HARNESS.md`。這份只講每支怎麼走、你實際打什麼。

## 兩種觸發

| 誰能啟動 | 技能 |
| --- | --- |
| 只有你打才跑 | `compass`、`grill-with-docs`、`to-spec`、`to-architecture`、`to-test-plan`、`to-tickets`、`implement`、`handoff` |
| 你打，或 agent 看說明自己接 | `grilling`、`writing-for-agents`、`tdd`、`diagnosing-bugs`、`code-review`、`writing-hooks` |

課程原有 10 支，另有 4 支本專案適配技能；`feasibility` 仍是未安裝的可選提案。`archify` 不在已安裝清單，見文末。

## 兩天怎麼串

D1 寫規格，D2 從零做出能跑的東西。迷路就 `/compass`，它會看 `docs/01` 到 `docs/06`、`docs/LESSONS.md`、`issues/` 缺哪一個，指下一支。

```text
D1
/grilling            → 釐清需求；已有文件時可用 /grill-with-docs
/to-spec             → docs/01-brief.md、02-prd.md、03-srs.md
/to-architecture     → docs/04-sad.md、docs/05-sds.md
/to-test-plan        → docs/06-test-plan.md，含 TC、eval、追溯矩陣
/writing-for-agents  → AGENTS.md 下半「本專案」、docs/LESSONS.md
/to-tickets          → issues/000 … issues/004

D2  每張票之間 /clear
I0 骨架              → /implement，照 course/STACK.md
I1–I3               → /implement，一張票一個 session，行為用 /tdd
紅燈原因不明          → /diagnosing-bugs
合併前               → /code-review
I4 驗模型            → 照測試計畫的門檻跑 eval，沒有專用技能
換人或換工具          → /handoff
一條規則破了會出事    → /writing-hooks
```

D1 的第 1–2 步留在同一個對話；第 4–5 步也是。後面那份要前面的推論原文，不要摘要。D2 每張票自包含，需要的都在 `docs/`、`LESSONS.md` 和那張票裡。同一個階段太長，做完這步再 `/compact`。不要跑 `/init`，會蓋掉專案規則。

規格和產出打架時，以 `docs/` 和 `course/STACK.md` 為準，偏差寫進 `docs/LESSONS.md`。有決定沒定，回到 `/grilling`，不要讓它猜一個默認值。

## 各支

### `/compass` — 路由器

看磁碟上已經有哪些文件，告訴你現在在哪、下一支是誰、該留下哪個檔。它不寫規格、不寫程式。

你打：`/compass`

### `/grilling` — 把決定問清楚

一輪問一層。每一題附它建議的答案，等你回，再問下一層。能自己查的事實它去查，決定留給你。樹問完就停，你確認共識之前不動手。

這門課拿它寫 `docs/01-brief.md` 和 `docs/02-prd.md`（範本在 `course/templates/`）。後面任何規格留白，也回到這裡。

你打：`/grilling`，然後照問題回。定案後用 `/to-spec` 依範本落檔。

### `/grill-with-docs` — 帶著文件訪談

已經有規格時讀現有決定，訪談中不重問，定案後把決定寫回 01–05；偏差才進 LESSONS。你打：`/grill-with-docs`。

### `/to-spec` — 收斂需求

把定案的討論依課程範本寫進 `docs/01-brief.md`、`02-prd.md`、`03-srs.md`，沿用追溯編號。你打：`/to-spec`。

### `/to-architecture` — 兩份設計

讀 PRD、SRS、`course/STACK.md`、`course/LEAVEBOT.md` 和兩份範本。技術棧是固定的，只在裡面設計。

- `docs/04-sad.md`：C4 第 1、2 層、主路徑時序（中間要看得到「驗證模型輸出」）、每個決定是模型、程式還是人、有真正替代方案的 ADR。
- `docs/05-sds.md`：ER、每個 `/api/` 端點和錯誤、畫面對到使用者流程、模型模組和規則模組分開。

剩餘天數、撞期、核准不歸模型。兩份草稿先給你改，再寫檔。寫完應列出沒有落點的 FR / NFR。下一步是 `docs/06-test-plan.md`。

你打：`/to-architecture`（SRS 已經在的時候）。

### `/to-test-plan` — 建立六號測試計畫

依 PRD、SRS、SAD、SDS 與課程範本建立 TC、AI eval 門檻、退出條件與追溯矩陣，輸出 `docs/06-test-plan.md`。參考原作者的 test-blueprint 和 uat-cases，但不另開測試總帳。你打：`/to-test-plan`。

原作者的 **test-blueprint** 決定測試層級、接縫與 CI 時機；**uat-cases** 列出使用者驗收案例及凍結編號。本課程的 `TC-xx` 是 06 裡一則測試案例的編號，可屬於驗收、系統、整合或單元層；D2 的 pytest 用 `@pytest.mark.req` 指回它。**I4 AI eval** 則是另一支以 fixture 逐句呼叫 `POST /api/parse`、統計解析準確率的腳本，不是 TC 的別名。兩者的規劃都記在 06。

通用流程只保留「測試計畫定案例 → 建置時寫並跑測試 → 審查後依案例核對結果」。TC 不需要另一支專屬指令；I4 AI eval 是 LeaveBot 專案的附加門檻，不在通用主幹。`docs/01–06` 在對應技能執行時逐份產生，不會等到最後才生成。`docs/LESSONS.md` 是本 repo 專用的偏差、誤解與踩坑紀錄。

### `/writing-for-agents` — 寫給 agent 讀的文件

本文是寫作標準：步驟和完成條件要能判斷做完沒有、能查到的不要複寫一份、用模型本來就懂的詞當錨點。技能的包裝細節在同目錄 `SKILL-MECHANICS.md`。

這門課拿它寫 `AGENTS.md` 下半「本專案」，以及 `docs/LESSONS.md`。上半原廠規則不要改。

你打：`/writing-for-agents`，並指明要改的是 `AGENTS.md` 下半。

### `/to-tickets` — 切成五張票

六份規格都在之後才打。先把五張的範圍列給你看，你點頭才寫檔。

| 票 | 做完看得到什麼 |
| --- | --- |
| `issues/000-i0-skeleton.md` | `bash dev.sh` 前後端都起來，`GET /api/health`，Ctrl+C 兩個 port 都放 |
| `issues/001-i1-first-slice.md` | 一句話 → 解析 → 預覽 → 送出 → 我的申請。模型在可替換的接縫後面，測試塞假的 |
| `issues/002-i2-rules.md` | 特休餘額、同日人數提醒，由程式算 |
| `issues/003-i3-approval.md` | 主管畫面和狀態轉換 |
| `issues/004-i4-ai-acceptance.md` | 用 `course/fixtures/` 跑 eval，過測試計畫的門檻；注入案例要過 |

I0 之後每張都是一條前後通的路徑，不是「先做完資料庫層」。測試計畫裡每個 TC 正好進一張票。下一步：一張一張 `/implement`，中間 `/clear`。

你打：`/to-tickets`

### `/implement` — 一張票一個 session

讀票與規格，對可測行為使用 `/tdd`，結束前跑完整 pytest、更新追溯矩陣與 LESSONS，並依 `/code-review` 檢查。不自動提交。你打：`/implement issues/001-i1-first-slice.md`。

### `/tdd` — 一張票的紅綠循環

一次只做一個行為。先寫一個會失敗的測試，確認它因為你預期的原因失敗，再寫剛好能過的程式，然後才整理。不要先把整張票的測試一次寫完。

測試打在別的模組會呼叫的接縫上（多半是 `docs/05-sds.md` 的 API），放在 `backend/tests/<layer>/`。每個測試標 `@pytest.mark.req("TC-xx", "...")`。模型只注入假實作，不打真的 API。

票結束前：跑完整 pytest 並貼結果、更新 `docs/06-test-plan.md` 追溯矩陣、有偏差就寫 `docs/LESSONS.md`。

你打：`/clear` 之後 `/tdd`，並指那張票，例如 `issues/001-i1-first-slice.md`。

### `/diagnosing-bugs` — 紅燈原因不明

先有一條幾秒內能穩定變紅的指令，再談原因。分類：產品回歸、時好時壞、環境問題。然後縮小、有已知好版本就 `git bisect`、一次只驗一個假說、用輸出證明、修原因、補一個修之前會紅的測試。探針輸出裡的金鑰先遮掉。

找不到能抓到這個 bug 的接縫時，寫進 `docs/LESSONS.md`，拿回 SAD / SDS 討論，不要當成已經修好。

你打：`/diagnosing-bugs`，附上失敗的指令和輸出。

### `/code-review` — 合併前看 diff

你要給一個定點（SHA、分支、tag）。沒給它會問，不會自己猜。兩條線分開看：有沒有守 `AGENTS.md` 和 `course/STACK.md`，有沒有做到那張票的 Done when。票上的 TC 要用 `grep` 對 `@pytest.mark.req`，矩陣上的 ✅ 只是宣稱。

報告分成必須改和判斷題。某一軸沒問題就直說。

你打：`/code-review main`（或你的定點）。

### `/handoff` — 換人、換工具、換目錄

寫一份給下一個全新對話的交接，放在系統暫存目錄，不進這個 repo。內容是進度、已經做的決定和為什麼、下一步、已知的坑、建議接著叫哪些技能。規格和票用路徑指過去，不複寫。金鑰抹掉。

它結束這一輪。你開新對話，貼它給的那一行。同一個對話要變短，用 `/compact`。

你打：`/handoff 下一輪做 I2 的規則票`

### `/writing-hooks` — 把紅線變成做不到

品味和順序留在文件。破一次就要花一天收拾，或會洩密、會毀資料，才寫成 hook，用 exit 2 擋。理由寫 stderr，告訴它改做什麼。平時安靜，診斷寫日誌。每支 hook 要有對得上允許/擋下的測試。

這個 repo 已經有 `guard-git.sh` 和 `guard-secrets.sh`，登記在 `.claude/settings.json`。課用的「結束前測試要綠」範本在 `course/templates/hooks/`。

你打：`/writing-hooks`，並講哪條規則要擋、在工具執行前還是結束前。

### `archify` — 課表外的畫圖工具

本 repo 的 `.claude/skills/` 沒有 `archify/SKILL.md`，所以它不是目前可呼叫的專案技能。課程 SAD / SDS 的 Mermaid 圖走 `/to-architecture`。
