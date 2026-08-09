# AI SDK Manifest

This manifest defines the version, compatibility, and required documents for the BerTele2 AI Development Kit (AI SDK).

## sdk_version

`TBD`

> No AI SDK version was defined before this Epic. The version will be set when the SDK reaches a stable release.

## architecture_version

`TBD`

> No architecture version was defined before this Epic. The version will be set when the architecture reaches a stable release.

## minimum_supported_agent

Any AI coding agent that can:

- Read Markdown files.
- Execute git commands.
- Run tests and linters.
- Generate patches.

## supported_agents

The AI SDK is **designed to be compatible with** the following agents. Compatibility is intended, not verified — no agent has been formally tested against this SDK.

| Agent | Status |
| --- | --- |
| ChatGPT | Designed to be compatible with |
| Codex | Designed to be compatible with |
| Claude Code | Designed to be compatible with |
| Gemini CLI | Designed to be compatible with |
| Cline | Designed to be compatible with |
| RooCode | Designed to be compatible with |
| Cursor | Designed to be compatible with |
| Windsurf | Designed to be compatible with |
| Continue | Designed to be compatible with |
| OpenHands | Designed to be compatible with |

## required_documents

The following documents are required reading for any AI agent working on BerTele2:

| Document | Purpose |
| --- | --- |
| [README.md](README.md) | AI SDK overview and index. |
| [project.md](project.md) | Vision, mission, goals, users, platforms, philosophy. |
| [architecture.md](architecture.md) | Complete system architecture with diagrams. |
| [roadmap.md](roadmap.md) | Milestones, epics, releases, technical debt. |
| [coding-standards.md](coding-standards.md) | Python style, typing, docstrings, logging, DI. |
| [development-rules.md](development-rules.md) | Mandatory development rules. |
| [workflow.md](workflow.md) | Design → implementation → review → release. |
| [git-workflow.md](git-workflow.md) | Branching, commits, patches, versioning. |
| [module-map.md](module-map.md) | Every module: purpose, deps, APIs, plans. |
| [testing.md](testing.md) | Testing strategy and expectations. |
| [release.md](release.md) | Release process and checklist. |
| [review-checklist.md](review-checklist.md) | Code review checklist. |
| [glossary.md](glossary.md) | Project terminology. |
| [agent-template.md](agent-template.md) | Reusable prompt for AI agents. |
| [epic-template.md](epic-template.md) | Reusable Epic template. |
| [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) | System prompt for AI agents. |
| [AI_CHANGELOG.md](AI_CHANGELOG.md) | AI SDK changelog. |
| [context/](context/) | Per-subsystem deep dives. |
| [prompts/](prompts/) | Reusable prompt templates. |
| [decisions/](decisions/) | Architecture Decision Records (ADRs). |

---

## Related Documents

- [README.md](README.md) — AI SDK overview.
- [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) — System prompt for AI agents.
- [AI_CHANGELOG.md](AI_CHANGELOG.md) — AI SDK changelog.