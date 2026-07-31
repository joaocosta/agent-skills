---
name: beads-handoff
description: Read a persisted grill-me design record and convert it, in a separate context, into validated, implementation-ready Beads issues and dependency edges. Use when execution should be handed off through a repository's bd/Beads workspace instead of handoff files under .agent-artifacts. Do not use while material design decisions remain unresolved or when no Beads workspace exists.
argument-hint: "Path to design.md or initiative slug; optionally request one task or a decomposed task DAG"
disable-model-invocation: true
---

# Beads Handoff

Convert a persisted, implementation-ready design into durable Beads work. Preserve its decisions; do not reopen the design, implement production code, or create markdown execution artifacts.

Operate source-first and assume no design-session conversation remains in context. The persisted `design.md` is the design authority; Beads becomes the execution and status authority after packaging.

## Establish the workspace and source

Run `bd prime`, then `bd where`. Stop if the target repository has no active Beads workspace; do not initialize one unless the user explicitly asks. Follow the repository's active Beads profile and conventions. Do not commit, push, or sync merely because this skill created issues.

Require a path to `.agent-artifacts/<initiative-slug>/design.md` or an unambiguous initiative slug. If neither is supplied, inspect `.agent-artifacts/` for one clearly matching candidate; do not guess among multiple designs.

Read the complete design. Check its declared readiness, then inspect current repository state and named anchors only enough to:

- verify paths, symbols, tests, commands, prerequisite outputs, and current completion state;
- understand implementation seams and dependencies; and
- detect contradictions that invalidate the design or decomposition.

Proceed only when the design is explicitly **ready for handoff** and no open question would force an implementer to choose product behavior, architecture, compatibility, risk posture, or acceptance semantics. Stop without mutating Beads when it is missing, not ready, materially incomplete, or contradicted by current evidence. State the exact gap and direct revision through `grill-me`; do not edit the design or invent a decision.

Before creating anything, search existing open and closed issues by initiative title, slug, source design path, and distinctive outcome. Inspect plausible matches with `bd show --json`. Reuse a complete matching handoff, or update only with explicit user approval. Never create a duplicate handoff merely because IDs were not supplied.

## Plan a context-bounded executable task DAG

Represent every handoff as a directed acyclic graph (DAG) of one or more independently executable task issues. A one-task handoff has no internal edge but may depend on existing Beads work. Blocking edges — not list order, handoff context, or parentage — are the authoritative execution structure.

Before decomposing, inventory every implementation-outline unit and dependency; numbered acceptance criterion; constraint, invariant, non-goal, risk control, migration or operational requirement; validation obligation; and already completed output. Map these items to tasks in a coverage ledger and aggregate concerns to the epic when used. Maintain a dependency ledger with each planned task's direct prerequisites, outputs consumed, edge reasons, and parallel status. Finish both ledgers and the complete DAG before mutating Beads.

Split at stable, independently testable seams until each task has one coherent outcome, one primary implementation surface, fits comfortably in a small fresh context with reserve for inspection and validation, and ends in a valid buildable, testable, migratable, deployable, or explicitly inert state. Split work that has multiple outcomes, crosses a risky interface or migration boundary, or cannot end coherently. Merge only when separation would invalidate an intermediate state, duplicate substantial work, or leave a fragment without an independently verifiable outcome. Reject a requested one-task handoff when it cannot satisfy these boundaries.

Prioritize, in order: context fit; a coherent independently verifiable outcome; valid reusable intermediate states; avoiding bookkeeping, broad discovery, phase-only tasks, and tests detached from their behavior; then reducing tasks or edges. Do not minimize task count at the expense of the earlier priorities.

For every relationship, distinguish:

- a **hard prerequisite**, whose concrete output is required to start — create a blocking edge;
- a **handoff**, whose output is useful but not required to start — document it without blocking;
- **parallel work** — create no edge; and
- **parentage** — use only for coordination hierarchy, never execution order.

Record direct hard prerequisites only. If C depends on B and B on A, omit C → A unless C independently consumes A's output. Name the output and reason for every edge, reject cycles, and topologically order tasks by prerequisites and earliest useful validation. Foundation work must expose a stable, independently tested interface; tasks in the same layer remain independently ready.

An epic is optional coordination metadata for a DAG with two or more tasks. Create one only when initiative-level scope, coverage, final validation, or aggregate closure needs durable tracking. Reuse a suitable existing epic when one already owns the initiative. Never use an epic as an execution prerequisite or as a wrapper around one task.

## Compose the canonical issue bodies

Read the applicable scaffold before composing issue content:

