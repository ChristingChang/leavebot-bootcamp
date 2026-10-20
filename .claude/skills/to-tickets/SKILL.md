---
name: to-tickets
description: 把六份規格切成 D2 的五個疊代票（I0–I4），寫進 issues/，每張都引用它要讓哪些 TC 變綠。
disable-model-invocation: true
---

# To Tickets

Split the build into the course's five iterations, one ticket each, that an agent can pick up cold in a fresh session. Material: `docs/01-brief.md` … `docs/06-test-plan.md`, `course/STACK.md`, `course/LEAVEBOT.md`.

## The five iterations

| Ticket | Iteration | Scope |
| --- | --- | --- |
| `issues/000-i0-skeleton.md` | I0 skeleton | `backend/`, `frontend/`, `pyproject.toml` and `dev.sh` exactly as `course/STACK.md` describes; `GET /api/health`; `bash dev.sh` serves both and Ctrl+C frees both ports. No business logic |
| `issues/001-i1-first-slice.md` | I1 vertical slice | the LLM client behind a fake-able seam (API only, per `course/STACK.md`); one sentence → `POST /api/parse` → preview → submit → "my requests" list. The thinnest path that runs end to end |
| `issues/002-i2-rules.md` | I2 rules | the rule checks the SRS assigns to code (annual-leave balance, same-day headcount reminder) |
| `issues/003-i3-approval.md` | I3 approval | the manager screen and the status transitions |
| `issues/004-i4-ai-acceptance.md` | I4 verify the AI | an eval script built from the test plan's comparison rules, run against `course/fixtures/`, at the test plan's threshold; the prompt-injection test cases |

Every ticket after I0 is a **vertical slice**: something observably works when it is done, front to back. Never "the database layer" or "the API layer".

## Ticket shape

```markdown
# <I1: verb the outcome>

## Test cases this ticket turns green
TC-01, TC-04 — copied from docs/06-test-plan.md with the requirement each verifies.

## Done when
- those test cases pass, each test marked @pytest.mark.req("TC-xx", ...)
- a command someone else can run (pytest selection, curl, or a click path on the dev server)
- the traceability matrix in docs/06-test-plan.md shows these TCs with their test files

## Context
The sections of docs/05-sds.md this touches (API IDs, screens, modules). Point, do not restate.

## Blocked by
000 — or "nothing".

## Notes
Traps, decided-against alternatives, the seam to test at.
```

## Rules

- **Every TC in the test plan lands in exactly one ticket.** List any that land nowhere — they are either missing scope or belong in "不測什麼".
- **No ticket decides what the spec left open.** Put the question in Notes and flag it to the user.
- **Show the full set before writing files.** Sizing is easier to judge as a list.

## Finish

Report the paths and say: build each ticket with `/tdd`, **`/clear`ing context between tickets**; each ticket ends with the traceability matrix and `docs/LESSONS.md` updated.
