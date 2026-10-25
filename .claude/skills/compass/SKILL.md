---
name: compass
description: 問這個情況該用哪個技能、走哪條流程。依本專案現有技能、文件與票指出合適入口。
disable-model-invocation: true
---

# Compass

This repo ships the course's original ten skills plus four local adaptations: `grill-with-docs`, `to-spec`, `to-test-plan`, and `implement`. D1 writes six spec documents; D2 builds the app in five iterations. Tell the user which skill fits their present problem and what file it should leave behind. The sequence below is a course path, not a gate: bugs and new decisions can enter at any point.

**Respond in the session's language.** Check which of `docs/01-brief.md` … `docs/06-test-plan.md`, `docs/LESSONS.md` and `issues/` already exist before answering — the next step is the first thing that is missing. The repo starts empty on purpose: everything outside `course/` and the config files is something the user builds.

## D1 — the spec chain (left side of the V)

| Step | Skill | Leaves behind (format) |
| --- | --- | --- |
| 1. Why build it: pain, goals, non-goals | **`/grilling`**; when working from existing docs, **`/grill-with-docs`** | Decisions for `docs/01-brief.md` |
| 2. For whom, what: persona, user flow, epic, story, BDD | **`/grilling`** or **`/grill-with-docs`** (same session) | Decisions for `docs/02-prd.md` |
| 3. Turn settled decisions into Brief, PRD, SRS | **`/to-spec`** | `docs/01-brief.md` … `docs/03-srs.md` using course templates |
| 4. How it fits together: C4, information flow, ADR | **`/to-architecture`** | `docs/04-sad.md` |
| 5. How each piece works: ER, API, screens, modules | **`/to-architecture`** (same run) | `docs/05-sds.md` |
| 6. How it will be verified: test cases, eval threshold, traceability matrix | **`/to-test-plan`** | `docs/06-test-plan.md` |
| 7. Project rules and lessons | **`/writing-for-agents`** | the 本專案 half of `AGENTS.md`; `docs/LESSONS.md` (`course/templates/LESSONS.md`) |
| 8. Split the build into iterations I0–I4 | **`/to-tickets`** | `issues/NNN-<slug>.md` |

After step 6, the traceability matrix at the end of `docs/06-test-plan.md` should list every AC / FR / NFR with a TC. A requirement missing from it is a gap.

## D2 — from zero to a working app (right side of the V)

| Iteration | Skill | Done when |
| --- | --- | --- |
| I0 skeleton: `backend/`, `frontend/`, `pyproject.toml`, `dev.sh` per `course/STACK.md` | **`/implement`** on the I0 ticket | `bash dev.sh` serves the frontend, which reads `/api/health`; Ctrl+C frees both ports |
| I1–I3 one ticket at a time | **`/implement`**, using **`/tdd`** for testable behaviour | the ticket's test cases go red, then green, each test marked `@pytest.mark.req(...)` |
| A test goes red and the cause is not obvious | **`/diagnosing-bugs`** | a reproducing test, one hypothesis at a time, then the fix |
| End of each iteration | — | ask the agent to click through the PRD user flow with the **playwright** MCP |
| Before merging an iteration | **`/code-review`** | a review a human accepts or rejects line by line |
| I4 verify the AI itself | — | an eval script the agent generates from the test plan's comparison rules passes `--min <threshold>`; injection test cases pass |
| Another teammate or tool takes over | **`/handoff`** | a file the next session starts from |
| A rule that must never be broken | **`/writing-hooks`** | a hook in `.claude/hooks/`, registered in both tools |

Finish with the traceability matrix: no AC / FR / NFR without a TC, no TC without a test file, three rows spot-checked by a human.

`/compass`, `/grill-with-docs`, `/to-spec`, `/to-architecture`, `/to-test-plan`, `/to-tickets`, `/implement` and `/handoff` are **user-triggered**: the user types them. Do not warn that they are missing — check `.claude/skills/<name>/SKILL.md` if in doubt. `/feasibility` is shown as an optional upstream idea in the diagram but is not installed here.

An open question at any step goes back to **`/grilling`**, never to a guessed default.

## Context hygiene

- D1 steps 1–2 stay in **one session**; steps 4–5 too. The later document needs the earlier reasoning verbatim, not a summary.
- Between tickets on D2, **`/clear`**. Each ticket is self-contained; everything it needs is in `docs/`, `docs/LESSONS.md` and the ticket.
- A session getting long mid-step: finish the step, then `/compact` with an instruction (`/compact next we build ticket 002`).

## Built-in commands, not skills

`/clear`, `/compact` and `/init` belong to Claude Code itself — and do not run `/init` here, it would overwrite the project's agent rules. In Codex, skills are called with `$name` (`$grilling`), and its own review command is `/review`.

## When the output disagrees with the handout

That is expected — models hallucinate. Align in this order: the spec (`docs/`, `course/STACK.md`), then the measures (tests, eval, the traceability matrix), then the instructor. Record the drift in `docs/LESSONS.md`.

## Where the boundaries live

`AGENTS.md` holds the rules (factory half on top, project half below); `course/STACK.md` fixes the stack and the one fixed API (`POST /api/parse`); `.claude/hooks/` blocks dangerous git commands whatever the agent decides; `.mcp.json` adds context7 (current docs) and playwright (a browser); `course/HARNESS.md` explains which file does what.