- task issue: [`references/task-issue-template.md`](references/task-issue-template.md);
- optional coordination epic: [`references/epic-issue-template.md`](references/epic-issue-template.md).

Populate each scaffold from the design and ledgers so every task is a self-contained fresh-session prompt. Preserve its `##` headings exactly once and in order, add `###` subsections only when useful, use `None` only for an inapplicable section, and remove every `{{placeholder}}`. Use outcome-oriented titles rather than phases such as “backend,” “tests,” or “cleanup.”

Also populate the Beads `acceptance_criteria` field with concise observable criteria and design AC mappings, and set `spec_id` to the repository-relative design path. Use repository conventions for labels and priority; otherwise use P2 and no speculative labels. Do not copy the full design or include secrets, credentials, production customer data, or unrelated personal information.

Use temporary body files outside the repository when safer than shell quoting, then remove them. Do not write manifests, task markdown, progress files, or loop controls into the repository.

When using a coordination epic, create or identify it first with a placeholder-free planned breakdown naming each task outcome. Create tasks in topological order so prerequisite IDs exist, adding `--parent <epic-id>` only for hierarchy. In each task, declare `Blocked by: None` or the direct prerequisite IDs and name the output consumed from each.

Create blocking edges with `--deps <prerequisite-id>,...` when supported; otherwise immediately run `bd dep add <blocked-task> <prerequisite-task>`. The blocked issue is always first. After capturing live child IDs, update the epic with its final breakdown, topological layers, coverage map, and direct edge list.

Leave generated execution work open and unassigned. Implementation agents claim ready tasks, record completion or blocker evidence in Beads, create follow-up issues for discovered work, and close only after the issue's done condition passes. Close a coordination epic only after all owned tasks and final validation succeed. Follow the repository's active profile for commits and sync.

## Create carefully

Before mutation, finish all issue bodies, acceptance text, titles, parentage, and dependency edges in memory or temporary files. Prefer commands equivalent to:

```bash
bd create --title "<outcome>" --type task --priority 2 \
  --body-file <temporary-body> --acceptance "<criteria and AC mappings>" \
  --spec-id .agent-artifacts/<initiative>/design.md --json

bd create --title "<initiative outcome>" --type epic --priority 2 \
  --body-file <temporary-epic-body> --acceptance "<success criteria>" \
  --spec-id .agent-artifacts/<initiative>/design.md --json
bd create --title "<child outcome>" --type task --priority 2 --parent <epic-id> \
  --deps <prerequisite-id>,<prerequisite-id> \
  --body-file <temporary-task-body> --acceptance "<task criteria>" \
  --spec-id .agent-artifacts/<initiative>/design.md --json
# Fallback only when create-time --deps is unavailable:
bd dep add <blocked-child-id> <prerequisite-child-id>
bd update <epic-id> --body-file <final-temporary-epic-body>
```

Capture every returned ID. Stop on the first mutation error. Do not silently delete successfully created issues or retry creation, because either can hide shared concurrent changes. Inspect the partial state, record the exact failure on the epic when one exists, and report the IDs requiring repair.

## Validate and review the live handoff

Inspect live Beads state rather than trusting the planned text:

1. Save `bd show <all-created-ids> --json` output to a temporary file outside the repository, then run from this skill directory:

   ```bash
   python3 scripts/validate_beads_handoff.py <show-json> \
     --source /absolute/path/to/design.md
   ```

2. For a multi-task DAG, run `bd graph <epic-or-task-id> --compact` and `bd dep cycles` or the installed equivalent; with an epic, also run `bd children <epic-id> --json`. Compare live parentage and edges with both ledgers and the epic: missing and extra edges are defects.
3. Run `bd lint <all-created-ids>` and inspect `bd ready`. Confirm dependency-free tasks are runnable, blocked tasks are not, and parallel tasks remain independent.
4. Rerun the duplicate search and confirm the handoff is the sole match.

Treat failures as issue defects. Update only newly created issues with non-interactive `bd update` flags, repair edges explicitly, and rerun every check. Never use `bd edit`, weaken content, or skip validation to report success.

A mechanical pass is not enough. Reread the design and live issues as a fresh implementation agent and confirm that each task has one context-bounded outcome, explicit execution and validation evidence, valid boundaries and intermediate states, and no need to rediscover work or reopen settled decisions. Verify semantic coverage of the outline, constraints, and ACs, and confirm Beads alone exposes ready work and durable status without repository control files.

Report the task count, coordination epic ID if any, ordered task IDs and titles, dependency edges, and exact mechanical and semantic validation results. Mention that no commit, push, or Beads sync was performed unless separately authorized.
