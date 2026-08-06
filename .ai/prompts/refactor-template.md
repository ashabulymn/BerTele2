# Prompt Template: Refactor

Use this template to prompt an AI agent to refactor code.

---

## Prompt

You are an AI coding agent working on the **BerTele2** project.

### Task

Refactor the following: **{{REFACTOR_DESCRIPTION}}**

### Refactor Details

- **Target module(s)**: {{TARGET_MODULES}}
- **Goal**: {{REFACTOR_GOAL}}
- **Constraints**: {{CONSTRAINTS}}

### Instructions

1. Read `.ai/README.md` and `.ai/agent-template.md` first.
2. Read the relevant `.ai/context/` files for the target modules.
3. Preserve **public behavior** — no breaking changes.
4. Keep changes focused on the refactor goal (no unrelated changes).
5. Ensure all existing tests pass (`pytest`).
6. Add tests if new behavior is introduced.
7. Update documentation (including the AI SDK) as needed.
8. Commit with a conventional commit message (`refactor(...)`).
9. Generate a patch: `git diff HEAD~1 HEAD > patches/refactor-{{REFACTOR_ID}}.patch`.

### Report

Report: summary, files changed, tests, documentation, commit message, and patch path.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{REFACTOR_ID}}` | Refactor identifier. |
| `{{REFACTOR_DESCRIPTION}}` | Short refactor description. |
| `{{TARGET_MODULES}}` | Modules to refactor. |
| `{{REFACTOR_GOAL}}` | The goal of the refactor. |
| `{{CONSTRAINTS}}` | Any constraints (e.g., no API changes). |

---

## Related Documents

- [agent-template.md](../agent-template.md) — AI agent prompt template.
- [development-rules.md](../development-rules.md) — Mandatory rules.
- [testing.md](../testing.md) — Testing strategy.