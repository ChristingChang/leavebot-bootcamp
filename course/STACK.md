# STACK —— 技術棧與邊界（固定，不要讓 agent 換）

> 2 天要從 0 做出全端加 AI 的 app，**選型的時間省下來給規格和測試**。
> 這一頁是規格，不是程式碼：這個 repo 裡沒有任何預先寫好的程式，`backend/`、`frontend/`、套件設定、啟動腳本都由你們的 agent 照這一頁生成。
> 生成的結果和這一頁不一樣時，**以這一頁為準**，把差異記進 `docs/LESSONS.md`。
> 想在這些邊界之外做選擇，寫進 `docs/04-sad.md` 的 ADR，並先問講師。

## 固定的部分

| 層 | 用什麼 | 位置 |
|---|---|---|
| 前端 | Next.js 16.4.2（App Router、TypeScript、Tailwind） | `frontend/` |
| 後端 | Python 3.12、FastAPI、標準庫 `sqlite3`、pytest | `backend/` |
| 資料庫 | SQLite 單一檔案 `backend/data/leavebot.db`（不進版控） | — |
| LLM | Anthropic Python SDK，**用你自己的 API key** | `backend/` 裡依 SDS 放 |

版本是講師在 2026-10-16 實測過的組合（Node 24、Python 3.12）。換版本前先問 —— 版本漂移是兩天課最常見的卡關原因。

## 紅線

- **模型一律透過 Anthropic API 呼叫。不准**用 `claude -p`、`codex exec` 這類 agent CLI 當後端 —— 它們帶著執行指令的工具，被注入攻擊時能在你的電腦上動手。API 呼叫沒有工具，最壞只是答錯。
- API key 只放 `.env`（變數 `ANTHROPIC_API_KEY`），不准寫進任何其他檔案。
- 測試**不准呼叫真的模型**。業務程式只依賴一個 `complete(system, user) -> str` 的介面，測試注入假的實作。
- 不開 CORS、不在前端寫死後端位址（見 I0 第 2 步）。

## I0：骨架怎麼生（D2 第一個疊代）

**1. 前端**：在 repo 根目錄跑這一行。版本寫死，`--disable-git` 一定要加（不然它會在 `frontend/` 裡再開一個 git repo）：

```bash
npx --yes create-next-app@16.4.2 frontend --ts --app --eslint --tailwind --no-src-dir --import-alias "@/*" --use-npm --disable-git --yes
```

它會在 `frontend/` 產生一份 `AGENTS.md`，提醒 agent 這版 Next.js 的 API 跟它記得的不一樣。**留著，不要刪。** 不確定新版寫法時，請 agent 用 context7 查（見 `HARNESS.md`）。

**2. 前端轉 API 給後端**：在 `frontend/next.config.ts` 的設定物件裡加上 `rewrites`：

```ts
async rewrites() {
  return [
    {
      source: "/api/:path*",
      destination: `${process.env.BACKEND_URL ?? "http://127.0.0.1:8000"}/api/:path*`,
    },
  ];
},
```

瀏覽器只連前端，前端程式一律呼叫相對路徑 `/api/...`。

**3. 套件設定 `pyproject.toml`**（根目錄）。讓 agent 生成，必須符合：

| 項目 | 規定 |
|---|---|
| `requires-python` | `>=3.11` |
| `dependencies` | **只有** `fastapi>=0.115`、`uvicorn>=0.30`、`anthropic>=1.0`、`httpx>=0.27`。這就是白名單 |
| 開發用 | `pytest>=8.0` |
| pytest | `testpaths = ["backend/tests"]`、`pythonpath = ["backend"]`、`addopts = "--import-mode=importlib"`（不同層級有同名測試檔也不會撞名）、登記 marker `req` |

裝法：`python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`。之後一律用 `.venv/bin/python`、`.venv/bin/pytest` —— agent 的 shell 不會自動啟用 venv。

**4. 後端**：讓 agent 依 `docs/05-sds.md` 生成，結構固定成：

