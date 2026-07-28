---
name: handoff
description: Read a persisted grill-me design record and convert it, in a separate context, into a validated implementation handoff or deterministic Ralph-loop package. Use when implementation must be transferred to fresh sessions from `.agent-artifacts/<initiative-slug>/design.md`. Do not use while material design decisions remain unresolved.
argument-hint: "Path to design.md or initiative slug; optionally request one handoff or Ralph-loop tasks"
disable-model-invocation: true
---

# Handoff

Package a persisted, implementation-ready design for execution by fresh agents. Preserve its decisions; do not reopen the design or substitute a new plan.

Operate artifact-first. Assume no design-session conversation or repository findings remain in context. `design.md` is the authoritative design contract even if conversational context is present.

## Load and verify the source

Require a path to `.agent-artifacts/<initiative-slug>/design.md` or an unambiguous initiative slug. If neither is supplied, inspect `.agent-artifacts/` for a single clearly matching candidate; do not guess among multiple designs.

Read the complete persisted `design.md`. Check its declared readiness, then inspect the current repository and its named anchors only enough to:

- verify paths, symbols, tests, commands, and prerequisite outputs or establish an explicitly recorded empty state;
- understand implementation seams and current completion state; and
- detect contradictions that would invalidate the design or decomposition.

Proceed only when the artifact is explicitly **ready for handoff** and no open question would force an implementer to choose product behavior, architecture, compatibility, risk posture, or acceptance semantics. Accepted risks and non-blocking assumptions may remain when their consequences are clear.

Stop without creating handoff files when the artifact is missing, not ready, materially incomplete, or contradicted by current repository evidence. State the exact gap and direct the user to update the design through `grill-me`. Do not edit `design.md`, silently promote assumptions, or invent a decision to package the work.

## Choose exactly one execution shape

Create one `handoff.md` only when all work has one concrete outcome and can comfortably be implemented, tested, and completed in one fresh context.

Create a Ralph package when the user requests one or when independently verifiable milestones, dependencies, risk, or context size warrant decomposition. Prefer the requested shape when feasible, but reject an unsafe single-session shape with a concise explanation.

Before choosing, inventory:

1. every implementation-outline unit and dependency;
2. every numbered acceptance criterion, constraint, invariant, non-goal, risk control, migration or operational requirement, and validation obligation; and
3. current repository state and already completed work.

Use this inventory as a coverage ledger. Map every item to the single handoff or one or more Ralph tasks. An implementation-outline unit is a starting boundary, not automatically one task.

## Use the canonical scaffolds

Read the applicable scaffold files before writing artifacts:

- single session: [`references/handoff-template.md`](references/handoff-template.md);
- Ralph overview: [`references/ralph-readme-template.md`](references/ralph-readme-template.md);
- Ralph execution state: [`references/progress-template.md`](references/progress-template.md); and
- each Ralph task: [`references/task-template.md`](references/task-template.md).

The scaffolds are defaults, not cages: adapt prose, tables, and add useful sections when the design requires it. Preserve every scaffold's `##` required heading exactly once and in order. Use `None` rather than silently omitting a required section that has no applicable content. Remove every `{{placeholder}}`.

Generated files live beside `design.md`:

- **Single session:** `handoff.md`; no `README.md`, `progress.md`, `loop.sh`, or `tasks/`.
- **Ralph:** `README.md`, `progress.md`, executable `loop.sh`, and ordered `tasks/task-01-<slug>.md`, `task-02-<slug>.md`, and so on; no `handoff.md`.

Do not overwrite artifacts from the opposite shape without explicit user approval. Do not put handoff files elsewhere unless explicitly requested.

## Decompose Ralph work recursively

Split an outline unit whenever it has multiple independently verifiable outcomes, exceeds one fresh context, crosses a risky interface or migration boundary, or cannot end in a coherent repository state. Merge units only when neither can be implemented or validated usefully alone. Prefer the smallest set of tasks that satisfies these constraints, not the largest possible task count.

Order tasks by prerequisites and earliest useful validation. Foundation-only work is acceptable only when it exposes a stable interface and can be tested independently. Keep every intermediate state buildable, testable, migratable, deployable, or explicitly inert. Use migrations, adapters, flags, compatibility stages, or additive changes where the design calls for them.

Use deterministic naming: contiguous two-digit task numbers beginning at `01`, plus a concise lowercase kebab-case outcome slug. Avoid phase-only names such as `backend`, `tests`, or `cleanup` when a behavioral outcome is available.

Each task must own one concrete outcome, one primary implementation surface, and its focused tests or validation. Keep tests with the behavior they prove. Reserve a separate integration or final-validation task only when it has distinct cross-cutting behavior or cannot run earlier.

## Make every execution unit self-contained

