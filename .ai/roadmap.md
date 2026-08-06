# BerTele2 Roadmap

This document tracks milestones, epics, releases, and technical debt.

## Milestones

| Milestone | Status | Description |
| --- | --- | --- |
| M1 — Core Gateway | ✅ Complete | Session engine, Telegram engine, API, security |
| M2 — Media Pipeline | ✅ Complete | Media engine, storage providers, pipeline steps |
| M3 — Connectors | ✅ Complete | GoWA and n8n connectors |
| M4 — Dashboard | ✅ Complete | Overview, logs, metrics, WebSocket |
| M5 — AI SDK | 🚧 In Progress | This Epic (A0) |
| M6 — Automation Engine | 🔜 Planned | Workflow triggers, actions, conditions, scheduler |

## Epics

### Completed Epics

| Epic | Description | Patch |
| --- | --- | --- |
| Epic 14 | Core gateway foundation | `epic14.patch` |
| Epic 15 | Session management | `epic-15.patch` |
| Epic 16 | Telegram engine | `epic-16.patch` |
| Epic 17 | Media pipeline | `patches/epic-17.patch` |
| Epic 18 | Storage providers | `patches/epic-18.patch` |
| Epic 19 | GoWA media + connectors | `patches/epic-19.patch`, `patches/epic-19R.patch` |

### Current Epic

| Epic | Description | Status |
| --- | --- | --- |
| Epic A0 | AI Development Kit (AI SDK) | 🚧 In Progress |

### Future Epics

| Epic | Description |
| --- | --- |
| Epic A1 | Automation Engine — triggers and actions |
| Epic A2 | Automation Engine — scheduler and workflows |
| Epic A3 | Additional storage providers (S3, GCS) |
| Epic A4 | Worker pool for background tasks |
| Epic A5 | Multi-tenant isolation |
| Epic A6 | Additional connectors |

## Release Targets

| Version | Target | Contents |
| --- | --- | --- |
| 0.1.0 | Next | AI SDK, automation engine foundation |
| 0.2.0 | Later | Storage providers, worker pool |
| 1.0.0 | Future | Stable public API, multi-tenant |

## Technical Debt Backlog

- [ ] Replace in-memory user store with a persistent repository.
- [ ] Add integration tests for the full media pipeline.
- [ ] Add S3/GCS storage providers.
- [ ] Add rate limiting and concurrency controls to the automation engine.
- [ ] Add structured logging configuration for production.
- [ ] Add metrics collection for the dashboard (real data, not stubs).
- [ ] Add migration coverage for all models.

---

## Related Documents

- [project.md](project.md) — Vision and goals.
- [architecture.md](architecture.md) — System architecture.
- [release.md](release.md) — Release process.
- [module-map.md](module-map.md) — Module details.