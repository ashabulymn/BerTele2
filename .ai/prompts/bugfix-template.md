# Prompt Template: Bugfix

Use this template to prompt an AI agent to fix a bug.

---

## Prompt

You are an AI coding agent working on the **BerTele2** project.

### Task

Fix the following bug: **{{BUG_DESCRIPTION}}**

### Bug Details

- **Observed behavior**: {{OBSERVED_BEHAVIOR}}
- **Expected behavior**: {{EXPECTED_BEHAVIOR}}
- **Steps to reproduce**: {{REPRO_STEPS}}
- **Affected module(s)**: {{AFFECTED_MODULES}}

### Instructions

1. Read `.ai/README.md` and `.ai/agent-template.md` first.
2. Read the relevant `.ai/context/` files for the affected modules.
3. Reproduce the bug with a failing test.
4. Fix the bug with minimal, focused changes (no unrelated refactoring).
5. Ensure the new test passes and the full suite passes (`pytest`).
6. Update documentation (including the AI SDK) if behavior changed.
7. Commit with a conventional commit message (`fix(...)`).
8. Generate a patch: `git diff HEAD~1 HEAD > patches/fix-{{BUG_ID}}.patch`.

### Report

Report: root cause, fix description, tests added, files changed, commit message, and patch path.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{BUG_ID}}` | Bug identifier. |
| `{{BUG_DESCRIPTION}}` | Short bug description. |
| `{{OBSERVED_BEHAVIOR}}` | What happens currently. |
| `{{EXPECTED_BEHAVIOR}}` | What should happen. |
| `{{REPRO_STEPS}}` | Steps to reproduce. |
| `{{AFFECTED_MODULES}}` | Affected modules. |

---

## Related Documents

- [agent-template.md](../agent-template.md) — AI agent prompt template.
- [testing.md](../testing.md) — Testing strategy.
- [git-workflow.md](../git-workflow.md) — Commit conventions.