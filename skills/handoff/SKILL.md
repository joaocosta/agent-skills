---
name: handoff
description: Convert a grill-me design record that is ready for handoff into a self-contained implementation brief for one fresh session or ordered tasks for a Ralph loop. Use immediately after grill-me when implementation will continue without the current conversation. Do not use while material design decisions remain unresolved.
argument-hint: "Optional implementation focus; optionally request one handoff or Ralph-loop tasks"
disable-model-invocation: true
---

# Handoff

Transfer an implementation-ready design from the current conversation to fresh agents that cannot see it. Preserve the decisions established by `grill-me`; this skill packages the design for execution rather than reopening it or replacing it with a new plan.

## Confirm readiness

Find the final `grill-me` design record in the conversation and check its declared readiness.

Proceed only when the record is explicitly **ready for handoff** and no open question would force an implementer to choose product behavior, architecture, compatibility, risk posture, or acceptance semantics. Accepted risks and non-blocking assumptions may remain when their consequences are clear.

If the record is absent, marked **not ready for handoff**, or contains a material unresolved decision:

- do not create handoff files;
- identify the missing or blocking decisions briefly; and
- direct the user back to `grill-me` to resolve them.

Do not silently upgrade assumptions into decisions merely to make the handoff possible.

## Reuse established context

Treat the final design record as the authoritative handoff input. Reuse its settled decisions, codebase anchors, acceptance criteria, constraints, risks, and blockers. If the user supplies arguments, use them to narrow the implementation focus without contradicting the record.

Do not repeat broad repository exploration already performed by `grill-me`. Inspect only the referenced artifacts needed to make paths and symbols actionable or to account for repository changes made after the record was completed. If current evidence contradicts the record, flag the contradiction and stop rather than silently overturning the design.

A handoff must be self-contained operationally: a fresh agent should know what outcome to produce, what to read, what is settled, how to validate the result, and when it is done. This does not require copying entire specifications, design records, ADRs, issues, commits, or diffs. Cite durable sources by path, symbol, commit, issue, or URL and summarize only the portions needed to execute correctly. Avoid fragile line-number references.

## Choose the execution shape

Create one `handoff.md` when the work has one coherent outcome and can reasonably fit in one fresh implementation session.

Create ordered Ralph-loop tasks only when session boundaries, dependencies, risk, or independently verifiable milestones make decomposition useful. Each task must:

- deliver one coherent, reviewable outcome rather than a horizontal layer of unfinished machinery;
- state its dependencies and the artifacts it consumes from earlier tasks;
- leave the repository in a valid state;
- have validation that can run at that point; and
- avoid repeating analysis or decisions assigned to another task.

Prefer the execution shape explicitly requested by the user when it remains feasible. Do not split work merely because the design record is long.

Before writing, map every in-scope acceptance criterion and cross-cutting constraint to the single handoff or to one or more tasks. Use this coverage check to prevent omissions, but do not add a verbose traceability table unless it helps the implementation agents.

## Write outside the repository

Create a new uniquely named directory beneath the operating system's temporary directory, never in the workspace. Do not overwrite a prior handoff.

- For one session, write `<temporary-directory>/<unique-handoff-directory>/handoff.md`.
- For a Ralph loop, write `<temporary-directory>/<unique-handoff-directory>/README.md` plus `task-01-<slug>.md`, `task-02-<slug>.md`, and so on. Each task file is the complete prompt for one fresh Ralph iteration; the runner should be able to pass it to an agent without reconstructing context from the README or conversation. The README orchestrates the sequence but is not a substitute for task-local instructions.

Do not generate a shell runner or assume a particular Ralph command unless the user requests one and the repository provides an established runner convention. When requested, reference or wrap that convention rather than inventing a new execution interface.

Do not modify production code or repository documentation while producing the handoff.

## Required content

Each handoff or task must contain the following, merging sections when that makes the document easier to use:

- **Objective and current state** — the observable outcome and what already exists.
- **Required reading and code anchors** — a minimal reading sequence, ordered so the agent encounters contracts and authoritative design sources before their consumers; include stable symbols, relevant tests, and commands.
- **Scope** — what this execution unit owns.
- **Non-goals** — what it intentionally excludes, kept separate from scope so exclusions are difficult to overlook.
- **Settled decisions and constraints** — implementation-significant conclusions from the design record, including invariants, compatibility, and failure behavior where relevant.
- **Dependencies and prerequisites** — prior task outputs, environmental needs, and external dependencies without secret values.
- **Implementation direction** — natural seams and intended approach, while preserving legitimate implementation discretion.
- **Acceptance criteria and validation** — externally verifiable outcomes and exact or discoverable validation commands. Distinguish automated checks from required manual verification.
- **Risks, assumptions, and blockers** — only those still relevant to execution. A ready handoff must not contain a blocker that requires a new design decision.
- **Suggested skills** — only skills known to be available and materially useful, with why and at what stage to invoke them. Omit this section when none are relevant.
- **Done condition** — one consolidated statement defining the evidence required to declare the execution unit complete; it must agree with, not weaken, the acceptance criteria.

Tell the implementation agent to inspect referenced code before editing and to report contradictions rather than silently changing settled decisions.

For each Ralph-loop task, also include:

- **Completion check** — repository evidence that lets an agent detect the task is already complete and skip it safely.
- **Handoff to the next task** — concrete artifacts, symbols, migrations, tests, or decisions the next task should reuse rather than rediscover.

The Ralph-loop `README.md` must summarize the overall objective, shared authoritative references, execution order, dependency graph, cross-task constraints, and final end-to-end acceptance criteria. It must also state that each task file is the prompt for one fresh iteration and explain how to advance to the next file after the current task's done condition passes. Keep task-local detail in task files.

## Protect fidelity and privacy

Do not invent missing decisions, broaden scope, or turn optional ideas into requirements. Preserve important rationale when omitting it would tempt an implementer to reverse a settled decision. Clearly distinguish facts, decisions, assumptions, accepted risks, and non-goals when ambiguity could affect execution.

Do not include secrets, credential values, production customer data, or unrelated personally identifiable information.

## Final check

Read every generated document as a fresh agent with no access to the conversation. Confirm that:

- the objective, boundaries, implementation direction, and done conditions are executable;
- all in-scope acceptance criteria and constraints from the design record are covered;
- references are durable and sufficient without duplicating source documents;
- task dependencies and handoff artifacts are explicit;
- no task reopens a settled decision or requires an unstated material decision; and
- validation can demonstrate both task-level and final completion.

Report whether a single handoff or Ralph-loop set was created and list every exact path created.
