# {{Initiative}} — Ralph execution

## Objective

{{Overall implementation objective and statement that design.md is authoritative while progress.md is execution state. Explain that each task file is one fresh iteration prompt and advancement requires its done condition to pass.}}

## Verified starting state

{{Current repository evidence, prerequisite outputs, and opposite-shape check.}}

## Ordered tasks

1. [`task-01-{{slug}}.md`](./tasks/task-01-{{slug}}.md) — {{one outcome}}.

## Dependency graph

```text
01
```

{{Explain dependencies and reusable outputs.}}

## Cross-task constraints

{{Settled constraints, invariants, non-goals, safety rules, and valid-intermediate-state requirements shared by tasks.}}

Treat `progress.md` as the loop's machine-readable routing state. After each attempt, choose `Next task` from tasks whose prerequisites are complete and which are not blocked. A blocked task does not prevent independent runnable work: record its concrete evidence and route to another runnable task. If no runnable task remains, set `Next task` to `none`; set the initiative to `blocked` when blockers remain, or `complete` only when every task is complete. Never route back to a blocked task unless new external evidence or a recorded resolution makes it runnable.

## Coverage map

| Design obligation | Owning task(s) |
|---|---|
| {{outline unit, AC, constraint, or validation obligation}} | 01 |

## Final acceptance and validation

{{End-to-end acceptance criteria and exact final validation.}}

Before finishing, update `progress.md` with:

- the work-item identifier and status;
- files changed;
- tests added or changed;
- exact test commands and results;
- benchmark results, when applicable;
- important decisions or discoveries;
- remaining risks; and
- the recommended next runnable item, or `none` with concrete blocker evidence.

Leave the repository in a coherent, reviewable state. Create one commit for this work item. Generate a Conventional Commits message for the changes. Use the subject to concisely identify the change, and use the body to explain **why** it was needed—its motivation, problem, or intended outcome—without narrating what the diff does. Infer carefully from the available context; do not invent rationale.

End with a concise report containing:

- work item attempted;
- outcome;
- tests and benchmark results;
- files changed; and
- next recommended item.

If every work item is complete, create `.agent-artifacts/{{initiative-slug}}/ralph-complete` and make no further code changes.
