---
name: handoff
description: Read a persisted grill-me design record and convert it, in a separate context, into a self-contained implementation brief or finely scoped ordered Ralph-loop tasks. Use when implementation must be transferred to fresh sessions from `.agent-artifacts/<initiative-slug>/design.md`. Do not use while material design decisions remain unresolved.
argument-hint: "Path to design.md or initiative slug; optionally request one handoff or Ralph-loop tasks"
disable-model-invocation: true
---

# Handoff

Package a persisted, implementation-ready design for execution by fresh agents. Preserve its decisions; do not reopen the design or substitute a new plan.

Operate artifact-first. Assume no design-session conversation or repository findings remain in context. `design.md` is the authoritative design contract even if conversational context is present.

## Load and verify the source

Require a path to `.agent-artifacts/<initiative-slug>/design.md` or an unambiguous initiative slug. If neither is supplied, inspect `.agent-artifacts/` for a single clearly matching candidate; do not guess among multiple designs.

Always read the complete persisted `design.md`. Check its declared readiness, then inspect the current repository and the durable anchors it names only enough to:

- verify paths, symbols, tests, commands, and prerequisite outputs still exist or establish an explicitly recorded empty state;
- understand the implementation seams and current completion state; and
- make each execution prompt actionable.

Do not depend on the original conversation and do not repeat broad design exploration. The repository may have changed since persistence, so never assume the design session's findings are still true without checking the anchors relevant to decomposition.

Proceed only when the artifact is explicitly **ready for handoff** and no open question would force an implementer to choose product behavior, architecture, compatibility, risk posture, or acceptance semantics. Accepted risks and non-blocking assumptions may remain when consequences are clear.

Stop without creating handoff files when the artifact is missing, not ready, materially incomplete, or contradicted by current repository evidence. State the exact gap or contradiction and direct the user to update the design through `grill-me`. Do not silently promote assumptions, edit `design.md`, or make a product/design decision in order to package work.

## Choose the execution shape

Create one `handoff.md` only when all work has one concrete outcome and can comfortably be implemented, tested, and completed in one fresh context.

Create ordered Ralph-loop tasks when the user requests them or when independently verifiable milestones, dependencies, risk, or context size warrant decomposition. Prefer the requested shape when feasible, but explain and reject a single-session shape that would be unsafe.

Before selecting the shape, inventory:

1. every implementation-outline unit and dependency from `design.md`;
2. every numbered acceptance criterion, constraint, invariant, non-goal, risk control, migration/operational requirement, and validation obligation; and
3. current repository state and already completed work.

Use this inventory as a coverage ledger. Map every item to the single handoff or one or more Ralph tasks. Keep the ledger while planning; include a compact coverage map in the Ralph `README.md` when it helps later auditing.

## Decompose Ralph work recursively

Start from the design's natural implementation seams, not broad phases or a preferred task count. Produce vertical, independently reviewable increments. A foundational task is valid only when it delivers usable, tested infrastructure and leaves the repository valid; never create placeholder layers for later completion.

For every proposed task:

1. State its outcome in one sentence.
2. List its production changes, direct tests, migration/configuration/documentation work, and validation.
3. Identify dependencies, outputs reused later, and the practical commit boundary.
4. Ask whether any listed part can be implemented, validated, and committed independently while preserving a valid repository.
5. If yes, split it and repeat this review on each child task.
6. If no, keep it together and make the coupling reason evident in the task prompt.

A task must be split or explicitly justified as indivisible when any of these signals appear:

- its outcome joins independently observable capabilities with “and”;
- it spans multiple public capabilities, subsystems, migrations, or operational concerns;
- it combines reusable foundation work with a consumer that can be validated separately;
- its acceptance criteria form disjoint validation groups;
- it suggests more than one practical commit boundary;
- it uses a coarse label such as “complete module,” “shared infrastructure,” “integration,” “release readiness,” or “all tests” without a narrower observable boundary; or
- reading, implementation, focused tests, debugging, and validation could consume most of a fresh context.

As a conservative target, expected task work should use roughly 20–40% of a fresh context, preserving capacity for repository reading and debugging. Prefer one public behavior or one tightly coupled internal capability plus its direct tests. Do not create trivial mechanical tasks, test-only cleanup detached from owned behavior, or intermediate states that fail established checks.

Keep tightly coupled production code and direct tests together. Separate documentation, migration, package/release work, unrelated refactors, and broad contract validation when each has an independent done condition. Ordered tasks may depend on earlier tasks, but each must leave the repository valid and be independently committable where practical.

A ready design should not require a new design task. Bounded implementation discovery may occur inside the task that consumes it, but if discovery could change settled behavior or architecture, stop and return the design for revision rather than adding a task that reopens it.

After decomposition, run two audits:

