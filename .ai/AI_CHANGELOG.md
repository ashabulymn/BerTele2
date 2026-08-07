# AI SDK Changelog

This changelog tracks every change to the **BerTele2 AI Development Kit (AI SDK)** — the documentation, architecture definitions, development rules, and configuration models under `.ai/`. It is maintained **separately** from the application `CHANGELOG.md`.

All notable changes to the AI SDK are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-08-08

### Added

- **AI SDK Manifest** (`AI_MANIFEST.md`): Defines `sdk_version`, `architecture_version`, `minimum_supported_agent`, `supported_agents`, and `required_documents`.
- **System Prompt** (`SYSTEM_PROMPT.md`): Consolidates global development rules, architecture rules, scope rules, quality gates, coding rules, and review workflow into a single authoritative reference for AI agents.
- **AI SDK Changelog** (`AI_CHANGELOG.md`): This file, tracking AI SDK changes separately from the application changelog.
- **GoWA Architecture Documentation** (`context/gowa.md`): Documents the GoWA authentication model (Connection = host + username + password), device model (`device_id`), node model (nodes store only `device_id` and `chat_id`), and the architecture diagram (GoWA Connection → Connector → Device → Workflow Node → Media Sender).
- **GoWA Development Rules** (`development-rules.md`): Adds mandatory rules that GoWA authentication belongs to the Connector, workflow nodes store only `device_id` and `chat_id`, and authentication credentials must never appear inside workflow definitions.
- **Quality Gates** (`SYSTEM_PROMPT.md`): Explicitly defines the five mandatory quality gates: Unit Tests, Scope Verification, Git Verification, Patch Verification, and Final Self Review.
- **Compatibility Matrix** (`README.md`): Adds a compatibility table listing supported AI agents (ChatGPT, Codex, Claude Code, Gemini CLI, Cline, RooCode, Cursor, Windsurf, Continue, OpenHands).

### Changed

- **GoWA Context** (`context/gowa.md`): Updated with authentication model, device model, node model, and architecture diagram sections. Added cross-references to `AI_MANIFEST.md`, `SYSTEM_PROMPT.md`, and `AI_CHANGELOG.md`.
- **Development Rules** (`development-rules.md`): Added "GoWA Authentication & Node Model" section with mandatory rules. Added cross-reference to `context/gowa.md`.

### Notes

- This Epic (A1) is **documentation-only**. No application code, APIs, or connectors were modified.

---

## [Unreleased]

---

## Related Documents

- [README.md](README.md) — AI SDK overview and index.
- [AI_MANIFEST.md](AI_MANIFEST.md) — SDK manifest.
- [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) — System prompt for AI agents.
- [../../CHANGELOG.md](../../CHANGELOG.md) — Application changelog.