---
name: to-architecture
description: 從 1_requirements.md 產出 2_architecture.md：系統邊界、AI 與程式碼的分工、資料模型、API、技術決策。拆票之前做。
disable-model-invocation: true
---

# To Architecture

Turn `1_requirements.md` into the technical decisions the tickets will depend on. Runs after the requirement is settled, before `/to-tickets` — architecture decisions change how work should be split, so settle them first.

## Shape

Write `2_architecture.md` at the repo root, following the section order of `templates/2_architecture_template.md`. Read that template first; its `💡` hints are rules for you and must not appear in the output.

The sections that matter most in this project:

- **誰負責什麼** — for every decision in the flow, say whether the LLM, the code, or a human makes it. Remaining leave balance, date clashes and approval are never the LLM's.
- **資料模型** — a Mermaid `erDiagram`, using the words `1_requirements.md` uses.
- **API** — only the endpoints and payloads the tickets will build against, not a full catalogue.
- **技術決策** — one entry per choice that had a real alternative: what was chosen, what was rejected, why. A choice with no alternative considered gets no entry.

## Rules

- **Do not invent.** The material is `1_requirements.md`, `LEAVEBOT.md`, `AGENTS.md` and the conversation. An open choice goes back to `/grilling` — it does not get a plausible default.
- **Stay inside the starter's stack** (FastAPI + SQLite + pytest, see `AGENTS.md`). Adding a dependency is a decision the user makes, not you.
- **Decisions, not ceremony.** No C4 levels, no NFR boilerplate. A section with nothing settled in it says so in one line.
- **Every acceptance criterion must land somewhere.** Before finishing, list each criterion from `1_requirements.md` and the part of the architecture that serves it. One that lands nowhere is a gap — report it.
- **Show the draft before writing.** Let the user edit, then write the file.

## Finish

Report the file path, the acceptance criteria that landed nowhere (if any), and the next step: `/to-tickets`.

## Rationalization table

| Excuse | Reality |
| --- | --- |
| "The requirement didn't say, Postgres is a safe default" | A guessed default is a decision nobody made. Unsettled choices go back upstream. |
| "The LLM can just return the remaining balance too" | Then the balance is whatever the model says. Numbers and statuses come from code. |
| "A big diagram makes it look complete" | Diagrams earn their place by answering a question a ticket will ask. |
