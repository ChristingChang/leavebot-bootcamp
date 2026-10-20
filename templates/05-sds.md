# 05 SDS —— ＜專案名稱＞

> **每一塊怎麼做。** 細到 agent 可以照著寫程式、你可以照著驗收。上游：`04-sad.md`。範例：`examples/it-asset/05-sds.md`。

| 項目 | 內容 |
|---|---|
| 版本 | ＜v0.1＞ |
| 上游 | `04-sad.md` ＜v0.1＞ |
| 最後更新 | ＜YYYY-MM-DD＞ |

---

## 1. ER Model

> 💡 只畫這一版需要的表。使用者原本輸入的文字建議存下來，AI 出錯時才查得到。名稱只用英文、數字、底線。

```mermaid
erDiagram
    TABLE_A ||--o{ TABLE_B : has
    TABLE_A {
        int id PK
        string field_name
    }
    TABLE_B {
        int id PK
        int table_a_id FK
        string field_name
    }
```

| 表 | 欄位 | 型別 | 允許的值 / 預設 | 對應需求 |
|---|---|---|---|---|
| ＜＞ | ＜＞ | ＜＞ | ＜＞ | ＜FR-02＞ |

---

## 2. API 規格

> 💡 每支 API 都寫錯誤情況 —— 只寫成功路徑，AI 會自己發明錯誤處理。路徑一律在 `/api` 底下。
> 解析 API 的形狀已由 `STACK.md` 固定，照抄，不要改。

### API-01 `POST /api/parse`

| 項目 | 內容 |
|---|---|
| 用途 | 把一句話解析成假單草稿（**只解析，不存檔**） |
| 對應需求 | ＜FR-01＞ |
| Request | `{"sentence": "string", "today": "YYYY-MM-DD"}` |
| Response 200 | `{"requests": [{"start_date", "end_date", "period", "leave_type", "days"}], "clarify": bool}` |

| 錯誤情況 | 狀態碼 | 回傳 |
|---|---|---|
| ＜例：模型逾時＞ | ＜503＞ | ＜`{"error": "…"}`＞ |
| ＜例：模型輸出不符格式＞ | ＜422＞ | ＜＞ |

### API-02 `＜METHOD＞ /api/＜path＞`

| 項目 | 內容 |
|---|---|
| 用途 | ＜＞ |
| 對應需求 | ＜＞ |
| Request | ＜＞ |
| Response 200 | ＜＞ |

| 錯誤情況 | 狀態碼 | 回傳 |
|---|---|---|
| ＜＞ | ＜＞ | ＜＞ |

---

## 3. 畫面

> 💡 每個畫面：誰用、顯示什麼、能做什麼、呼叫哪支 API。對到 PRD 的 user flow。

| 編號 | 畫面 | 誰用 | 顯示 | 動作 → API | 對應需求 |
|---|---|---|---|---|---|
| UI-01 | ＜＞ | ＜P-01＞ | ＜＞ | ＜按「送出」→ API-02＞ | ＜US-01＞ |

---

## 4. 模組與介面

> 💡 後端拆成哪些模組、各自對外提供什麼函式。**AI 的部分與規則的部分分開成不同模組**，規則才測得了。

| 模組 | 負責 | 對外介面（簽名） | 對應需求 |
|---|---|---|---|
| ＜例：parsing＞ | ＜呼叫 LLM、驗證輸出格式＞ | ＜`parse(sentence: str, today: date) -> ParseResult`＞ | ＜FR-01＞ |
| ＜例：rules＞ | ＜剩餘額度、撞期＞ | ＜＞ | ＜FR-03＞ |

**今天是幾號**：＜例：`clock.today()` 讀 `LEAVEBOT_TODAY`（見 `STACK.md`），測試注入固定日期＞

**給 LLM 的 prompt 放哪裡、輸出怎麼驗證**：＜例：prompt 放 `backend/app/prompts.py`；輸出用 pydantic model 驗證，失敗回 422＞

---

## 通過檢核

- [ ] ER 圖在 Mermaid 預覽裡畫得出來，每張表都對到需求
- [ ] 每支 API 都有對應需求與錯誤情況；`API-01` 符合 `STACK.md` 的合約
- [ ] 每個畫面都對到 PRD user flow 的某一步
- [ ] AI 與規則在不同模組
