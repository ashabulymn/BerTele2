# Prompt Template: Documentation

Use this template to prompt an AI agent to write or update documentation.

---

## Prompt

You are an AI coding agent working on the **BerTele2** project.

### Task

Write/update documentation for: **{{DOC_TOPIC}}**

### Documentation Details

- **Topic**: {{DOC_TOPIC}}
- **Type**: {{DOC_TYPE}} (e.g., context file, ADR, module map, release notes)
- **Target file(s)**: {{TARGET_FILES}}

### Instructions

1. Read `.ai/README.md` for the documentation index.
2. Read the relevant `.ai/context/` files and source code for accuracy.
3. Follow the structure of existing docs in the same category.
4. Use Markdown with proper headings.
5. Use Mermaid diagrams where appropriate.
6. Cross-reference related documents.
7. Avoid duplicating information already documented elsewhere.
8. Keep the documentation accurate and up to date.

### Report

Report: summary, files written/updated, and any cross-references added.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{DOC_TOPIC}}` | The topic to document. |
| `{{DOC_TYPE}}` | Type of documentation. |
| `{{TARGET_FILES}}` | Files to write/update. |

---

## Related Documents

- [README.md](../README.md) — Documentation index.
- [glossary.md](../glossary.md) — Terminology.
- [architecture.md](../architecture.md) — System architecture.