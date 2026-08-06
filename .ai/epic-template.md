# BerTele2 Epic Template

Use this template to structure any Epic on BerTele2. Copy the template and fill in the placeholders.

---

# Epic {{EPIC_ID}}: {{EPIC_TITLE}}

## Overview

{{Brief description of the Epic and its purpose.}}

## Goal

{{The single, well-defined goal of this Epic.}}

## Scope

- {{In-scope item 1}}
- {{In-scope item 2}}

## Out of Scope

- {{Out-of-scope item 1}}
- {{Out-of-scope item 2}}

## Tasks

- [ ] {{Task 1}}
- [ ] {{Task 2}}
- [ ] {{Task 3}}

## Acceptance Criteria

- [ ] {{Criterion 1}}
- [ ] {{Criterion 2}}
- [ ] {{Criterion 3}}

## Documentation

- [ ] Update relevant docs in `.ai/`.
- [ ] Add ADR if a significant decision is made.

## Testing

- [ ] Unit tests for new behavior.
- [ ] Full suite passes (`pytest`).

## Commit

Commit message: `{{TYPE}}({{SCOPE}}): {{DESCRIPTION}}`

## Patch

```bash
mkdir -p patches
git diff HEAD~1 HEAD > patches/epic-{{EPIC_ID}}.patch
```

## Push

```bash
git push origin $(git branch --show-current)
```

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{EPIC_ID}}` | Epic identifier (e.g., A0, 20). |
| `{{EPIC_TITLE}}` | Short title. |
| `{{TYPE}}` | Commit type (`feat`, `fix`, `docs`, etc.). |
| `{{SCOPE}}` | Commit scope (e.g., `media`, `telegram`). |
| `{{DESCRIPTION}}` | Short commit description. |

---

## Related Documents

- [README.md](README.md) — AI SDK overview.
- [workflow.md](workflow.md) — Development workflow.
- [git-workflow.md](git-workflow.md) — Commit and patch conventions.
- [agent-template.md](agent-template.md) — AI agent prompt template.