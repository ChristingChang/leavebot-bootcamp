---
name: writing-hooks
description: 撰寫與審查 agent lifecycle hook：判斷何時需要機器攔截、如何保持安靜、測試決策與處理跨平台失敗。當要新增 hook 或排查 hook 沒擋住、誤擋、反覆噴訊息時使用。
---

# Writing Hooks

Reference for hooks that stay alive. `/writing-for-agents` covers documents the model reads; this covers the machine enforcement around it. Evidence for every rule here — three rot modes observed in a real project, with numbers — lives in [PATHOLOGY.md](PATHOLOGY.md); read it when you need to justify a rule, not to apply one.

## Tier placement: what deserves a hook

Agent instruction files are probabilistic — read, not guaranteed, and compliance decays as context grows. Place each rule by the cost of a violation:

| Rule kind | Belongs in | Why |
| --- | --- | --- |
| Taste, style, preference (naming, comment density) | Agent instructions / rules | A violation is ugly, not broken; machine enforcement costs more than it saves |
| Process order (test first, changelog before commit) | Docs + human review | Review catches it; exceptions are common, hard blocks would paralyze work |
| Irreversible or architecture-polluting actions (writing into a retired dir, bypassing the single entry point) | **Blocking hook, using the host's protocol** | Someone spends a day tracing it back; that rule cannot be probabilistic |
| Secrets, destructive commands, production operations | **Blocking hook, using the host's protocol** | One violation is an incident |

**The 10th-violation test**: if this rule is broken ten times, what does cleanup #10 cost? "Manual archaeology" → hook. "Fixed in passing during review" → keep it prose; every hook you add is one more thing that can rot.

## Silence discipline: where output goes

The three destinations look identical in shell and cost wildly differently:

| Destination | Cost | Use |
| --- | --- | --- |
| `>> logfile` | Zero — never enters the conversation | **Default.** Everything diagnostic |
| `>&2` (stderr) | Host-specific; may be shown on a block or treated as a hook error | Use only as the host's event contract requires, and say **what to do instead** |
| stdout | Host-specific; may be parsed or injected into context | Only when the event contract requires a structured response |

A hook has two legitimate forms: a **decider** (can block using the host's documented response) and an **observer** (writes logs without adding conversation noise). A hook that always allows and still talks taxes every tool call to say nothing. Status broadcasts ("hook fired", "done") are worse than waste — they make dead functionality look alive.

`tee` is stdout in disguise: it writes the file **and** stdout by definition. Write logs directly to a file when the host does not need to consume the output. Verify the target agent's event-specific stdout, stderr and exit-code contract before relying on them.

## Staying alive: every hook ships with its test

The three rot modes ([PATHOLOGY.md](PATHOLOGY.md)) share one root cause: nothing verified the hook still worked. Therefore:

- Each hook has a test that runs with the project's normal checks.
- The test feeds **real payloads** through the hook and asserts its **decisions** (allow/block), never just that it ran — running is the default, deciding is the function.
- Make paths independent of the current working directory. A test can copy the hook into a temporary fixture and control the conditions without adding test-only switches to production code.

A rule you cannot write a check for is a rule you should not encode as a hook — an unverified hook is worse than none, because it creates the illusion that someone is watching the door.

## Cross-platform execution

Hooks may run under Windows, WSL, Git Bash, macOS or Linux, sometimes with a different shell and working directory than the interactive session. Test on the actual host and shell. Three habits help:

1. **Handle expected errors explicitly.** In shell hooks, `set -e` can end the script before it records why. Check dependencies, path conversion and input parsing where they can fail.
2. **Choose failure behaviour deliberately.** A missing dependency must leave a diagnostic trace. Whether the operation proceeds or is blocked depends on the rule's risk and the host's contract; test that path.
3. **Resolve paths inside the execution environment.** Do not pass a Windows path to a WSL tool or assume the hook starts in the repository root. Quote paths and provide fallbacks for diagnostics such as timestamps.

## Structure: the four-layer skeleton

Order guards from cheapest to most expensive, exiting 0 early: dependency present → tool name matches → path in jurisdiction → only then read content and judge. Full annotated skeleton, the Write/Edit field gotcha (`.content` vs `.new_string`), and observability patterns (`jq -nc`, truncation with original length) are in [PATHOLOGY.md](PATHOLOGY.md).
