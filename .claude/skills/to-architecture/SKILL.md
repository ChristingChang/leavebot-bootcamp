---
name: to-architecture
description: 從 PRD 與 SRS 產出 docs/04-sad.md（C4、資訊流、誰負責什麼、ADR）與 docs/05-sds.md（ER、API、畫面、模組）。寫測試計畫與拆票之前做。
disable-model-invocation: true
---

# To Architecture

Turn `docs/02-prd.md` and `docs/03-srs.md` into the two design documents the tickets and tests will depend on: `docs/04-sad.md` (how it fits together) and `docs/05-sds.md` (how each piece works). Runs after the SRS, before the test plan.

Read first: `course/STACK.md` (the stack is fixed — you design **inside** it), `course/LEAVEBOT.md` (scope and the fixed `POST /api/parse` contract), `course/templates/04-sad.md`, `course/templates/05-sds.md`, `course/templates/TRACEABILITY.md`. The templates' `💡` hints are rules for you and must not appear in the output. `course/examples/it-asset/` shows finished documents for a different problem — use it for depth, never copy its content.

## SAD — what must be in it

- **C4 L1 and L2** as Mermaid `flowchart`s. L2 is browser → Next.js → (rewrites for `/api/*`) → FastAPI → SQLite / an LLM client module that calls the Anthropic API (API only; tests swap in a fake).
- **Information flow** as a Mermaid `sequenceDiagram` for the main path: sentence → parse → **validation of the LLM output** → rules → database → screen. The validation step must be visible.
- **Who does what**: for every decision, the LLM, the code or a human. Remaining leave balance, date clashes and approval are never the LLM's.
- **ADR rows** for choices made inside `course/STACK.md` (including which model, and why) that had a real alternative — chosen, rejected, why, reversible or not, which requirement. A choice with no alternative considered gets no row.

## SDS — what must be in it

- **ER** as a Mermaid `erDiagram`, using the words the PRD uses. Store the employee's original sentence.
- **API** — every endpoint under the `/api/` prefix, each with its requirement IDs and **error cases**. `API-01` is `POST /api/parse`, copied exactly from `course/STACK.md`.
- **Screens** — each mapped to a step of the PRD user flow and to the API it calls.
- **Modules** — the LLM-facing module and the rules module are separate, with the signatures other modules call.

## Rules

- **Do not invent.** An open choice goes back to `/grilling` — it does not get a plausible default.
- **Do not leave the stack.** A new dependency, framework or service is the user's decision, raised as a question, not written into an ADR.
- **Every FR and NFR must land somewhere** in the SAD or SDS. Before finishing, list any that land nowhere and report them.
- **Mermaid names** in `erDiagram` use only letters, digits and underscores. Edge labels and node text containing `(`, `)`, `:` or `/` must be wrapped in double quotes (`-->|"build_llm()"|`) — unquoted, the whole diagram fails to render.
- **Show both drafts before writing.** Let the user edit, then write the files.

## Finish

Report the two paths, any FR / NFR that landed nowhere, and the next step: write `docs/06-test-plan.md`, including its traceability matrix.

## Rationalization table

| Excuse | Reality |
| --- | --- |
| "React Query / an ORM would be cleaner" | `course/STACK.md` fixed the stack so that two days go to specs and tests. Ask; don't decide. |
| "The LLM can return the remaining balance too" | Then the balance is whatever the model says. Numbers and statuses come from code. |
| "Validation is an implementation detail" | It is the only thing between a prompt injection and the database. It goes in the information flow. |
