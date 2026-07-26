---
name: handoff
description: Convert a grill-me design record that is ready for handoff into a self-contained implementation brief for one fresh session or ordered tasks for a Ralph loop. Use immediately after grill-me when implementation will continue without the current conversation. Do not use while material design decisions remain unresolved.
argument-hint: "Optional implementation focus; optionally request one handoff or Ralph-loop tasks"
disable-model-invocation: true
---

# Handoff

Transfer an implementation-ready design from the current conversation to fresh agents that cannot see it. Preserve the decisions established by `grill-me`; this skill packages the design for execution rather than reopening it or replacing it with a new plan.

## Confirm readiness

Use the final `grill-me` design record already in the conversation as the primary input and check its declared readiness. Identify the initiative slug established by `grill-me` and verify that `.agent-artifacts/<initiative-slug>/design.md` exists for downstream agents. Do not reread the file when the complete final record is already in context. Read it only when the handoff runs in a later session, the conversation record is missing or ambiguous, or persisted-content validation is needed. If the slug is not known, inspect `.agent-artifacts/` for a clearly matching design; do not guess when multiple initiatives are plausible.

Proceed only when the record is explicitly **ready for handoff** and no open question would force an implementer to choose product behavior, architecture, compatibility, risk posture, or acceptance semantics. Accepted risks and non-blocking assumptions may remain when their consequences are clear.

If no usable final record is available, the record is marked **not ready for handoff**, it contains a material unresolved decision, or the persisted `design.md` is missing:

- do not create handoff files;
- identify the missing artifact or blocking decisions briefly; and
- direct the user back to `grill-me` to persist or resolve them.

Do not silently upgrade assumptions into decisions merely to make the handoff possible.

## Reuse established context

Reuse the final in-context record's settled decisions, codebase anchors, acceptance criteria, constraints, risks, and blockers. The persisted `design.md` remains the durable authoritative source that generated prompts should direct implementation agents to read. If validation reveals that the conversation and persisted design differ materially, update the design through `grill-me` before packaging a handoff. If the user supplies arguments, use them to narrow the implementation focus without contradicting the record.

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

### Size Ralph-loop tasks for fresh contexts

Size each task so a fresh agent can read its references, implement it, add or update focused tests, run validation, and complete the handoff comfortably within one context window. As a conservative planning target, the expected work should consume no more than roughly 20–40% of a fresh context window; uncertainty and debugging need the remaining capacity.

Prefer vertical, independently valuable and verifiable increments. Keep tightly coupled code and its direct tests together, but split work when it crosses subsystems or concerns, combines unrelated production changes, migrations, refactors, documentation, or broad test work, or contains outcomes that can be implemented, tested, and committed independently. Do not combine work merely because it belongs to one feature. When substantial discovery or an unresolved implementation decision remains, create an ordered investigation or decision task before dependent implementation. Preserve real dependencies, and do not create trivial mechanical tasks or unverifiable intermediate states.

Before finalizing a Ralph-loop decomposition, review every proposed task and ask:

- Could this reasonably consume most of a fresh context window?
- Does it cross subsystem or concern boundaries?
- Does it contain more than one meaningful implementation outcome?
- Could any part be completed, tested, and committed independently?

If any answer is yes, split the task unless that would create artificial sequencing or an unverifiable intermediate state. Do not target a fixed task count; optimize for the smallest independently valuable and verifiable unit of work, not the fewest tasks.

Before writing, map every in-scope acceptance criterion and cross-cutting constraint to the single handoff or to one or more tasks. Use this coverage check to prevent omissions, but do not add a verbose traceability table unless it helps the implementation agents.

## Write initiative artifacts

Write the handoff beside the design in `.agent-artifacts/<initiative-slug>/`. The user's invocation of this skill authorizes creation of the selected handoff shape. Inspect the initiative directory before writing and preserve `design.md` unchanged.

The two execution shapes are mutually exclusive for an initiative:

