---
name: code-review
description: 沿 Standards（是否遵守專案規範）與 Spec（是否做到要求）兩條軸審查分支、PR、提交範圍或進行中的工作。當使用者要求 code review、「審一下」時使用。
---

# Code Review

Two-axis review of the change the user identifies: a branch, PR, commit range or current worktree.

- **Standards** — does the code conform to the current project's conventions?
- **Spec** — does it faithfully implement the originating ticket or spec?

Keep independent notes for the two axes so a standards preference does not masquerade as a missed requirement. Use separate reviewers when the task and available tools justify it; report the findings together.

## 1. Pin the fixed point

Use the exact range or PR the user named. For work in progress, include staged and unstaged changes as requested. If the comparison point is unclear and changes the review, ask before making findings against an assumed baseline.

Review the changed lines and the surrounding code they depend on, rather than judging only the file tree.

## 2. Standards axis

The repo's own documented standards win over everything below. Read `CLAUDE.md` / `AGENTS.md`, any `docs/` conventions, and — more reliable than either — the surrounding code.

Baseline smells, always checked, always reported as **judgement calls, never violations**:

- **Mysterious name** — the name does not say what it does
- **Duplicated code** — same logic in three places, about to drift
- **Feature envy** — a function more interested in another object's data than its own
- **Data clumps** — the same three parameters travelling everywhere together
- **Primitive obsession** — a domain concept carried as a bare string
- **Repeated switches** — the same branch on the same type, scattered
- **Shotgun surgery** — one change forcing edits across many files
- **Divergent change** — one file edited for unrelated reasons
- **Speculative generality** — abstraction for a case that does not exist
- **Message chains** — `a.b().c().d()`
- **Middle man** — a class that only delegates
- **Refused bequest** — a subclass that ignores most of what it inherits

A documented repo standard overrides any of these. Consistency beats a rule from a book.

## 3. Spec axis

Read the originating request, ticket or specification and any acceptance criteria it references. Check the change against them:

- Every *Done when* condition, literally — met, or not
- Required tests or other verification have actually run and exercise the promised behaviour; a checked box or passing badge alone is a claim, not evidence
- Project constraints on architecture, dependencies, external services and sensitive data are observed
- **Scope creep** — shipped things the spec did not ask for
- **Silent gaps** — spec items with no code
- **Reinterpretation** — built something adjacent to what was asked

## 4. Report

Side by side, most severe first. Each finding: file and line, one sentence on the defect, and the concrete failure — inputs or state, and what breaks.

Separate **must fix** from **judgement call**. A review where everything is urgent gets ignored wholesale.

Say plainly when an axis found nothing. Manufactured findings to look thorough cost more than they are worth.
