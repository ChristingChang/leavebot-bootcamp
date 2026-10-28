# 05 SDS — LeaveBot 請假系統

> 版本：v0.2（2026-10-28：UI-01 理由空白時顯示「--」，小組確認）｜負責人：ChristingChang（小組）｜日期：2026-10-28｜狀態：草稿（待講師審查）｜審查者：講師（待審）
> 上游：`docs/04-sad.md`、`docs/03-srs.md`（v0.3）。契約變更時同步更新 `docs/06-test-plan.md` 的 TC。
> 例子中的員工都來自下方的種子資料；日期星期已核對。

## 目錄

- [資料模型與不變量](#資料模型與不變量)
- [API 契約](#api-契約)
- [UI 與模組契約](#ui-與模組契約)
- [變更與未決](#變更與未決)

## 資料模型與不變量

員工是預先寫入的種子資料，本次只讀不改。假單由 POST 一次建立，之後主線不修改也不刪除。`id`、`days`、`status` 由伺服器決定；客戶端請求帶這些欄位會被拒絕（Q-3、Q-10）。

| 欄位                           | 型別、格式與可空性         | 預設／約束                                                                            | 來源         |
| ------------------------------ | -------------------------- | ------------------------------------------------------------------------------------- | ------------ |
| `employees.id`               | TEXT，非空，例如 `E001`  | 主鍵                                                                                  | FR-01、Q-2   |
| `employees.name`             | TEXT，非空                 | —                                                                                    | FR-01        |
| `leave_requests.id`          | INTEGER，非空              | 主鍵，自動遞增；也是列表排序依據                                                      | FR-02、FR-09 |
| `leave_requests.employee_id` | TEXT，非空                 | 外鍵 → `employees.id`                                                              | FR-01、FR-09 |
| `leave_requests.leave_type`  | TEXT，非空                 | CHECK 值為 `annual`／`personal`／`sick`                                         | FR-03        |
| `leave_requests.start_date`  | TEXT，非空，`YYYY-MM-DD` | —                                                                                    | FR-03、FR-04 |
| `leave_requests.end_date`    | TEXT，非空，`YYYY-MM-DD` | CHECK `end_date >= start_date`                                                      | FR-04        |
| `leave_requests.period`      | TEXT，非空                 | CHECK 值為 `full_day`／`am`／`pm`                                               | FR-03、FR-05 |
| `leave_requests.reason`      | TEXT，非空                 | 預設 `''`；已去頭尾空白。長度上限**只在程式**檢查，不加 DB CHECK（Brief R-3） | FR-07        |
| `leave_requests.days`        | REAL，非空                 | CHECK `days > 0`；值為 0.5 的倍數                                                   | FR-06、FR-08 |
| `leave_requests.status`      | TEXT，非空                 | 預設 `'pending'`；CHECK `status = 'pending'`（主線唯一合法值）                    | FR-08        |

**種子員工**（Q-2）：初始化時以「不存在才插入」寫入，可重複執行。

| id       | name   |
| -------- | ------ |
| `E001` | 王小明 |
| `E002` | 李小華 |
| `E003` | 陳小美 |

AC 裡的「員工甲」對應 `E001`，「員工乙」對應 `E002`。

**初始化與連線：**

- 應用程式啟動（lifespan）時，對 `get_db_path()` 執行 `init_db()`：`CREATE TABLE IF NOT EXISTS` 加種子資料，可重複執行。
- 每個 API 請求開一條連線，請求結束時在 `finally` 關閉。每條連線都啟用 `PRAGMA foreign_keys = ON`。
- 匯入任何模組時都不連線資料庫。

**交易邊界：** POST 先在記憶體中完成全部驗證，沒有錯誤才進入寫入交易。寫入交易只有一個 INSERT，用 `with conn:` 包住，成功就提交、例外就回滾。

**持久性：** 資料存在 `LEAVEBOT_DB` 指向的檔案，重新整理頁面或重啟服務後仍在（NFR-03）。

**重試與重複送出：** POST 不具冪等性，每次成功都新增一筆（D-3）。若伺服器已提交，但瀏覽器因網路錯誤沒收到回應，員工可能重送而產生兩筆。前端在任何失敗後都會重新讀取列表，讓員工看得到實際存檔結果（見 UI-01）。

**資料不變量：**

- I-1：每筆假單的 `status` 都是 `pending`。程式只寫入 `pending`，DB CHECK 是最後防線。
- I-2：`days` 等於 `count_leave_days(start_date, end_date, period)`，大於 0，且是 0.5 的倍數。
- I-3：`end_date >= start_date`；`period` 為 `am`／`pm` 時，`start_date == end_date`。
- I-4：`employee_id` 一定存在於 `employees`（外鍵）。
- I-5：`reason` 已去頭尾空白，寫入當下長度不超過 `REASON_MAX_LENGTH`。
- I-6：任何 4xx 或 5xx 回應之後，假單筆數與送出前相同（NFR-01）。

## API 契約

所有 API 都在 `/api/` 下，請求與回應都是 JSON（UTF-8），前端以相對路徑呼叫，不開 CORS。

**錯誤格式：** 所有錯誤回應都使用同一種本文。

```json
{"errors": [{"field": "leave_type", "code": "required", "message": "請選擇假別"}]}
```

- `field`：出錯的請求欄位名稱。整筆層級的錯誤為 `null`，例如沒有工作日、資料庫故障。
- `code`：給程式與測試判斷用，見下表。
- `message`：給使用者看的中文訊息。前端以 `textContent` 顯示（NFR-04）。
- 測試只斷言 `errors` 中「包含」預期的 `field` 與 `code`，不斷言順序或訊息全文。

| code                       | HTTP                     | field                        | 何時發生                                       | 訊息範例                                   | 來源       |
| -------------------------- | ------------------------ | ---------------------------- | ---------------------------------------------- | ------------------------------------------ | ---------- |
| `invalid_body`           | 400                      | `null`                     | 本文不是 JSON，或不是 JSON 物件                | 請求格式錯誤                               | —         |
| `unknown_field`          | 422                      | 該欄位名                     | 出現未定義的欄位                               | 不接受的欄位：foo                          | Q-10       |
| `client_field_forbidden` | 422                      | `status`／`days`         | 請求帶了狀態或天數，不論值為何                 | 狀態不能由申請人指定                       | FR-08、Q-3 |
| `required`               | 422                      | 該欄位名                     | 必填欄位缺漏、`null` 或空字串                | 請選擇假別                                 | FR-03      |
| `invalid_value`          | 422                      | 該欄位名                     | 型別不是字串，或值不在允許清單（大小寫須一致） | 假別不正確                                 | FR-03      |
| `invalid_date`           | 422                      | `start_date`／`end_date` | 格式不是 `YYYY-MM-DD`，或日期不存在          | 開始日期格式不正確                         | FR-03      |
| `employee_not_found`     | 422（POST）／404（列表） | `employee_id`              | 員工 ID 不在員工表                             | 找不到這位員工                             | FR-01      |
| `end_before_start`       | 422                      | `end_date`                 | 結束日期早於開始日期                           | 結束日期不能早於開始日期                   | FR-04      |
| `half_day_multi_day`     | 422                      | `period`                   | 上午／下午，但開始與結束不同天                 | 半天假只能選同一天                         | FR-05      |
| `no_workday`             | 422                      | `null`                     | 區間內沒有週一至週五                           | 選擇的日期沒有工作日                       | FR-06      |
| `reason_too_long`        | 422                      | `reason`                   | 去頭尾空白後超過 `REASON_MAX_LENGTH`         | 理由最多 200 字                            | FR-07      |
| `database_error`         | 500                      | `null`                     | 資料庫讀寫拋出例外                             | 系統暫時無法處理，資料沒有存檔，請稍後再試 | NFR-01     |

`reason_too_long` 的訊息由 `REASON_MAX_LENGTH` 組出，不另外寫死「200」。

### API-01｜GET /api/health

用途：確認服務啟動，首頁以此顯示連線狀態（骨架票 000）。

- 成功：`200 {"status": "ok"}`。
- 不讀資料庫。
- 失敗：服務沒有啟動時，連線本身就會失敗，由前端顯示「無法連線」。

### API-02｜GET /api/employees（FR-01）

頁面載入時呼叫，用來填入下拉選單。沒有資料副作用。

- 成功：`200`，依 `id` 遞增排序。

  ```json
  {"employees": [{"id": "E001", "name": "王小明"}, {"id": "E002", "name": "李小華"}, {"id": "E003", "name": "陳小美"}]}
  ```
- 失敗：資料庫例外回 `500 database_error`，訊息改為「系統暫時無法讀取資料，請稍後再試」。

### API-03｜POST /api/leaves（FR-01～FR-08、FR-10）

員工按送出時呼叫。伺服器驗證全部規則；只有完全合法時，才以伺服器算出的 `days` 和 `status = "pending"` 新增一筆。

- 請求：只允許下列 6 個欄位。前端一律送出全部 6 個，`reason` 可以是空字串。

  ```json
  {"employee_id": "E001", "leave_type": "annual", "start_date": "2026-10-16", "end_date": "2026-10-19", "period": "full_day", "reason": ""}
  ```

  | 欄位                         | 必填 | 合法值                                                                            |
  | ---------------------------- | ---- | --------------------------------------------------------------------------------- |
  | `employee_id`              | 是   | 員工表中的 id                                                                     |
  | `leave_type`               | 是   | `annual`、`personal`、`sick`                                                |
  | `start_date`、`end_date` | 是   | `YYYY-MM-DD` 的實際存在日期；不限過去或未來（D-2、Q-8）                         |
  | `period`                   | 是   | `full_day`、`am`、`pm`                                                      |
  | `reason`                   | 否   | 字串；缺漏或 `null` 視為空字串；去頭尾空白後 0～`REASON_MAX_LENGTH` 字（Q-1） |
- 成功：`201`，回傳實際存下的資料（SRS E1）。

  ```json
  {"leave": {"id": 1, "employee_id": "E001", "leave_type": "annual", "start_date": "2026-10-16", "end_date": "2026-10-19", "period": "full_day", "reason": "", "days": 2, "status": "pending"}}
  ```

  `days` 是 JSON 數字，可能序列化成 `2` 或 `2.0`，請以數值比較。
- 失敗：`400` 或 `422`，資料庫完全不寫入。`500` 時交易回滾，也不留資料。全部錯誤一次回傳（Q-7）。以下是同時缺假別、日期又反向的例子：

  ```json
  {"errors": [
    {"field": "leave_type", "code": "required", "message": "請選擇假別"},
    {"field": "end_date", "code": "end_before_start", "message": "結束日期不能早於開始日期"}
  ]}
  ```
- 驗證順序與跨欄位規則：讓多重錯誤的結果可以預測。

  1. 本文不是 JSON 物件時，直接回 400，不做後續檢查。
  2. 逐一檢查每個鍵：`status`、`days` 記為 `client_field_forbidden`，其他未定義的鍵記為 `unknown_field`。
  3. 逐欄檢查 `employee_id`、`leave_type`、`start_date`、`end_date`、`period`、`reason` 的必填、型別與合法值；員工存在與否也在這一步。
  4. **只有在 `start_date`、`end_date`、`period` 三者各自合法時**，才檢查跨欄位規則，而且最多產生一條：

     - 先看 `end_before_start`；
     - 不成立時再看 `half_day_multi_day`；
     - 也不成立時再看 `no_workday`。

     例如：開始 10-20、結束 10-19、下午，只回 `end_before_start`，不會同時回 `half_day_multi_day`。

### API-04｜GET /api/employees//leaves（FR-09）

選員工時、送出成功後、送出失敗後都會呼叫。沒有資料副作用。

- 成功：`200`，只含該員工的假單，依 `id` 由大到小（最新送出在最前，Q-4）。沒有假單時回 `{"leaves": []}`。

  ```json
  {"leaves": [{"id": 3, "employee_id": "E001", "leave_type": "sick", "start_date": "2026-10-05", "end_date": "2026-10-05", "period": "full_day", "reason": "發燒", "days": 1, "status": "pending"}]}
  ```
- 失敗：

  - 員工不存在時回 `404`，錯誤碼 `employee_not_found`。
  - 資料庫例外時回 `500`，錯誤碼 `database_error`。
- 讀取語意：查詢條件一律含 `WHERE employee_id = ?`，不會回傳其他員工的資料（SRS E17）。

**路由登記順序：** `create_app()` 先 `include_router` 所有 `/api` 路由，**最後**才 `mount("/", StaticFiles(directory=<app>/static, html=True))`。這樣靜態檔不會攔截 API 路徑。

## UI 與模組契約

### UI-01｜單頁請假畫面（US-01、US-02、US-03）

整個功能只有一頁 `static/index.html`，加上 `app.js`、`style.css`。所有使用者文字（姓名、理由、錯誤訊息）一律用 `textContent` 放進畫面，不使用 `innerHTML`（NFR-02、SRS E16）。

- **載入：** 呼叫 API-02 填入下拉選單。初始為未選擇狀態，送出按鈕停用並提示「請先選擇員工」；列表區顯示同樣的提示（Q-6）。
- **選員工：** 呼叫 API-04，顯示該員工的假單列表。
  - 沒有假單時顯示「目前沒有假單」（Q-4）。
  - 每筆顯示假別（特休／事假／病假）、日期區間、時段（整天／上午／下午）、天數、狀態（待審核）、理由（Q-9）。
  - 理由為空字串時顯示「理由：--」，不省略這一行（2026-10-28 小組決定）。只有前端顯示改變，API 與資料庫照舊存空字串。
  - 代碼轉中文的對照表只在 `app.js` 定義一處。
- **送出中：** 按鈕設為 `disabled`，文字改為「送出中…」。在收到回應前不會再發出請求（FR-10、AC-01.4）。
- **成功（201）：**
  - 顯示「已送出：<日期區間>，共 <days></days> 天，待審核」。
  - 清空假別、日期、時段、理由，保留所選員工（Q-5）。
  - 重新呼叫 API-04，按鈕恢復可用。
- **驗證失敗（400／422）：**
  - 逐條顯示 `errors[].message`。有 `field` 的錯誤顯示在對應欄位旁，`field` 為 `null` 的顯示在表單頂端。
  - 保留表單內容（Q-5），按鈕恢復可用。
- **伺服器或網路失敗（500、無回應）：**
  - 顯示「系統暫時無法處理，資料沒有存檔，請稍後再試」，保留表單內容，按鈕恢復可用。
  - 重新呼叫 API-04，讓員工看見實際狀態。
- **前端的責任範圍：**
  - 前端**不做**業務規則驗證：不檢查日期順序、字數，也不加 `maxlength`，上限只在後端定義一處（R-3）。
  - 前端只負責「未選員工時停用送出」與「送出中停用」這兩個體驗限制。
  - 前端永遠不送 `status`、`days`。

### 模組接縫（`backend/app/`）

**`leave_rules.py`：純函式，不碰資料庫與環境變數（FR-03～FR-08，ADR-01）**

- 常數：
  - `REASON_MAX_LENGTH = 200`（理由上限，唯一定義處；變更票 002 只改這裡）。
  - `LEAVE_TYPES = ("annual", "personal", "sick")`、`PERIODS = ("full_day", "am", "pm")`。
  - `ALLOWED_FIELDS`：上述 6 個請求欄位。
- `count_leave_days(start: date, end: date, period: str) -> float`：
  - 前提是 `end >= start`。
  - 計算包含首尾的週一至週五天數：`full_day` 時回傳工作日數；`am`／`pm` 時，若該日是工作日回傳 0.5，否則回傳 0。
  - 回傳 0 代表沒有工作日，由呼叫端轉成 `no_workday`。
- `normalize_reason(value) -> str`：
  - `None` 視為 `""`。
  - 字串去掉頭尾空白後回傳。`str.strip()` 涵蓋全形空白 U+3000。
  - 非字串的處理由呼叫端判定為 `invalid_value`。
- `validate_leave_request(payload: dict, employee_ids: set[str]) -> ValidationResult`：
  - 依 API-03 的驗證順序檢查。
  - `ValidationResult` 有兩個屬性：`errors: list[dict]`（每項含 `field`、`code`、`message`）與 `leave: dict | None`。
  - 恰好其中一個有內容。合法時，`leave` 含 6 個正規化後的欄位，加上 `days` 和 `status="pending"`。

**`db.py`：唯一碰 SQLite 的模組（FR-01、FR-02、FR-09；NFR-02、NFR-03）**

- `get_db_path() -> Path`：每次呼叫都重新讀 `LEAVEBOT_DB`；未設定時用 `backend/data/leavebot.db`，並建立上層目錄。
- `connect(path) -> sqlite3.Connection`：設定 `row_factory = sqlite3.Row`，啟用外鍵；由呼叫端負責關閉。
- `init_db(path) -> None`：建表加種子資料，可重複執行；結束時關閉自己開的連線。
- `list_employees(conn) -> list[dict]`、`list_employee_ids(conn) -> set[str]`。
- `insert_leave(conn, leave: dict) -> dict`：在 `with conn:` 交易中 INSERT，回傳含 `id` 的完整資料。
- `list_leaves(conn, employee_id: str) -> list[dict]`：依 `id DESC` 排序。
- 所有 SQL 都用 `?` 參數，不以字串拼接使用者輸入（NFR-02）。
- `sqlite3.Error` 不在這裡吞掉，交給 API 層處理。

**`api.py`：路由（`APIRouter(prefix="/api")`）**

- API-03 端點以 `await request.json()` 讀取原始本文，不宣告 Pydantic 請求模型（ADR-01）。
- 端點以 `db.insert_leave(...)` 這種**模組屬性**的方式呼叫 `db`，不用 `from db import insert_leave`，讓測試能替換函式來模擬資料庫故障。
- 端點捕捉 `sqlite3.Error`，轉成 `500 database_error`。
- 連線以 FastAPI dependency（`yield` 後關閉）提供。

**`main.py`**

- 提供 `create_app() -> FastAPI` 與模組層級的 `app = create_app()`。
- lifespan 啟動時執行 `db.init_db(db.get_db_path())`。
- 先登記 router，最後掛載靜態目錄。

### 測試注入方式（NFR-05）

- **暫存資料庫：**
  - pytest fixture 先執行 `monkeypatch.setenv("LEAVEBOT_DB", str(tmp_path / "test.db"))`，再用 `with TestClient(app) as client:`，觸發 lifespan 初始化。
  - 每個測試都有自己的檔案，不會讀寫開發資料庫。
  - 因為路徑在請求當下讀取、匯入時不連線，同一個 `app` 物件可以在不同測試間重複使用。
- **資料庫故障：** 用 `monkeypatch.setattr(db, "insert_leave", 會拋出 sqlite3.OperationalError 的函式)` 替換寫入函式，斷言回應是 `500 database_error`，且列表筆數不變。
- **規則單元測試：** 直接呼叫 `leave_rules.validate_leave_request()` 與 `count_leave_days()`，傳入 `employee_ids={"E001", "E002", "E003"}`，不需要資料庫或 HTTP。
- **固定時鐘：主線不需要。**
  - 接受過去日期（D-2），日期也不設上下限（Q-8），所以沒有任何規則讀「今天」。AC 裡的 2026-10-12 只是情境描述。
  - 因此主線**不建立**時鐘模組，也不讀 `LEAVEBOT_TODAY`。
  - 若日後有規則需要「今天」，依 STACK 做法：只由單一函式 `today()` 在呼叫當下讀取 `LEAVEBOT_TODAY`，未設定時用真實日期；測試以 `monkeypatch.setenv("LEAVEBOT_TODAY", "2026-10-12")` 注入。

## 變更與未決

- **相容性：** 全新系統，沒有既有資料或 API，不需要遷移。
- **已知的後續變更：**
  - 變更票 `issues/002-reason-limit.md` 會把上限從 200 改為 100，只需改 `REASON_MAX_LENGTH`。
  - 理由長度沒有 DB CHECK，所以舊資料中 101～200 字的理由仍會保留，也能正常列出。變更票要決定這是否可接受。
- **C1 主管核准**需要放寬 `status` 的 CHECK 並遷移資料表（SAD R-B），屆時另開票處理。
- **未決：** 沒有影響實作的未決契約。

> 審查重點：欄位、狀態碼、錯誤及資料副作用可直接實作；前後端契約一致；FR／NFR 有落點；測試者可據此建立獨立預期。
