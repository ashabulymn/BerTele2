# Prompt Template: Release

Use this template to prompt an AI agent to prepare a release.

---

## Prompt

You are an AI coding agent working on the **BerTele2** project.

### Task

Prepare a release for version **{{VERSION}}**.

### Release Details

- **Version**: {{VERSION}}
- **Milestone**: {{MILESTONE}}
- **Included Epics**: {{EPICS}}

### Instructions

1. Read `.ai/release.md` for the release process.
2. Read `.ai/roadmap.md` for milestone details.
3. Verify all Epics in the milestone are complete.
4. Run the full test suite (`pytest`) and confirm it passes.
5. Update `CHANGELOG.md` with release notes.
6. Bump the version in `pyproject.toml`.
7. Verify migration scripts are generated and reviewed.
8. Create a release branch and tag.
9. Write release notes.

### Report

Report: version, milestone, tests result, CHANGELOG summary, tag, and release notes.

---

## Placeholders

| Placeholder | Description |
| --- | --- |
| `{{VERSION}}` | Version to release (e.g., 0.1.0). |
| `{{MILESTONE}}` | Milestone name. |
| `{{EPICS}}` | List of included Epics. |

---

## Related Documents

- [release.md](../release.md) — Release process.
- [roadmap.md](../roadmap.md) — Milestones and epics.
- [git-workflow.md](../git-workflow.md) — Versioning and branching.