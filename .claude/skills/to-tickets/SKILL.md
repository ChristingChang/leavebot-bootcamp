---
name: to-tickets
description: 把需求與架構切成一張張垂直切片票，寫進 issues/，每張都標明驗收指令與被誰擋住。
disable-model-invocation: true
---

# To Tickets

Split the work into tickets an agent can pick up cold, one per session. Material: `1_requirements.md`, `2_architecture.md`, and the conversation.

## Vertical slices, not layers

Every ticket is a **vertical slice**: something observably works when it is done. Never "add the database schema", "add the API layer", "add the UI" — three tickets, and nothing works until all three land, so nothing can be reviewed or reverted independently.

The first ticket is the **thinnest path that runs end to end**. It is allowed to be embarrassing — one hardcoded sentence, no error handling. Its job is to prove the seams line up. Everything after it widens that path.

## Sizing

One ticket = one fresh context window, about two hours for one person. If it needs more, split it. If three of them are one-liners, merge them.

The test for a good ticket: **could an agent that has never seen this conversation do it from the ticket alone?** If it needs the conversation, the ticket is underspecified.

## Blocking edges

Each ticket names what must be done before it. Real dependencies only — "B needs the table A creates" is an edge; "B feels like it comes after A" is not. Invented edges serialise work that could have run in parallel.

## Where they go

One file per ticket: `issues/NNN-<slug>.md`, numbered from `001`. Ticket shape:

```markdown
# <verb the outcome: "Parse one hardcoded sentence into a leave request">

## Done when
Observable conditions, at least one of them a command someone can run in a
terminal (a pytest selection, a curl). Someone else must be able to check
these without reading the implementation.

## Context
The one paragraph of background needed to start. Point at the section of
2_architecture.md, do not restate it.

## Blocked by
001 — or "nothing".

## Notes
Traps, decided-against alternatives, the seam to test at.
```

## Rules

- **Show the full set before writing files** — the sizing and the edges are much easier to judge as a list than one at a time.
- **No ticket decides what the spec left open.** Put the open question in the ticket's Notes and flag it to the user.

## Finish

Report the paths and the blocking order, and say: build each ticket with `/tdd`, **`/clear`ing context between tickets** — each ticket is self-contained, so the last one's context is disposable.
