# 000｜骨架：首頁能讀到 /api/health

> 狀態：待實作｜估計：小（約 20 分鐘，13:30–13:50）｜建立：2026-10-28｜依賴：無｜阻塞：`issues/001-submit-leave.md`

## 成果

在 repo 根目錄可以安裝、啟動並測試一個空白的 FastAPI 服務：
- 首頁以 `fetch('/api/health')` 顯示連線結果（例如「已連線」）。
- `.venv/bin/python -m pytest` 能跑，health 測試通過。

**不寫任何請假邏輯**：不建資料庫、`leave_rules`、`db`、`api` 的業務路由，也不做表單。

## 要讀的規格

- `course/01-上課/04-STACK.md`：「骨架票 000 的要求」第 1～5 點、「安裝與執行」。
- `docs/05-sds.md`：API-01 `GET /api/health`、`main.py` 的模組接縫、「路由登記順序」。
- `AGENTS.md`：「技術邊界」與「本專案決策」。

## 範圍

1. 根目錄的 `pyproject.toml`：
   - 套件白名單 `fastapi`、`uvicorn`、`httpx`；`[dev]` 加 `pytest`；`requires-python = ">=3.12"`。
   - `package-dir = {"" = "backend"}`、`[tool.setuptools.packages.find] where = ["backend"]`，並包含靜態檔 package data。
   - pytest 設定：`testpaths = ["backend/tests"]`、`pythonpath = ["backend"]`、`addopts = "--import-mode=importlib"`，並註冊 `req` marker。
2. `backend/app/__init__.py`、`backend/app/main.py`：
   - 提供 `create_app() -> FastAPI` 與模組層級的 `app = create_app()`。
   - 提供 `GET /api/health`，回傳 `200 {"status": "ok"}`。
   - 先登記所有 `/api` 路由，最後才掛載靜態目錄 `/`。
3. `backend/app/static/` 下的 `index.html`、`app.js`、`style.css`：首頁呼叫 `/api/health` 並顯示結果；連線失敗時顯示「無法連線」。
4. `backend/tests/` 下一個 health 測試。

## 骨架檢查（本票沒有業務 TC；TC-01～TC-12 全部屬於 001）

- [ ] 安裝成功：`.venv/bin/python -m pip install -c course/01-上課/05-constraints.txt -e ".[dev]"`。這是 macOS 第一次安裝，要把結果記下來。
- [ ] `.venv/bin/python -m pytest` 通過，至少有 1 個 health 測試，斷言 `200` 且本文為 `{"status": "ok"}`。
- [ ] 啟動 `.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload` 後：
  - 開 `http://127.0.0.1:8000/`，畫面顯示連線結果。
  - `http://127.0.0.1:8000/api/health` 回傳 JSON，沒有被靜態頁攔截。
- [ ] Ctrl+C 停止後，可以再次啟動。
- [ ] 沒有產生 `backend/data/leavebot.db`，也沒有加入白名單以外的套件。
- [ ] `git status` 只出現本票的檔案。

## 建置前提

- repo 根目錄已有 `.venv`（Python 3.12.14）。系統預設的 `python3` 是 3.9.6，**不可使用**。
- pip 安裝需要網路。

## 完成時回報

- 貼上 pytest 的實際輸出。
- 回報首頁網址與畫面結果。
- 回報實際安裝成功的套件版本。
- 若有偏差，記進 `docs/LESSONS.md`。
- 不 commit。完成後停止，等小組驗收。
