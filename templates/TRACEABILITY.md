# 追溯規則：需求怎麼一路接到測試

> 六份文件不是六份報告，是**一條鏈**。每一環都用編號指回上一環，最後由測試接住。
> 鏈斷在哪裡，`.venv/bin/python scripts/trace.py` 會告訴你。

## 編號

| 編號 | 在哪份文件定義 | 例 |
|---|---|---|
| `G-01` `NG-01` | 01 Brief | 目標、非目標 |
| `P-01` `EP-01` `US-01` | 02 PRD | persona、epic、user story |
| `AC-01.1` | 02 PRD | US-01 的第 1 條驗收條件 |
| `UC-01` `FR-01` `NFR-01` | 03 SRS | use case、功能、非功能需求 |
| `ADR-01` | 04 SAD | 技術選型 |
| `API-01` `UI-01` | 05 SDS | API、畫面 |
| `TC-01` | 06 Test Plan | 測試案例 |

**定義** = 寫在標題開頭（`### UC-01`）、粗體開頭（`- **AC-01.1** …`）、或表格第一欄（`| FR-01 |`）。其他位置出現只算引用。
編號發出去就凍結；作廢的留著標「已作廢」；不重用。

## 鏈

```text
G ─▶ EP ─▶ US ─▶ AC ─┬─▶ FR / NFR ─▶ API / UI / 模組
                     │        │
                     └────────┴─▶ TC ─▶ @pytest.mark.req("TC-xx")
```

## V-model

```text
 01 Brief / 02 PRD  ─────────────────▶  驗收測試     tests/acceptance/
      03 SRS  ─────────────────────▶  系統測試＋eval tests/system/、run_eval.py
          04 SAD  ─────────────────▶  整合測試     tests/integration/
              05 SDS  ─────────────▶  單元測試     tests/unit/
                    ╲             ╱
                     06 Test Plan（先寫好右邊要驗什麼）
```

## trace.py 擋三種斷鏈

| 缺口 | 意思 | 怎麼補 |
|---|---|---|
| 沒有 TC | 有 AC / FR / NFR 沒被任何 TC 涵蓋 | 在 06 加 TC，或寫進「不測什麼」並寫理由 |
| TC 沒有測試 | 計畫了但沒寫 | 寫測試，標 `@pytest.mark.req("TC-xx")` |
| 指向不存在的編號 | 測試標的編號文件裡沒有 | 改標註，或補文件 |

```bash
.venv/bin/python scripts/trace.py            # 看矩陣與缺口
.venv/bin/python scripts/trace.py --strict   # 有缺口就失敗（交付前跑）
```

## 這句話該寫在哪份文件

```text
有技術名詞（框架、資料表、API 路徑）嗎？
├─ 有 → 講「怎麼組起來」→ 04 SAD；講「每一塊怎麼做」→ 05 SDS
└─ 沒有
   └─ 寫得成 Given / When / Then 嗎？
      ├─ 能 → 使用者看得到的結果 → 02 PRD 的 AC；系統必須做到的行為 → 03 SRS 的 FR / NFR
      └─ 不能
         └─ 在講「為什麼、為誰、值不值得」嗎？
            ├─ 是 → 01 Brief 或 02 PRD 的 persona / epic
            └─ 不是 → 可能不該存在；是願望就放 03 的「無法驗證區」
```

改編自原 `sdd-lite` 線（已封存為 `archive/sdd-lite`）的 `docs/DOC-MAP.md` 與 SRS 編號規則。
