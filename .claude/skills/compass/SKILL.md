---
name: compass
description: 問這個情況該用哪個技能、走哪條流程。上課用的 6 個技能的路由器。
disable-model-invocation: true
---

# Compass

This repo ships six skills, one per step of the bootcamp. Tell the user which one fits where they are now, and what file it should leave behind.

**Respond in the session's language.**

## The flow: idea → reviewed code

| Step | Skill | Leaves behind | Day |
| --- | --- | --- | --- |
| 1. Sharpen the requirement by interview | **`/grilling`** | answers that become `1_requirements.md` (format: `templates/1_requirements_template.md`) | Day 1 |
| 2. Settle the skeleton: boundaries, data model, API | **`/to-architecture`** | `2_architecture.md` (format: `templates/2_architecture_template.md`) | Day 2 |
| 3. Split the work into vertical slices | **`/to-tickets`** | `issues/NNN-<slug>.md`, one per ticket | Day 2 |
| 4. Build one ticket, test first | **`/tdd`** | a red test, then the code that turns it green | Day 3 / self-study |
| 5. Review the change before it lands | **`/code-review`** | a review report a human then accepts or rejects line by line | Day 3 |

`/compass`, `/to-architecture` and `/to-tickets` are **user-triggered**: the user types them, and they are deliberately absent from your own list of skills. Do not warn that they are missing — check `.claude/skills/<name>/SKILL.md` if in doubt.

Skip a step only when its file already exists and nobody disputes it. An open question at any step goes back to **`/grilling`**, never to a guessed default.

## Context hygiene

- Steps 1–3 stay in **one unbroken session**: the architecture and the tickets need the interview's reasoning verbatim, not a summary of it.
- Between tickets in step 4, **`/clear`**. Each ticket is self-contained; the last one's context is disposable.
- A session getting long mid-step: finish the step, then `/compact` with an instruction (`/compact next we build ticket 002`). Compacting mid-step makes the agent lose the thread.

## Built-in commands, not skills

`/clear`, `/compact` and `/init` belong to Claude Code itself. In Codex, skills are called with `$name` (`$grilling`), and its own review command is `/review`.

## Where the red lines live

`AGENTS.md` holds the project's rules; `.claude/hooks/` blocks the dangerous git commands whatever the agent decides. To stop the agent finishing while tests are red, install `templates/hooks/pytest-on-stop.sh` (Day 3).
