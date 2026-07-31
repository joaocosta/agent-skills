# Skills

Skills are under the `skills/` folder.

Whenever a new skill is created, add it to the list below with a relative link to its `SKILL.md` file and a simple description of what it does.

When a new skill includes maintained Python scripts or tests, add their paths to every applicable check in `dev/hooks/pre-commit` and to the Pyright `include` list in `pyproject.toml`. Run `dev/hooks/pre-commit` and resolve all failures before reporting completion.

When two or more skills are complementary or form a sequence, add a workflow section describing when and in what order to use them. Define the handoff artifacts and clarify what downstream skills should reuse rather than repeat. Add such a workflow only when the relationship arises; do not create speculative workflows.

## Skill index

- [agents-md-comparator](skills/agents-md-comparator/SKILL.md) — Compares two AGENTS.md instruction bundles through static analysis and isolated empirical Pi runs, producing evidence for human review.
- [beads-handoff](skills/beads-handoff/SKILL.md) — Converts a persisted design contract into validated, dependency-aware Beads issues without creating markdown execution artifacts.
- [grill-me](skills/grill-me/SKILL.md) — Stress-tests a proposal and persists a self-contained, implementation-ready design contract for a separate handoff session.
- [handoff](skills/handoff/SKILL.md) — Reads a persisted design contract and creates a self-contained implementation brief or finely scoped ordered Ralph-loop tasks.
- [mutation-testing-loop](skills/mutation-testing-loop/SKILL.md) — Runs one evidence-driven mutmut iteration, resolving only the highest-value survivor group that materially improves a Python project.

## Design-to-implementation workflow

1. Use [grill-me](skills/grill-me/SKILL.md) while material product or technical decisions remain unresolved. It writes `.agent-artifacts/<initiative-slug>/design.md` as the sole downstream design contract. The record includes settled decisions, durable codebase anchors, numbered acceptance criteria, constraints, risks, validation, and a dependency-aware implementation outline with independently verifiable seams.
2. Start a separate context and choose one packaging skill; do not carry over the design conversation. Use [handoff](skills/handoff/SKILL.md) for repository-local markdown execution artifacts, or [beads-handoff](skills/beads-handoff/SKILL.md) when the target repository has an active Beads workspace and issues should be the durable execution source of truth. Either skill must read the complete persisted record, verify its anchors against current repository state, and preserve settled decisions rather than repeat broad exploration or redesign them.
3. Choose exactly one packaging route and do not duplicate the same initiative across both systems. Handoff creates either one `handoff.md` or a Ralph package. Beads handoff creates a context-bounded executable DAG of one or more self-contained tasks; an epic is optional coordination metadata for a multi-task DAG, never its execution structure. In both paths, execution units have explicit dependencies, validation, completion boundaries, valid intermediate states, and complete acceptance-criteria coverage; downstream work reuses recorded prior outputs rather than rediscovering them.

