---
name: mutation-testing-loop
description: Run one evidence-driven mutation-testing improvement iteration on a Python project using mutmut. inspect and rank all survivor groups, resolve only the highest-value unresolved issue, validate it, and optionally commit it. Use whenever the user asks to run mutmut, investigate surviving mutants, improve tests through mutation testing, or continue a mutation-testing loop. Mutation score is explicitly not the objective; pursue only changes that materially improve supported behavior, correctness, clarity, or maintainability.
compatibility: Requires Python, mutmut 3.x, a project test environment, and git for commits.
disable-model-invocation: true
---

# Mutation Testing Loop

Perform exactly one improvement iteration and stop. Mutation testing is an investigation aid, not a score target. A lower survivor count is useful evidence only when it results from a well-supported improvement.

## Establish the project contract

Read repository guidance, mutation configuration, test configuration, relevant documentation, and current Git status. Use the project's existing environment; do not install or upgrade dependencies unless asked.

Require `mutmut` 3.x and locate its executable. The bundled controller defaults to `.venv/bin/mutmut`; pass `--mutmut <path>` when the project uses another environment.

Protect user work. Do not discard unrelated changes, include them in a commit, or begin destructive cleanup when generated mutation state is not clearly at `<repository>/mutants`.

Ensure `mutants/` is ignored by Git before running. Add the narrow ignore entry when needed, but never commit generated contents.

## Run quietly from clean state

Resolve this skill's directory as `<skill-dir>`, then run from the project root:

```bash
<project-python> <skill-dir>/scripts/mutmut_control.py --mutmut <mutmut-path> run --fresh --report-name initial
```

The controller suppresses mutmut's high-volume progress display and retains the initial evidence as:

- `mutants/mutmut-initial-run.log` — full progress and diagnostics;
- `mutants/survivors-initial.json` — machine-readable statuses, groups, and compact diffs;
- `mutants/survivors-initial.md` — all survivor groups and their mutations.

Named reports prevent the final pass from overwriting the inventory used to choose the finding.

Do not stream the raw run log, call `mutmut results --all true` directly, invoke `mutmut show` for every survivor, or read generated multi-megabyte Python files. Inspect the concise artifacts instead. Read the raw log only around a specific failure.

If the full run fails or has errors that make its evidence unreliable, diagnose that limitation rather than selecting a finding from incomplete results.

## Triage every survivor group

Read all of `mutants/survivors-initial.md`, in chunks when necessary. Group further when different symbols expose the same behavioral or design issue. Do not equate syntactic similarity with a common root cause. Keep broad searches and large test modules out of context: locate candidate symbols and focused tests first, then read only relevant ranges unless the whole file is needed.

Rank every group using repository evidence:

1. impact on supported behavior;
2. likelihood of a genuine test or implementation weakness;
3. regression risk;
4. value and maintainability of a resolution.

Select only the highest-value unresolved group. If no group supports a valuable change, make no change and report that conclusion. Do not move to a second group.

Before editing, inspect the selected production code, callers, behavioral boundaries, tests, types, validation, documentation, and conventions. Classify its relevant survivors as one or more of:

- missing or weak behavioral coverage;
- redundant, unreachable, ambiguous, duplicated, or unnecessarily complex code;
- equivalent mutation;
- impossible or unsupported state;
- low-value or non-contractual behavior;
- mutation-tool limitation;
- unresolved specification question.

Do not invent intended behavior. Equivalent, impossible, low-value, and tool-limited mutants are findings, not invitations to add implementation-coupled tests or score-only exclusions.

## Resolve one material issue

Choose the resolution that improves the project independently of mutation score:

- Strengthen tests when observable supported behavior lacks a meaningful guarantee.
- Simplify, clarify, relocate, or remove production logic when the survivor exposes a design or maintainability problem.
- Add a documented exclusion only when repository evidence demonstrates equivalence, impossibility, low value, or a tool limitation and the exclusion itself is maintainable.
- Make no code change when evidence cannot support a valuable resolution.

Avoid tests that mirror private implementation, weakened assertions or behavior, speculative contracts, broad exclusions, unrelated cleanup, and pursuit of a perfect score.

## Validate the finding

After changing code:

1. Run the directly relevant tests and make them pass.
2. Rerun the originally surviving mutants for each selected exact symbol:

   ```bash
   <project-python> <skill-dir>/scripts/mutmut_control.py --mutmut <mutmut-path> rerun \
     --report-name initial --symbol '<exact symbol from survivors-initial.md>'
   ```

3. Run repository-required format, lint, type, and broader test checks.
4. Run a final complete mutation pass without deleting generated state:

   ```bash
   <project-python> <skill-dir>/scripts/mutmut_control.py --mutmut <mutmut-path> run --report-name final
   ```

Compare `mutants/survivors-initial.json` with `mutants/survivors-final.json` for the selected symbol. Confirm that its original survivors are killed or no longer generated for a legitimate reason and that the affected group has no new relevant survivor. Never infer a kill from ordinary tests or from a missing old mutant name alone; when identities change, compare before-and-after diffs.

## Commit only valuable changes

When valuable changes were made and validation passed, create one Conventional Commits commit containing only this iteration's changes. Use the subject for the change and the body for the behavioral risk, missing guarantee, ambiguity, or maintainability problem it resolves. Do not narrate the diff, invent rationale, commit `mutants/`, or create an empty commit.

## Report compactly

Report:

### Outcome
Whether a material change and commit were made, plus commit hash and message when applicable.

### Mutation run
Initial and final commands and counts for total, killed, survived, timeout, error, and other available statuses; note limitations.

### Ranked findings
List the selected group first, followed by the most important deferred groups. For each give symbol/file, representative mutation, behavioral effect, evidence-based assessment, and disposition. State that all groups in `mutants/survivors-initial.md` were reviewed; do not reproduce hundreds of low-value entries.

### Selected finding
Explain original behavior, surviving mutation, why it mattered, why tests missed it, and whether the root issue was tests, production, specification, or tooling.

### Resolution and verification
Explain the change's material value, why tests are behavioral rather than implementation-coupled, commands and outcomes, and direct mutation evidence.

### Remaining work
Name the leading deferred groups without changing them. Point to `mutants/survivors-initial.md` for the reviewed inventory and `mutants/survivors-final.md` for the post-change inventory.
