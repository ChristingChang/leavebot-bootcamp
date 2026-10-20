# 模板庫

> 上課時用，回公司也能直接帶走。每一份都是**填空題**：`＜＞` 是要換掉的地方，`💡` 是提示。
> 寫好的範例在 [`../examples/it-asset/`](../examples/it-asset/)（另一個題目：IT 設備借用），看「寫完長什麼樣」用，**不要照抄** —— 你的題目和它不一樣。

## 六份規格文件（D1）

複製到 `docs/`，檔名照抄（`docs/01-brief.md` …），`scripts/trace.py` 靠這個位置找它們。

| 檔案 | 回答 | 單元 |
|---|---|---|
| [`01-brief.md`](./01-brief.md) | 為什麼做：痛點、goal、non-goal | D1-2 |
| [`02-prd.md`](./02-prd.md) | 為誰做、做什麼：persona、user flow、epic、story、BDD 驗收條件 | D1-3 |
| [`03-srs.md`](./03-srs.md) | 什麼叫做好了：use case、FR、NFR | D1-4 |
| [`04-sad.md`](./04-sad.md) | 怎麼組起來：C4、資訊流、誰負責什麼、技術選型 | D1-5 |
| [`05-sds.md`](./05-sds.md) | 每一塊怎麼做：ER、API、畫面、模組 | D1-6 |
| [`06-test-plan.md`](./06-test-plan.md) | 怎麼驗：V-model 對應、測試案例、AI 驗收、退出條件 | D1-7 |
| [`TRACEABILITY.md`](./TRACEABILITY.md) | 編號規則、需求怎麼一路接到測試、這句話該寫在哪份文件 | 隨時查 |

讓 AI 照格式寫：

```text
用 @templates/02-prd.md 的格式，根據 @docs/01-brief.md 和我們剛剛的討論，產出 docs/02-prd.md。
模板裡的 💡 提示是寫給你的規則，要遵守，但不要出現在產出裡。
沒討論到的，放進「待決事項」，不要替我決定。
```

## 專案大腦與紅線（D1-8、D2）

| 檔案 | 什麼時候用 |
|---|---|
| [`agent-rules/AGENTS.safe.md`](./agent-rules/AGENTS.safe.md) | 專案大腦：**通用安全模式**（套件、秘密、輸入驗證、AI 輸出） |
| [`agent-rules/AGENTS.tdd.md`](./agent-rules/AGENTS.tdd.md) | 追加：**TDD 強制模式**（先紅燈、不准改測試） |
| [`hooks/`](./hooks/) | 把紅線從文字規則變成「做不到」 |

**專案大腦怎麼放**：Codex 讀根目錄的 `AGENTS.md`；Claude Code 讀 `CLAUDE.md`，它只有一行 `@AGENTS.md`。所以規則只改 `AGENTS.md`。

## 這些模板刻意不做的事

- **不給 LeaveBot 的答案。** 範例用的是別的題目。
- **不求完整。** 只列這兩天用得到的段落。真實專案需要更多，自己加；用不到的，刪掉。
- **不寫無法檢查的規則。** 「請寫出高品質的程式碼」這種句子，AI 讀了不知道怎麼做，你也不知道它做到了沒。
