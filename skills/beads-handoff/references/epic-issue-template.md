## Outcome and current state

{{Initiative outcome, verified repository state, authoritative design path, and why decomposition is required.}}

## Success criteria

{{Initiative-level observable success criteria with complete design AC-ID coverage.}}

## Required reading and anchors

{{Ordered source design, durable code, tests, documentation, and prerequisite issue anchors.}}

## Scope and owned components

{{Aggregate scope and ownership boundaries for the task DAG.}}

## Non-goals

{{Explicit initiative exclusions.}}

## Settled decisions and constraints

{{Cross-cutting decisions, invariants, compatibility constraints, and rationale that no child may reopen.}}

## Work breakdown and dependency DAG

{{List topological layers and each child issue ID with its outcome. Then list every direct edge exactly as `<blocked-id> depends on <prerequisite-id> — <required output and reason>`. State which children can run in parallel. Populate with live IDs after child creation.}}

## Design coverage

{{Map every implementation-outline unit, design AC ID, constraint, risk control, migration or operational requirement, and validation obligation to child issue IDs.}}

## Final validation

{{Exact cross-cutting commands, inspections, and expected evidence required before closing the epic.}}

## Risks and assumptions

{{Accepted cross-cutting risks and non-blocking assumptions, or `None`.}}

## Completion boundary and done condition

{{Required child state, final evidence, coherent repository state, and deliberately excluded work.}}

## Execution protocol

Start with `bd ready`; inspect and atomically claim one runnable child. Record exact outputs, validation, discoveries, and blockers in Beads. Close a child only after its done condition passes. Create and link discovered follow-up work instead of hiding it in prose. Close this epic only after every child and final validation succeed. Follow the repository's active profile for commits and synchronization.
