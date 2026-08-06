# BerTele2 AI Development Kit (AI SDK)

The **AI Development Kit** is the authoritative documentation for the BerTele2 project. It is designed so that **any AI coding agent** (ChatGPT, Codex, Claude Code, Gemini CLI, Cline, RooCode, Amp, OpenHands, Cursor, Windsurf, Continue, etc.) can understand the project without prior knowledge.

This directory contains project intelligence and development guidance only. It does **not** add application features.

---

## Purpose

- Provide a single source of truth for project architecture, conventions, and workflows.
- Enable any AI agent to onboard quickly and contribute safely.
- Reduce the risk of unrelated refactoring, duplicated logic, and architectural drift.
- Document decisions (ADRs) so future changes are informed by history.

## Supported AI Agents

The SDK is agent-agnostic. It works with any agent that can:

- Read Markdown files.
- Execute git commands.
- Run tests and linters.
- Generate patches.

Examples: ChatGPT, Codex, Claude Code, Gemini CLI, Cline, RooCode, Amp, OpenHands, Cursor, Windsurf, Continue.

## How to Start a New Epic

1. Read [project.md](project.md) and [architecture.md](architecture.md) to understand the vision and system.
2. Read [roadmap.md](roadmap.md) to see what is planned and what is complete.
3. Read [development-rules.md](development-rules.md) and [coding-standards.md](coding-standards.md) before writing code.
4. Use the [epic-template.md](epic-template.md) to structure the Epic.
5. Follow [workflow.md](workflow.md) and [git-workflow.md](git-workflow.md) for implementation and delivery.
6. Consult [module-map.md](module-map.md) and the [context/](context/) files for subsystem details.
7. Review your work against [review-checklist.md](review-checklist.md) before finishing.

## How to Review Code

1. Read [review-checklist.md](review-checklist.md) for the full checklist.
2. Verify the change matches the Epic scope (no unrelated refactoring).
3. Confirm tests exist and pass (see [testing.md](testing.md)).
4. Confirm documentation is updated where relevant.
5. Use the [prompts/review-template.md](prompts/review-template.md) to structure the review.

## How to Generate Patches

1. Complete the Epic and commit it.
2. Generate the patch:

```bash
mkdir -p patches
git diff HEAD~1 HEAD > patches/epic-<id>.patch
```

3. Verify the patch applies cleanly on a fresh checkout.

## How to Contribute

1. Read [project.md](project.md) and [glossary.md](glossary.md).
2. Read [development-rules.md](development-rules.md) — these are mandatory.
3. Read [coding-standards.md](coding-standards.md) for style and typing.
4. Read [git-workflow.md](git-workflow.md) for branch and commit conventions.
5. Implement one Epic at a time. Keep changes focused.
6. Add or update tests. Run the full suite before finishing.
7. Update documentation (including this SDK) when behavior changes.
8. Generate a patch and submit it.

---

## Documentation Index

| Document | Purpose |
| --- | --- |
| [project.md](project.md) | Vision, mission, goals, users, platforms, philosophy |
| [architecture.md](architecture.md) | Complete system architecture with diagrams |
| [roadmap.md](roadmap.md) | Milestones, epics, releases, technical debt |
| [coding-standards.md](coding-standards.md) | Python style, typing, docstrings, logging, DI |
| [development-rules.md](development-rules.md) | Mandatory development rules |
| [workflow.md](workflow.md) | Design → implementation → review → release |
| [git-workflow.md](git-workflow.md) | Branching, commits, patches, versioning |
| [module-map.md](module-map.md) | Every module: purpose, deps, APIs, plans |
| [testing.md](testing.md) | Testing strategy and expectations |
| [release.md](release.md) | Release process and checklist |
| [review-checklist.md](review-checklist.md) | Code review checklist |
| [glossary.md](glossary.md) | Project terminology |
| [agent-template.md](agent-template.md) | Reusable prompt for AI agents |
| [epic-template.md](epic-template.md) | Reusable Epic template |
| [context/](context/) | Per-subsystem deep dives |
| [prompts/](prompts/) | Reusable prompt templates |
| [decisions/](decisions/) | Architecture Decision Records (ADRs) |