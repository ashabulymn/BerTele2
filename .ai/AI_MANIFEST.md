# AI SDK Manifest

This manifest defines the version, compatibility, and required documents for the BerTele2 AI Development Kit (AI SDK).

## sdk_version

`1.0.0`

## architecture_version

`1.0`

## minimum_supported_agent

Any AI coding agent that can:

- Read Markdown files.
- Execute git commands.
- Run tests and linters.
- Generate patches.

## supported_agents

| Agent | Status |
| --- | --- |
| ChatGPT | ✅ Supported |
| Codex | ✅ Supported |
| Claude Code | ✅ Supported |
| Gemini CLI | ✅ Supported |
| Cline | ✅ Supported |
| RooCode | ✅ Supported |
| Cursor | ✅ Supported |
| Windsurf | ✅ Supported |
| Continue | ✅ Supported |
| OpenHands | ✅ Supported |

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