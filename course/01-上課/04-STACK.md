# STACK — D2 固定技術棧

全班只有一個 HTTP 服務。Agent 從空白專案生成骨架，選型由本檔固定，產品細節由已確認的 SDS 決定。

| 層 | 選擇 |
|---|---|
| 前端 | HTML、CSS、原生 JavaScript，`backend/app/static/` |
| 後端 | Python 3.12、FastAPI、uvicorn |
| 資料 | 標準庫 sqlite3；開發預設 `backend/data/leavebot.db` |
| 測試 | pytest、httpx／FastAPI TestClient |
| 畫圖 | 隨 repo 提供的 Archify；Node 最低 18；無法執行時用 Mermaid |

主線不建立 `frontend/`、不使用 Next.js、不需要 `dev.sh` 或模型 API key。Node 只給畫圖與已設定的 MCP 使用。

## 骨架票 000 的要求

1. 在根目錄生成 `pyproject.toml`。套件白名單為 `fastapi`、`uvicorn`、`httpx`；`[dev]` 加 `pytest`。`requires-python = ">=3.12"`。將**彩排或本機實際驗證過的相容版本**記在交付紀錄，不聲稱未跑過的版本已驗證。
2. setuptools 使用明確的 package discovery：`package-dir = {"" = "backend"}`、`[tool.setuptools.packages.find] where = ["backend"]`，包含靜態頁 package data。避免把 `course/`、`issues/` 當 Python package。
3. pytest 設定：`testpaths = ["backend/tests"]`、`pythonpath = ["backend"]`、`addopts = "--import-mode=importlib"`，註冊 `req` marker。
4. 生成 `backend/app/__init__.py`、`main.py` 與 `static/index.html`、`app.js`、`style.css`；`main.py` 提供 `app = FastAPI()`、`GET /api/health`。所有 `/api` 路由先登記，最後掛載靜態目錄 `/`。
5. 首頁以 `fetch('/api/health')` 顯示連線結果；加入一個 health 測試。這張票不做請假功能。

## 安裝與執行（repo 根目錄）

macOS / Linux：
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -c course/01-上課/05-constraints.txt -e ".[dev]"
.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload
.venv/bin/python -m pytest
```

Windows PowerShell（啟動與測試分別在兩個終端機）：
```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -c course/01-上課/05-constraints.txt -e ".[dev]"
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
.venv\Scripts\python.exe -m pytest
```

瀏覽器開 `http://127.0.0.1:8000/`。port 被占用加 `--port 8001`。Ctrl+C 停止後重啟一次，確認能再開。

## 表單票 001 的邊界

- API 都在 `/api/`，前端用相對路徑；同來源，不開 CORS。具體端點、欄位與錯誤碼由 SDS 指定。
- 驗證放後端。天數由程式以包含首尾的日期範圍計算，扣掉週末；半天限單日工作日。客戶端不決定天數與狀態。
- 資料庫路徑從 `LEAVEBOT_DB` 讀；測試每次使用暫存資料庫，初始化與關閉連線要可重複執行。
- 若規則使用「今天」，從 `LEAVEBOT_TODAY` 讀，課堂固定 `2026-10-12`；測試明確注入。開發可未設時讀真實日期，但要在畫面／紀錄說明。
- SQL 使用參數，理由以 `textContent` 呈現。拒絕的輸入不存檔；前端顯示可理解的錯誤。
- 主線測試以 `backend/tests/acceptance/` 與 `backend/tests/unit/` 為主；測試層級依實際接縫選擇，不硬湊四層。

## C4/C5 才適用

先建立挑戰票與更新規格，再加入 Anthropic SDK 選用依賴及必要的環境載入方式。金鑰只存在環境或未追蹤 `.env`，模型名稱明確設定並記錄實測版本；不把 Agent CLI 當後端。
模型輸出是草稿，經 schema 與程式規則驗證，使用者確認後才送出。一般測試使用 deterministic fake，真正模型 eval 分開執行。解析合約與 fixture 的 `today`、六種假別、比對規則見 [fixtures/README.md](../02-補充/fixtures/README.md)；規劃寫入 06 的選用區。

## 已驗證的套件組合

`course/01-上課/05-constraints.txt`記錄2026-10-25在Windows／Python3.12.9實際通過20項參考測試的版本。安裝時以 `-c` 套用；它不是新的套件白名單。其他平台與Agent仍須課前試跑。
