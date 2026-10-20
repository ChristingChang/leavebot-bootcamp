# STACK —— 技術棧與邊界（固定，不要讓 agent 換）

> 2 天要從 0 做出全端加 AI 的 app，**選型的時間省下來給規格和測試**。
> 這一頁就是 agent 的邊界：`AGENTS.md` 的紅線要求它照這裡做。
> 想在這些邊界之外做選擇，寫進 `docs/04-sad.md` 的 ADR，並先問講師。

## 固定的部分

| 層 | 用什麼 | 位置 |
|---|---|---|
| 前端 | Next.js 16.4.2（App Router、TypeScript、Tailwind） | `frontend/` |
| 後端 | FastAPI＋Python 標準庫 `sqlite3`，pytest 測試 | `backend/` |
| 資料庫 | SQLite 單一檔案 `backend/data/leavebot.db`（已在 `.gitignore`） | — |
| LLM | **只能**透過 `kit/llm.py`：`build_llm(load_llm_settings())` | `kit/` |
| 一起啟動 | `bash scripts/dev.sh`（前端 :3000、後端 :8000，可用環境變數換） | `scripts/` |

版本是講師在 2026-10-16 實測過的組合（Node 24、Python 3.12）。換版本前先問 —— 版本漂移是兩天課最常見的卡關原因。

## I0：骨架怎麼生（D2 第一個疊代）

**1. 前端**：在 repo 根目錄跑這一行。版本寫死，`--disable-git` 一定要加（不然它會在 `frontend/` 裡再開一個 git repo）：

```bash
npx --yes create-next-app@16.4.2 frontend --ts --app --eslint --tailwind --no-src-dir --import-alias "@/*" --use-npm --disable-git --yes
```

它會在 `frontend/` 產生一份 `AGENTS.md`，提醒 agent 這版 Next.js 的 API 跟它記得的不一樣、要先讀 `node_modules/next/dist/docs/`。**留著，不要刪。**

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

瀏覽器只連前端，前端程式一律呼叫相對路徑 `/api/...`。**不要**在後端開 CORS、**不要**在前端寫死 `localhost:8000`。

**3. 後端**：讓 agent 依 `docs/05-sds.md` 生成，結構固定成：

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

**4. 驗收 I0**：`bash scripts/dev.sh` 起得來，瀏覽器開前端，頁面經 proxy 讀到 `GET /api/health`。

## 今天是幾號：固定成課程日期

課程情境、eval 集與公司規章的「今天」都是 **2026-10-12（週一）**。後端任何用到「今天」的地方（送出期限、逾期、解析時傳給模型的日期），**一律從環境變數 `LEAVEBOT_TODAY` 讀**，沒設才用真實日期。`scripts/dev.sh` 預設會設成 `2026-10-12`。

不這樣做的話：彩排時一張 10/23 的假單，過了 10/22 18:00 就被送出期限擋下，demo 走不通。測試也一樣，不准依賴真實時鐘。

## 唯一替你定好的 API：解析合約

```text
POST /api/parse
  request:  {"sentence": "下週三下午看牙醫", "today": "2026-10-12"}
  response: {"requests": [{"start_date", "end_date", "period", "leave_type", "days", …}], "clarify": false}
```

欄位定義同 `fixtures/README.md`。這支 API 的形狀為了讓 `scripts/run_eval.py` 能幫每一組量準確率而固定，**其他所有 API 由你們的 SDS 決定**。

## 套件

- 後端：只能用 `pyproject.toml` 的 `dependencies` 裡有的。要加，先問。
- 前端：只能用 create-next-app 裝好的。要加（UI 套件、狀態管理、表單庫……），先問。

## 不做

登入（員工用下拉選單切換身分）、通知、部署、Docker、多團隊、ORM、前端自動化測試。
這些都是真實系統需要的東西，**但不是這兩天要練的東西**。想做的話寫進 `docs/01-brief.md` 的 non-goal，那也是一種決策。

## 測試

在 repo 根目錄跑 `pytest`。每個測試標註它實作哪個測試案例、驗哪條需求：

```python
@pytest.mark.req("TC-03", "AC-01.1")
def test_employee_sees_preview_after_submitting_a_sentence(client): ...
```

`.venv/bin/python scripts/trace.py` 會檢查需求 → 測試案例 → 測試的追溯有沒有斷掉。規則見 `templates/TRACEABILITY.md`。
