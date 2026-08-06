# Prompt Template: Review

Use this template to prompt an AI agent to review code changes.

---

## Prompt

You are an AI coding agent reviewing changes on the **BerTele2** project.

### Task

Review the following changes: **{{CHANGE_DESCRIPTION}}**

### Review Instructions

1. Read `.ai/review-checklist.md` for the full checklist.
2. Read `.ai/development-rules.md` and `.ai/coding-standards.md`.
3. Review the changes against the checklist:
   - Architecture (scope, interfaces, DI, no circular imports, no duplication).
   - SOLID principles.
   - Testing (unit tests, error paths, full suite).
   - Documentation (docstrings, AI SDK, ADRs, CHANGELOG).
   - Performance (no blocking I/O, no unbounded memory).
   - Security (no secrets, input validation, auth).
   - Maintainability (readability, naming, no dead code).
4. Report findings as: **Pass**, **Warn**, or **Fail** for each category.
5. Provide specific, actionable feedback.

### Report

Report: summary, per-category verdicts, and a list of required changes.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{CHANGE_DESCRIPTION}}` | Description of the changes to review. |

---

## Related Documents

- [review-checklist.md](../review-checklist.md) — Review checklist.
- [development-rules.md](../development-rules.md) — Mandatory rules.
- [coding-standards.md](../coding-standards.md) — Style and conventions.