- **Task audit:** every task has one concrete outcome, focused criteria and validation, explicit dependencies, a completion check and boundary, a valid intermediate state, and no reopened decision.
- **Coverage audit:** every inventory item is covered, no task contradicts another, and final end-to-end validation proves the complete design.

If any task remains coarse, split it again. Do not optimize for the fewest tasks.

## Write initiative artifacts

Write beside the design in `.agent-artifacts/<initiative-slug>/`. Inspect the directory first and preserve `design.md` unchanged.

Execution shapes are mutually exclusive:

- **Single session:** `design.md` and `handoff.md`; no `README.md`, `progress.md`, or `tasks/`.
- **Ralph loop:** `design.md`, `README.md`, `progress.md`, and ordered `tasks/task-01-<slug>.md`, `task-02-<slug>.md`, and so on; no `handoff.md`.

If opposite-shape artifacts exist, stop and ask whether to remove them or use another slug. Ask before overwriting selected-shape artifacts unless the user explicitly requested regeneration or update. Do not modify production code or repository documentation outside the initiative directory.

Each task file is the complete prompt for one fresh iteration. It may direct the agent to read `design.md`, `progress.md`, prior outputs, and code, but must not require the README, original conversation, or an unstated finding to understand its work. Include the relevant settled decisions and boundaries locally instead of saying only “follow the design.” Avoid duplicating the entire design.

Do not generate a shell runner or assume a Ralph command unless requested and the repository has an established convention.

## Required execution-unit content

Each handoff or task must include, merging sections when useful:

- **Concrete outcome and current state** — one observable result and verified starting point.
- **Required reading and anchors** — minimal ordered paths, symbols, tests, and commands; inspect before editing and report contradictions.
- **Scope and owned components** — production behavior and direct supporting work.
- **Non-goals** — especially adjacent work owned elsewhere.
- **Settled decisions and constraints** — relevant interfaces, invariants, compatibility, failure behavior, and rationale where omission risks reversal.
- **Dependencies and prerequisites** — prior task outputs, environment, and external dependencies without secrets.
- **Implementation direction** — intended seams and reuse, preserving incidental discretion.
- **Focused acceptance criteria** — only evidence attributable to this unit, linked to design criterion IDs where applicable.
- **Focused validation** — exact or readily discoverable automated commands and distinct manual checks.
- **Risks and assumptions** — only execution-relevant items; no design blocker.
- **Completion check** — repository evidence to detect already-complete work safely.
- **Completion boundary and done condition** — what is finished, what deliberately remains, and evidence required.
- **Next-task handoff** — exact artifacts, symbols, migrations, tests, or discoveries downstream must reuse rather than recreate.
- **Suggested skills** — only known available skills that materially help, with when and why; omit otherwise.

For Ralph tasks, also require the agent to inspect Git status, mark the task `in progress` in `progress.md`, update it with exact outputs and validation after success, or record concrete blocker evidence before stopping. A task must not claim earlier work exists without checking repository evidence and progress.

## Ralph orchestration files

`README.md` must contain the overall objective, authoritative references, ordered tasks, dependency graph, cross-task constraints, compact design-coverage map, and final end-to-end acceptance criteria/validation. State that each task file is one fresh iteration prompt and explain advancement only after its done condition passes. Keep task-local detail in task files.

Initialize `progress.md` as durable execution state with initiative status, current/next task, ordered checklist using `pending`/`in progress`/`complete`/`blocked`, completed outputs and validation evidence, cross-task discoveries/deviations, blockers, and next action. Start every task `pending` and `task-01` next; never invent implementation progress. `progress.md` records execution state, not design authority.

## Protect fidelity and privacy

Do not invent missing decisions, broaden scope, turn optional ideas into requirements, or reopen settled decisions. Distinguish facts, decisions, assumptions, accepted risks, constraints, and non-goals where ambiguity affects execution. Preserve rationale when omission would encourage reversal.

Do not include secrets, credential values, production customer data, or unrelated personally identifiable information.

## Final fresh-context check

Reread `design.md` and every generated file from disk while assuming no conversation exists. Confirm:

- the source artifact alone supports the decomposition;
- every task has one outcome and fits comfortably in one fresh context;
- task criteria, validation, dependencies, reusable outputs, completion check, and completion boundary are explicit;
- every intermediate repository state is valid and independently committable where practical;
- no task repeats broad discovery or reopens design decisions;
- implementation-outline units, constraints, and acceptance criteria have complete coverage;
- references are durable and task-local prompts contain essential decisions;
- exactly one execution shape exists; and
- Ralph README, progress, and task files agree on names, order, dependencies, coverage, and state.

Report the shape created and every exact path. If validation exposes coarse tasks or missing design detail, refine the decomposition or stop for a `design.md` revision rather than accepting the gap.
