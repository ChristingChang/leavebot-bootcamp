# Checkpoint：先確認可用，再切換

`main` 保持空白學生起點。五個 `cp*` 分支是講師的參考快照，採用同一份課程規格；來源與驗證證據見各快照的 `course/CHECKPOINT-RECEIPT.md`。

| 時點 | 分支 | 內容／接續 |
|---|---|---|
| 10:30 | `cp1-requirements` | Brief、PRD、SRS 已確認；單元10／卡D、E |
| 12:30 | `cp2-design` | 設計、TC、兩張票，尚無app；單元12／卡H骨架 |
| 14:15 | `cp3-tests` | 骨架測試綠；首個業務測試預期紅；單元12／卡H表單TDD |
| 16:30 | `cp4-working-feature` | 表單主線與測試通過；單元13／卡I、J |
| 17:30 | `cp5-delivered` | 變更後的交付範例與證據；單元14／卡K或課後比對 |

## 取得
在自己的 fork 根目錄，若尚未設定 upstream：
```bash
git remote add upstream https://github.com/Zenobia000/leavebot-bootcamp.git
git fetch upstream
git branch -r
```
只 fork main 就夠，保底分支可從 upstream 取得。看不到分支時先查講師是否已發布；不要把「只複製main」直接當成錯誤原因。

## 保留自己進度後才切
先用 `git status`、`git diff` 看改動，把本次成果以明確路徑加入並 commit。檔案路徑依實際存在者選，不貼一串可能不存在的路徑，也不使用 `git add -A`。未追蹤的資料庫與秘密不要加入。
確認工作目錄乾淨後：
```bash
git fetch upstream
git show-ref --verify refs/remotes/upstream/cp2-design
git switch -c rescue-cp2 upstream/cp2-design
```
`show-ref` 找不到就停止並詢問講師。`rescue-cp2` 已存在時先看該分支進度，不能刪掉重建。切換前先停止開發伺服器；含程式的快照重新建 venv 並依 STACK 安裝，資料庫不隨 Git 分支變動。

`cp3-tests` 的首個業務測試預期失敗；這是給學生完成綠燈的起點，不是完整功能。保底快照只提供一組已確認決策，可能與本組不同，切過去後先讀差異。
