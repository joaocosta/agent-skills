# Skills

Skills are under the `skills/` folder.

Whenever a new skill is created, add it to the list below with a relative link to its `SKILL.md` file and a simple description of what it does.

When two or more skills are complementary or form a sequence, add a workflow section describing when and in what order to use them. Define the handoff artifacts and clarify what downstream skills should reuse rather than repeat. Add such a workflow only when the relationship arises; do not create speculative workflows.

## Skill index

- [grill-me](skills/grill-me/SKILL.md) — Stress-tests a proposal through a rigorous design interview and produces an implementation-ready design record.
- [handoff](skills/handoff/SKILL.md) — Converts established context and design artifacts into self-contained implementation handoffs or ordered Ralph-loop tasks.

## Design-to-implementation workflow

1. Use [grill-me](skills/grill-me/SKILL.md) while material product or technical decisions remain unresolved. Its handoff artifact is the self-contained design record containing settled decisions, codebase anchors, acceptance criteria, risks, and blockers.
2. Use [handoff](skills/handoff/SKILL.md) when the design is ready to transfer to a fresh implementation session. Reuse the design record and its references; do not repeat broad exploration or reopen settled decisions. Split work into ordered tasks only when it cannot fit coherently in one session.

