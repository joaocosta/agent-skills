# Skills

Skills are under the `skills/` folder.

Whenever a new skill is created, add it to the list below with a relative link to its `SKILL.md` file and a simple description of what it does.

When two or more skills are complementary or form a sequence, add a workflow section describing when and in what order to use them. Define the handoff artifacts and clarify what downstream skills should reuse rather than repeat. Add such a workflow only when the relationship arises; do not create speculative workflows.

## Skill index

- [grill-me](skills/grill-me/SKILL.md) — Stress-tests a proposal and persists a self-contained, implementation-ready design contract for a separate handoff session.
- [handoff](skills/handoff/SKILL.md) — Reads a persisted design contract and creates a self-contained implementation brief or finely scoped ordered Ralph-loop tasks.

## Design-to-implementation workflow

1. Use [grill-me](skills/grill-me/SKILL.md) while material product or technical decisions remain unresolved. It writes `.agent-artifacts/<initiative-slug>/design.md` as the sole downstream design contract. The record includes settled decisions, durable codebase anchors, numbered acceptance criteria, constraints, risks, validation, and a dependency-aware implementation outline with independently verifiable seams.
2. Start a separate context for [handoff](skills/handoff/SKILL.md), supplying the repository and path to `design.md`; do not carry over the design conversation. Handoff must read the complete persisted record, verify its anchors against current repository state, and preserve settled decisions rather than repeat broad exploration or redesign them.
3. Choose exactly one execution shape per initiative: for one session, add `handoff.md`; for a Ralph loop, add `README.md`, `progress.md`, executable `loop.sh`, and ordered prompts under `tasks/`. Ralph tasks recursively refine the implementation outline into one-outcome, fresh-context-sized units with explicit dependencies, validation, completion boundaries, valid intermediate states, and complete acceptance-criteria coverage. Downstream tasks reuse prior outputs recorded in `progress.md` rather than rediscovering or recreating them. Each iteration updates progress, creates a Conventional Commit, and reports its outcome; the final iteration creates `ralph-complete` so `loop.sh` can stop.

