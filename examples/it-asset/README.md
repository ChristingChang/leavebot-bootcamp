# 範例：IT 設備借用平台（六份文件）

> **看「寫完長什麼樣」用，不要照抄。** 題目刻意和 LeaveBot 不同：這裡的 AI 只「建議設備類型」，不解析日期。
> 每一份都照 [`../../templates/`](../../templates/) 的格式寫，也都通過了模板最後的通過檢核。

| 文件 | 看什麼 |
|---|---|
| [`01-brief.md`](./01-brief.md) | goal 怎麼寫得可以量、non-goal 怎麼寫理由 |
| [`02-prd.md`](./02-prd.md) | user flow 畫到多細、BDD 的失敗路徑長什麼樣 |
| [`03-srs.md`](./03-srs.md) | FR 怎麼標來源、NFR 怎麼寫「怎麼驗」 |
| [`04-sad.md`](./04-sad.md) | C4、資訊流裡「AI 輸出在哪裡被驗證」 |
| [`05-sds.md`](./05-sds.md) | API 錯誤情況、AI 與規則分成不同模組 |
| [`06-test-plan.md`](./06-test-plan.md) | TC 怎麼對回需求、AI 窮舉後刪掉了什麼、門檻為什麼是那個數字 |

自己跑一次追溯檢查（範例沒有程式，所以每個 TC 都會顯示「還沒有測試」—— 那是 D2 要補的）：

```bash
.venv/bin/python scripts/trace.py --docs examples/it-asset
```