A single handoff and each task are complete fresh-session prompts. They may direct the implementer to read `design.md`, `progress.md`, prior outputs, and code, but must include essential settled decisions and boundaries locally instead of saying only “follow the design.” Avoid copying the entire design.

Populate every required section with:

- durable reading anchors and exact prior outputs to verify and reuse;
- explicit scope, ownership, non-goals, constraints, and dependencies;
- bounded implementation direction that does not invent design;
- observable criteria mapped to design acceptance-criterion IDs;
- exact focused validation and expected evidence;
- a completion check for safely detecting existing work;
- a completion boundary and done condition that leaves a valid repository state; and
- precise downstream artifacts and discoveries to reuse rather than recreate.

For Ralph tasks, direct the agent to inspect Git status, mark the task `in progress` in `progress.md`, and record exact outputs and validation after success or concrete blocker evidence before stopping. A task must verify repository evidence and progress rather than merely claiming prior work exists.

## Build the Ralph control plane

`README.md` is the stable prompt passed to every loop iteration. It must include the ordered tasks, dependency graph, shared constraints, complete design coverage map, and final end-to-end validation. Retain the scaffold's closing controls so every iteration:

- updates `progress.md` with status, files, tests, exact results, discoveries, risks, and next work;
- leaves a coherent state and creates one Conventional Commit at the task boundary;
- ends with a concise work report;
- treats `Next task` as the next runnable task, allowing independent work to continue around a blocked task;
- records `Next task: none` and initiative status `blocked` when no runnable work remains, so the loop pauses for intervention instead of retrying; and
- creates `.agent-artifacts/<initiative-slug>/ralph-complete` only after every work item is complete, allowing the loop to stop.

Initialize `progress.md` as execution state, never design authority. Start the initiative `not started`, every task `pending`, no current task, and task 01 as next. Never invent implementation progress.

Copy [`assets/loop.sh`](assets/loop.sh) to the initiative as `loop.sh` and make it executable. Preserve its generic `ralph-complete` protocol, script-relative paths, logging, failure propagation, `RALPH_CMD` override, `MAX_ITERATIONS` guard, disabled Pi extension discovery, task-based session naming, blocked/no-runnable stop, and no-progress guard. By default, session names use `ralph:<initiative>:<next-task-file-stem>`, deriving the runnable task from `progress.md` and verifying that its file exists; `RALPH_SESSION_PREFIX` may override the portion before the task name. A blocked task may coexist with another runnable task, but `Next task: none` with initiative status `blocked` exits distinctly for human intervention. Pending work with no recorded runnable task is a protocol/dependency error. Adapt the script only for a concrete repository need that the design establishes; never hard-code the example initiative slug.

## Validate mechanically

After writing all files, run the bundled validator from the skill directory:

```bash
python3 scripts/validate_handoff.py /absolute/path/to/.agent-artifacts/<initiative-slug> --shape single
# or
python3 scripts/validate_handoff.py /absolute/path/to/.agent-artifacts/<initiative-slug> --shape ralph
```

For Ralph packages, also run explicitly:

```bash
bash -n /absolute/path/to/.agent-artifacts/<initiative-slug>/loop.sh
```

Treat any failure as an artifact defect: fix the generated files and rerun validation. The validator checks required headings and order, unresolved placeholders, shape exclusivity, progress fields, contiguous task names, cross-file task references, explicit acceptance-criterion coverage, README loop controls, executable script state, required loop settings, Bash syntax, and sandboxed blocked/deadlock/no-progress/routing behavior. Do not weaken the generated artifact or skip checks merely to report success.

Mechanical validation complements, rather than replaces, the semantic fresh-context review.

## Protect fidelity and privacy

Do not broaden scope, turn optional ideas into requirements, or reopen settled decisions. Distinguish facts, decisions, assumptions, accepted risks, constraints, and non-goals where ambiguity affects execution. Preserve rationale when omission would encourage reversal.

Do not include secrets, credential values, production customer data, or unrelated personally identifiable information.

## Final fresh-context review

Reread `design.md` and every generated file from disk while assuming no conversation exists. Confirm:

- the source artifact alone supports the decomposition;
- every task has one outcome and fits comfortably in one fresh context;
- task criteria, validation, dependencies, reusable outputs, completion check, and completion boundary are explicit;
- every intermediate state is valid and independently committable where practical;
- no task repeats broad discovery or reopens design decisions;
- outline units, constraints, and acceptance criteria have complete coverage;
- references are durable and task prompts contain essential decisions;
- exactly one execution shape exists; and
- Ralph README, progress, loop, and task files agree on names, order, dependencies, coverage, state, and completion protocol.

Report the shape, every exact generated path, and validation commands/results. If review exposes coarse tasks or missing design detail, refine the decomposition or stop for a `design.md` revision rather than accepting the gap.
