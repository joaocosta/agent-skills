# Rate-limit configuration design

**Initiative:** rate-limit
**Status:** ready for handoff
**Artifact path:** `.agent-artifacts/rate-limit/design.md`

## Goal

Replace the hard-coded disabled rate limiter with one environment-backed boolean configuration function.

## Current repository anchors

- `src/rate-limit.ts` exports `rateLimitEnabled()` and currently always returns `false`.
- There is no test harness yet.

## Settled decisions

- Read `RATE_LIMIT_ENABLED` when the function is called.
- Only the case-insensitive value `true` enables the limiter; absent or other values disable it.
- Keep the existing exported function and add no dependencies.

## Non-goals

No numeric thresholds, config-file support, logging, or deployment changes.

## Acceptance criteria

- **AC1:** `rateLimitEnabled()` returns true only for case-insensitive `true`.
- **AC2:** Tests cover true, false, absent, and malformed values without leaking process state.

## Validation

Add the smallest repository-native test harness, run its test command, and run any available typecheck.

## Implementation outline

1. Add focused tests around the existing export.
2. Implement environment parsing in the existing module.

## Risks and assumptions

The repository is intentionally minimal. Choosing a lightweight test harness is implementation discretion.