```text
backend/
├── app/
│   ├── main.py        ← 一定要有 `app = FastAPI()`；所有路由都在 /api 底下
│   └── …              ← 其他模組依 SDS 拆
├── data/              ← SQLite 檔，不進版控
└── tests/
    ├── acceptance/    ← 驗 PRD 的 AC（打 API）
    ├── system/        ← 驗 SRS 的 FR / NFR
    ├── integration/   ← 驗 SAD 的元件邊界
    └── unit/          ← 驗 SDS 的模組
```

**5. 啟動腳本 `dev.sh`**（根目錄）。讓 agent 生成，必須做到：

- 一個指令同時起後端（uvicorn，預設 :8000）與前端（`next dev`，預設 :3000），port 可用 `BACKEND_PORT`、`FRONTEND_PORT` 換
- 把 `BACKEND_URL` 傳給前端，把 `LEAVEBOT_TODAY` 預設成 `2026-10-12`
- port 被佔用時，印出換 port 的指令再結束
- **Ctrl+C 之後兩個 port 都要釋放**。彩排時直接 kill 子程序，`npx` 底下的 next-server 被留下來繼續佔 port；要用 process group（例如 `setsid`）整組關掉

**6. 驗收 I0**：`bash dev.sh` 起得來，瀏覽器開前端，頁面經 proxy 讀到 `GET /api/health`；Ctrl+C 後再跑一次也起得來。

## 呼叫模型（I1）

- 從 `.env` 讀 `ANTHROPIC_API_KEY` 與 `LLM_MODEL`。模型選哪個、為什麼，寫進 SAD 的 ADR（解析一句話用小模型通常就夠，eval 會告訴你）。
- 設逾時上限，數字依 Test Plan（用整份 eval 集量，不要拿一句話量）。
- 模型的輸出**必須通過格式驗證**才能往下走；剩餘天數、撞期、核准一律由程式碼或人決定，不採用模型給的任何數字或狀態。
- SDK 的用法不確定時，請 agent 用 context7 查官方文件，不要憑記憶寫。

## 今天是幾號：固定成課程日期

課程情境、eval 集與公司規章的「今天」都是 **2026-10-12（週一）**。後端任何用到「今天」的地方（送出期限、逾期、解析時傳給模型的日期），**一律從環境變數 `LEAVEBOT_TODAY` 讀**，沒設才用真實日期。

不這樣做的話：彩排時一張 10/23 的假單，過了 10/22 18:00 就被送出期限擋下，demo 走不通。測試也一樣，不准依賴真實時鐘。

## 唯一替你定好的 API：解析合約

```text
POST /api/parse
  request:  {"sentence": "下週三下午看牙醫", "today": "2026-10-12"}
  response: {"requests": [{"start_date", "end_date", "period", "leave_type", "days", …}], "clarify": false}
```

欄位定義同 `fixtures/README.md`。這支 API 的形狀為了讓每一組用**同一把尺**量準確率而固定（I4 的 eval 比對規則見 `templates/06-test-plan.md`），**其他所有 API 由你們的 SDS 決定**。

## 套件

- 後端：只能用上面白名單裡的。要加，先問。
- 前端：只能用 create-next-app 裝好的。要加（UI 套件、狀態管理、表單庫……），先問。

## 不做

登入（員工用下拉選單切換身分）、通知、部署、Docker、多團隊、ORM、前端自動化測試。
這些都是真實系統需要的東西，**但不是這兩天要練的東西**。想做的話寫進 `docs/01-brief.md` 的 non-goal，那也是一種決策。

## 測試

在 repo 根目錄跑 `.venv/bin/pytest`。每個測試標註它實作哪個測試案例、驗哪條需求：

```python
@pytest.mark.req("TC-03", "AC-01.1")
def test_employee_sees_preview_after_submitting_a_sentence(client): ...
```

每做完一張票，更新 `docs/06-test-plan.md` 的追溯矩陣：哪個 TC 由哪個測試檔驗過。規則見 `templates/TRACEABILITY.md`。