- **Single session:** `.agent-artifacts/<initiative-slug>/design.md` and `.agent-artifacts/<initiative-slug>/handoff.md`. Do not create `README.md`, `progress.md`, or `tasks/`.
- **Ralph loop:** `.agent-artifacts/<initiative-slug>/design.md`, `.agent-artifacts/<initiative-slug>/README.md`, `.agent-artifacts/<initiative-slug>/progress.md`, and ordered `.agent-artifacts/<initiative-slug>/tasks/task-01-<task-slug>.md`, `task-02-<task-slug>.md`, and so on. Do not create `handoff.md`.

If artifacts from the opposite shape already exist, stop and ask the user whether to remove them or use a different initiative slug; never leave both shapes in one initiative directory. Ask before overwriting an existing handoff of the selected shape unless the user explicitly requested regeneration or update.

Each task file is the complete prompt for one fresh Ralph iteration. A runner must be able to pass it to an agent without reconstructing context from the README, progress file, or conversation. The README orchestrates the sequence but is not a substitute for task-local instructions.

Do not generate a shell runner or assume a particular Ralph command unless the user requests one and the repository provides an established runner convention. When requested, reference or wrap that convention rather than inventing a new execution interface.

Do not modify production code or repository documentation outside `.agent-artifacts/<initiative-slug>/` while producing the handoff.

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

For each Ralph-loop task, make all of these explicit:

- **Single concrete outcome** — one independently valuable result, not a bundle of milestones.
- **Scope and relevant files or components** — identify likely anchors when known.
- **Non-goals** — especially adjacent work assigned to later tasks.
- **Dependencies and prerequisites** — including prior outputs it consumes.
- **Implementation guidance** — reuse the approach settled during design rather than reopening it.
- **Objective acceptance criteria** — observable evidence for this task only.
- **Focused validation** — exact or readily discoverable commands and checks proportionate to the change.
- **Completion boundary** — state what this task finishes and what remains for later tasks.
- **Completion check** — repository evidence that lets an agent detect the task is already complete and skip it safely.
- **Handoff to the next task** — concrete artifacts, symbols, migrations, tests, or decisions the next task should reuse rather than rediscover.

The Ralph-loop `README.md` must summarize the overall objective, shared authoritative references, execution order, dependency graph, cross-task constraints, and final end-to-end acceptance criteria. It must also state that each task file is the prompt for one fresh iteration and explain how to advance to the next file after the current task's done condition passes. Keep task-local detail in task files.

Initialize the Ralph-loop `progress.md` as the durable overall execution state. Include the initiative status, current or next task, an ordered task checklist with `pending`/`in progress`/`complete`/`blocked` states, completed outputs and validation evidence, cross-task discoveries or deviations, blockers, and the next action. Start every task as `pending` and identify `task-01` as next; do not claim implementation progress that has not occurred. Instruct each iteration to mark its task `in progress` when it starts, then update `progress.md` after the completion check and done condition pass, or record a `blocked` state before stopping. Task prompts must use this file for execution state, not as a replacement for authoritative design decisions.

## Protect fidelity and privacy

Do not invent missing decisions, broaden scope, or turn optional ideas into requirements. Preserve important rationale when omitting it would tempt an implementer to reverse a settled decision. Clearly distinguish facts, decisions, assumptions, accepted risks, and non-goals when ambiguity could affect execution.

Do not include secrets, credential values, production customer data, or unrelated personally identifiable information.

## Final check

Read every generated document as a fresh agent with no access to the conversation. Confirm that:

- the objective, boundaries, implementation direction, and done conditions are executable;
- all in-scope acceptance criteria and constraints from the design record are covered;
- references are durable and sufficient without duplicating source documents;
- task dependencies and handoff artifacts are explicit;
- no task reopens a settled decision or requires an unstated material decision;
- validation can demonstrate both task-level and final completion;
- every Ralph task passes the decomposition review, fits comfortably in one fresh context, has one concrete outcome, and states its completion boundary;
- the initiative contains exactly one execution shape; and
- for Ralph loops, `README.md`, `progress.md`, and every ordered file under `tasks/` agree on names, order, dependencies, and state.

Report whether a single-session handoff or Ralph-loop set was created and list every exact path created.
