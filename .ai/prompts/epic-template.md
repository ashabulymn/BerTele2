# Prompt Template: Epic

Use this template to prompt an AI agent to implement an Epic.

---

## Prompt

You are an AI coding agent working on the **BerTele2** project.

### Task

Implement the following Epic: **{{EPIC_TITLE}}**

### Epic Description

{{EPIC_DESCRIPTION}}

### Instructions

1. Read `.ai/README.md` and `.ai/agent-template.md` first.
2. Read `.ai/project.md`, `.ai/architecture.md`, and `.ai/development-rules.md`.
3. Read the relevant `.ai/context/` files for the subsystems involved.
4. Follow `.ai/coding-standards.md` and `.ai/testing.md`.
5. Implement the Epic with focused changes only (no unrelated refactoring).
6. Add tests for all new behavior.
7. Update documentation (including the AI SDK) as needed.
8. Commit with a conventional commit message.
9. Generate a patch: `git diff HEAD~1 HEAD > patches/epic-{{EPIC_ID}}.patch`.

### Report

Report: summary, files changed, tests, documentation, commit message, and patch path.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{EPIC_ID}}` | Epic identifier. |
| `{{EPIC_TITLE}}` | Epic title. |
| `{{EPIC_DESCRIPTION}}` | Detailed Epic description. |

---

## Related Documents

- [agent-template.md](../agent-template.md) — AI agent prompt template.
- [epic-template.md](../epic-template.md) — Epic structure template.
- [workflow.md](../workflow.md) — Development workflow.