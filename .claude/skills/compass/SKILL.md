---
name: compass
description: 問這個情況該用哪個技能、走哪條流程。上課用的 6 個技能的路由器。
disable-model-invocation: true
---

# Compass

This repo ships six skills for a two-day course: D1 writes six spec documents, D2 builds the app from zero in five iterations. Tell the user where they are now, which skill fits, and what file it should leave behind.

**Respond in the session's language.** Check which of `docs/01-brief.md` … `docs/06-test-plan.md` and `issues/` already exist before answering — the next step is the first thing that is missing.

## D1 — the spec chain (left side of the V)

| Step | Skill | Leaves behind (format) |
| --- | --- | --- |
| 1. Why build it: pain, goals, non-goals | **`/grilling`** | `docs/01-brief.md` (`templates/01-brief.md`) |
| 2. For whom, what: persona, user flow, epic, story, BDD | **`/grilling`** (same session) | `docs/02-prd.md` (`templates/02-prd.md`) |
| 3. What "done" means: use case, FR, NFR | — fill the template with the agent | `docs/03-srs.md` |
| 4. How it fits together: C4, information flow, ADR | **`/to-architecture`** | `docs/04-sad.md` |
| 5. How each piece works: ER, API, screens, modules | **`/to-architecture`** (same run) | `docs/05-sds.md` |
| 6. How it will be verified: test cases, eval threshold | — fill the template with the agent | `docs/06-test-plan.md` |
| 7. Split the build into iterations I0–I4 | **`/to-tickets`** | `issues/NNN-<slug>.md` |

After each document, run `.venv/bin/python scripts/trace.py`: it shows which requirements have no test case yet.

## D2 — from zero to a working app (right side of the V)

| Iteration | Skill | Done when |
| --- | --- | --- |
| I0 skeleton: `backend/` + `frontend/` per `STACK.md` | — | `bash scripts/dev.sh` serves the frontend, which reads `/api/health` |
| I1–I3 one ticket at a time | **`/tdd`** | the ticket's test cases go red, then green, each test marked `@pytest.mark.req(...)` |
| Before merging an iteration | **`/code-review`** | a review a human accepts or rejects line by line |
| I4 verify the AI itself | — | `.venv/bin/python scripts/run_eval.py --min <threshold>` passes; injection test cases pass |

Finish with `.venv/bin/python scripts/trace.py --strict`.

`/compass`, `/to-architecture` and `/to-tickets` are **user-triggered**: the user types them, and they are deliberately absent from your own list of skills. Do not warn that they are missing — check `.claude/skills/<name>/SKILL.md` if in doubt.

An open question at any step goes back to **`/grilling`**, never to a guessed default.

## Context hygiene

- D1 steps 1–2 stay in **one session**; steps 4–5 too. The later document needs the earlier reasoning verbatim, not a summary.
- Between tickets on D2, **`/clear`**. Each ticket is self-contained; everything it needs is in `docs/` and the ticket.
- A session getting long mid-step: finish the step, then `/compact` with an instruction (`/compact next we build ticket 002`).

## Built-in commands, not skills

`/clear`, `/compact` and `/init` belong to Claude Code itself — and do not run `/init` here, it would overwrite the project's agent rules. In Codex, skills are called with `$name` (`$grilling`), and its own review command is `/review`.

## Where the boundaries live

`AGENTS.md` holds the rules; `STACK.md` fixes the stack and the one fixed API (`POST /api/parse`); `.claude/hooks/` blocks dangerous git commands whatever the agent decides; `HARNESS.md` explains which file does what.
