# BerTele2 AI Agent Template

This is a reusable prompt template for any AI coding agent working on BerTele2. Copy this prompt and fill in the placeholders.

---

## Prompt

You are an AI coding agent working on the **BerTele2** project. Follow the instructions below exactly.

### 1. Read the AI SDK

Before making any changes, read the following files in order:

1. `.ai/README.md` — overview and index.
2. `.ai/project.md` — vision and goals.
3. `.ai/architecture.md` — system architecture.
4. `.ai/development-rules.md` — mandatory rules.
5. `.ai/coding-standards.md` — style and conventions.
6. `.ai/module-map.md` — module details.
7. `.ai/roadmap.md` — current and future epics.

Consult the relevant files under `.ai/context/` for the subsystem you are modifying.

### 2. Execute the Epic

Your task is: **{{EPIC_DESCRIPTION}}**

- Follow the Epic template in `.ai/epic-template.md`.
- Implement one focused change at a time.
- Follow `.ai/development-rules.md` (no unrelated refactoring, use interfaces, dependency injection, no duplicated logic, no circular imports).
- Follow `.ai/coding-standards.md` (typing, docstrings, logging, error handling).
- Add tests for all new behavior. See `.ai/testing.md`.
- Update documentation (including the AI SDK) when behavior changes.

### 3. Report Changes

When finished, report:

- **Summary**: What was implemented.
- **Files changed**: List of files created/modified.
- **Tests**: What tests were added and their results.
- **Documentation**: What docs were updated.
- **Commit**: The commit message used.
- **Patch**: The patch file path.

### 4. Avoid Unrelated Modifications

- Do **not** refactor code unrelated to the Epic.
- Do **not** change formatting or style of unrelated code.
- Do **not** add features outside the Epic scope.
- If you find an issue, note it in the technical debt backlog (`.ai/roadmap.md`) and move on.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{EPIC_DESCRIPTION}}` | The description of the Epic to implement. |

---

## Related Documents

- [README.md](README.md) — AI SDK overview.
- [epic-template.md](epic-template.md) — Epic template.
- [workflow.md](workflow.md) — Development workflow.
- [review-checklist.md](review-checklist.md) — Review checklist.