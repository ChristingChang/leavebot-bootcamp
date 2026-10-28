# LESSONS —— LeaveBot 請假系統的經驗紀錄

> 這份是專案自己的記憶：AI 誤解了什麼、產出和講義不一樣時怎麼對齊、踩過什麼坑。
> agent 在每張票結束時補充；人負責刪掉不重要的、把重複出現的升級成 `AGENTS.md`「本專案決策」的規則。

## 目錄

- [偏差紀錄](#偏差紀錄)
- [規格誤解](#規格誤解)
- [踩過的坑](#踩過的坑)
- [已升級成規則](#已升級成規則)

## 偏差紀錄

### 2026-10-28／卡 B｜PRD 沒有透過指定的 `/to-spec` 技能產出

- 講義說：卡 B 使用 `/to-spec` 技能；實際做了：agent 沒有呼叫技能，而是在對話裡依卡片與模板直接寫出 `docs/02-prd.md`。
- 發現方式：agent 在回報時主動說明。
- 對齊方式與證據：卡 C 起改由使用者以 `/to-spec` 呼叫技能。PRD 的內容依模板 Gate 審過，沒有重寫。
- 後續文件：無。

### 2026-10-28／票 001 WBS 3.B.1｜TC-09 員工隔離一跑就綠

- 講義說：每個 TC 先看到符合預期原因的紅燈，再轉綠；實際：`test_tc09_each_employee_sees_only_own_leaves` 第一次執行就通過。
- 原因：2.1 依 PM 指示先寫了 `db.list_leaves` 的 `WHERE employee_id = ?`（TC-01 只有 E001 的資料，其實用不到這個條件）。
- 對齊方式與證據：暫時把條件改成 `WHERE ? IS NOT NULL`，測試因預期原因變紅：`AssertionError: assert ['E001', 'E002'] == ['E001']`（E001 看到 E002 的假單）。放回原條件後轉綠。同一個 TC 的 E999 → 404 案例則自然先紅（`assert 200 == 404`）。
- 後續文件：無。之後若「最少程式」裡先寫了某個 TC 的條件，就預期那個 TC 會一跑就綠，要照這個做法驗證。

### 2026-10-28／票 001 WBS 3.A.4｜TC-10 有 5 個案例一跑就綠

- 講義說：每個 TC 先看到符合預期原因的紅燈，再轉綠；實際：TC-10 的 201 字拒絕案例（單元 2 條）自然先紅，但下列案例第一次就通過。
- 原因與驗證（暫時改程式，看到紅燈後改回；最後全套 38 passed）：
  - 單元「頭尾空白不計」「只有全形空白」：2.1 的 `normalize_reason` 已經 `strip()`。拿掉 `strip()` 後兩條變紅：`assert '  aaaa…　　' == 'aaaa…'`、`assert '　　　' == ''`。
  - 單元「200 個 `a`」「200 個『假』」：沒有上限時本來就合法。實作上限後，把 `>` 改成 `>=`（差一的錯誤），三條 200 字案例變紅：`assert [{'field': 'reason', … '理由最多 200 字'}] == []`。
  - API「201 個 `a` 不存檔」：寫測試時上限已實作。把上限檢查暫時停用後變紅：`assert 201 == 422`。
  - API「SQL 片段原樣讀回」：保護它的是 `db.py` 的 `?` 參數（B 的檔案）。A 不改 B 的檔案，改請 B 驗證紅燈，結果見下一行。
    - B 驗證結果：暫時把 `db.insert_leave` 的 `reason` 改成 f-string 拼接（`'{leave['reason']}'`），`-k tc10_sql` 變紅：`assert 500 == 201`（理由裡的 `'` 閉合了 SQL 字串，造成語法錯誤，被 TC-11 的處理轉成 500）。從備份還原後 `diff` 相同，全套 38 passed。
- 後續文件：無。邊界案例的「合法」那一側常常一跑就綠，可以用突變（例如把 `>` 改成 `>=`）證明測試守得住邊界。

### 2026-10-28／票 001 WBS 4.2｜TC-12 三項做法與 Test Plan 字面不同

- 講義說（Test Plan TC-12）：第 3 步用 DevTools Slow 3G；第 4 步日期區間寫「2026-10-16～2026-10-19」；第 8 步在終端機按 Ctrl+C。實際：第 3 步用 Playwright `page.route` 把 POST 延遲 3 秒；畫面顯示「2026-10-16 ～ 2026-10-19」（「～」前後各一個空白，來自 `app.js` 的 `formatDateRange`）；第 8 步用工具停止背景 uvicorn。
- 發現方式：A 操作時主動提出，B 記錄在 `docs/evidence/TC-12-record-2026-10-28.md`。
- 對齊方式與證據：小組 2026-10-28 判斷三項都不算失敗：前兩項驗的是同一件事（送出中只送 1 筆；服務停止後重啟資料仍在，log 與 `curl` 000 為證），第三項只差空白、內容正確。不改程式，也不改 Test Plan。
- 後續文件：無。之後若用 Agent 執行人工步驟，Test Plan 可改寫成「讓送出變慢的任一方式」「停止服務的任一方式」。

## 規格誤解

### Brief D-1／PRD AC-02.5「理由最多 200 字」

「200 字」至少有三種解讀：
- 中文與全形字算 1 字還是 2 字。
- 頭尾空白算不算。
- 只填空白算不算有填。

這三點不定，邊界案例就算不出預期值。解法是改規格，不是改程式：小組定案 SRS Q-1（去頭尾空白後以字元計算，每字算 1；只含空白視為未填），並補上邊界例子 E18～E21。

## 踩過的坑

- Markdown 表格中間若插入空行，表格會被切成兩張。SRS 待決事項表的 Q-10 曾因此獨立成另一張表；修改表格後要檢查列與列之間有沒有空行。
- 系統預設的 `python3` 是 3.9.6，不符合 `>=3.12`。一律使用 `.venv/bin/python`（3.12.14）。
- `course/01-上課/05-constraints.txt` 只在 Windows／Python 3.12.9 上驗證過，macOS 上是否可裝、可跑尚未驗證；000 第一次安裝時要記錄結果。
  - 2026-10-28／000 結果：macOS（Darwin 25.5.0）／CPython 3.12.14 以 `-c` 安裝 `-e ".[dev]"` 成功，health 測試 2 passed。實際版本：fastapi 0.162.0、starlette 1.10.0、uvicorn 0.54.0、httpx 0.28.1、pytest 9.1.1、pydantic 2.14.1。
- 2026-10-28／缺陷 D-2｜`monkeypatch.undo()` 讓 TC-11 讀到開發資料庫。
  - 現象：開發資料庫刪除後，TC-11 失敗：`sqlite3.OperationalError: no such table: employees`，而且 `backend/data/leavebot.db` 被建成 0 byte 的空檔。開發資料庫存在時則是假通過。
  - 原因：`monkeypatch.undo()` 會還原同一個 `monkeypatch` 的**所有**修改，包含 conftest 用來設定 `LEAVEBOT_DB` 的 `setenv`。TC-11 本來只想還原 `db.insert_leave`，結果之後的「E001 筆數 0」改讀開發資料庫。
  - 為什麼之前沒抓到：隔離檢查只看開發資料庫的 mtime，但這個錯誤只讀不寫，mtime 不會變。
  - 修法：TC-11 改用 `with monkeypatch.context() as m:`，只在 POST 期間替換函式；conftest 的 `db_path` 改用獨立的 `pytest.MonkeyPatch.context()`，測試再呼叫 `undo()` 也還原不到路徑。Test Plan 的 TC-11 步驟與斷言都沒有改。
  - 重現與驗證：讓 `LEAVEBOT_DB` 從外面指向一個有 E001 假單的資料庫，原本的 TC-11 變紅（`assert {'leaves': [{...}]} == {'leaves': []}`），修正後轉綠。只修 conftest、TC-11 仍用 `undo()` 時也會通過。
  - 檢查方式要改：驗證「測試不碰開發資料庫」時，除了 mtime，還要做兩件事：(1) 刪掉開發資料庫後跑全套，確認跑完仍不存在；(2) 在開發資料庫放一筆會讓測試失敗的資料，確認測試仍通過。
- 這組版本下 `fastapi.testclient` 會發出 `StarletteDeprecationWarning`，建議改裝 `httpx2`。`httpx2` 不在白名單，所以不加，警告保留；之後 starlette 若移除 httpx 支援再回來處理。

## 已升級成規則

- 目前沒有。
