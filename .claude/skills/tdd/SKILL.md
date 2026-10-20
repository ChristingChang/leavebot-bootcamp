---
name: tdd
description: 測試驅動開發，紅—綠—重構。當要以測試先行的方式建置功能或修 bug、當使用者提到 "TDD"、"red-green"、「紅綠」，或要求寫出能撐過重構的測試時使用。
---

# Test-Driven Development

Red → green → repeat, one behaviour at a time.

In this repo the behaviours are already named: each ticket lists the test cases (`TC-xx`) it turns green, and `docs/06-test-plan.md` says which layer each belongs to. Start from those.

## The loop

1. **Red** — write one failing test for the next behaviour. Run it. See it fail, and see it fail *for the reason you expect*. A test that passes before the code exists is testing nothing.
2. **Green** — the least code that passes it. Ugly is allowed here.
3. **Refactor** — clean up with the test holding the behaviour still. Optional; skip it when there is nothing to clean.

Never write all the tests up front. Batching them produces tests of *imagined* behaviour: they pin the shape you guessed at, and go numb to the shape you actually built. Each cycle should be informed by what the previous one taught you.

The first cycle is a **vertical slice** — one test proving a single path works end to end, before building outward.

## What a good test is

**Tested through the public interface.** Code should be able to change entirely without the tests moving. A test that breaks on a rename is a test of implementation.

**Named as a specification.** `user can check out with a valid cart` — reading the test names should tell you what the system does.

**Expected values from an independent source.** A known-good literal, a worked example, the spec. Never recomputed the way the code computes it — that test passes by construction and is **tautological**: it will pass just as happily when the code is wrong.

**One behaviour per test.** A test asserting five things fails without telling you which one broke.

## Seams

A **seam** is the boundary where behaviour is observable without reaching inside. Tests live at seams.

Pick the seam before the first test. Too deep and every refactor breaks the suite; too shallow and failures stop being diagnostic. The right seam is usually the interface another part of the system already calls.

The loop does not change at a module boundary. A test at the seam between two modules — real collaborators on both sides — is an integration test, written red-first like any other; the layer is a property of where the seam sits, not a different ritual.

Which seams deserve tests is a project decision, not a per-test guess. Take the layer from `docs/06-test-plan.md` and put the test under `backend/tests/<layer>/` (acceptance, system, integration, unit). The API section of `docs/05-sds.md` is usually the right seam for acceptance tests.

## Marking tests

Every test names the test case it implements and the requirement it verifies:

```python
@pytest.mark.req("TC-04", "AC-02.1")
def test_second_request_on_a_full_day_reminds_the_manager(client): ...
```

A test without a marker cannot be traced back to a requirement.

## Before you say the ticket is done

1. Run the full `.venv/bin/pytest` and paste the result.
2. Update the traceability matrix at the end of `docs/06-test-plan.md`: for each of this ticket's TCs, the test file and ✅. Only mark ✅ a TC whose marker you can show with `grep -rn 'mark.req("TC-xx"' backend/tests/`.
3. Add anything that drifted from the spec, any sentence of the spec you misread, and any environment trap to `docs/LESSONS.md`.

## Mocking

Default to **not** mocking. A test with four mocks is testing the mocks.

Mock only what you do not own and cannot make fast or deterministic: third-party network calls, the clock, randomness, the filesystem when it is genuinely slow. In this repo the LLM sits behind a seam you build: business code depends on a `complete(system, user) -> str` interface, and tests inject a fake implementation — never the real model (`course/STACK.md`). Your own modules are not on that list — if they are hard to use in a test, that is a design finding, not a mocking problem.

In-memory fakes beat mocks. A fake repository backed by a map exercises real logic; a mocked one asserts you called a method.

## Anti-patterns

- **Testing internals** — private functions, internal state. Rename-fragile, refactor-hostile.
- **Tautological tests** — expected value computed by the code under test.
- **Assertion-free tests** — "it runs without throwing" is not a specification.
- **Shared mutable fixtures** — order-dependent suites that pass alone and fail together.
- **Coverage as the goal** — coverage measures which lines ran, not which behaviours are pinned.

## Bugs

A bug fix starts with a test that reproduces it and goes red. Fix, watch it go green, keep the test. A fix without that test is a fix that comes back.
