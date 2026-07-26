# Durable audit events design

**Initiative:** audit-events
**Status:** ready for handoff
**Artifact path:** `.agent-artifacts/audit-events/design.md`

## Goal

Add durable JSONL audit-event persistence, a query API, and operator documentation to the existing TypeScript service.

## Current repository anchors

- `src/audit.ts` contains the existing public `AuditEvent` interface.
- No package metadata, persistence code, query API, tests, or operator documentation exists.

## Settled decisions

- Preserve `AuditEvent` and extend it with `timestamp`, `actor`, and `action` string fields.
- Store one JSON object per line under a configurable data directory.
- Appends must be serialized within one process and create the directory when absent.
- Query supports inclusive UTC start/end timestamps and optional exact actor matching.
- Malformed persisted lines are skipped and counted in a returned warning count.
- Tests use temporary directories and no production data.
- Operator documentation covers configuration, retention responsibility, malformed-line behavior, and backup/restore.

## Constraints and non-goals

- Standard library only for persistence.
- No cross-process locking, database, HTTP transport, authentication, or automated retention.
- Every intermediate task must keep prior tests passing.

## Acceptance criteria

- **AC1:** Events append as valid JSONL and concurrent in-process calls do not interleave bytes.
- **AC2:** Query filters inclusively by UTC range and exact actor and returns malformed-line warning count.
- **AC3:** Tests cover directory creation, append ordering, filtering boundaries, and malformed lines using temporary directories.
- **AC4:** Operator documentation explains configuration, retention ownership, malformed records, and backup/restore.
- **AC5:** A clean install, typecheck, and complete test suite pass without external services.

## Validation

Use repository-defined install, typecheck, and test commands. Inspect fixtures for production data and run a clean end-to-end test after all capabilities exist.

## Dependency-aware implementation outline

1. Establish package/test/typecheck scaffolding and implement the append-only store with focused tests.
2. Reuse the store parser to implement query behavior and focused boundary/malformed-line tests.
3. Add operator documentation and run clean end-to-end validation against AC1–AC5.

## Risks and assumptions

Cross-process write safety is explicitly accepted as out of scope. File growth is operator-managed and must be documented.
