---
name: mutation-testing-loop
description: Run one evidence-driven mutation-testing improvement iteration on a Python project using mutmut. inspect and rank all survivor groups, resolve only the highest-value unresolved issue, validate it, and optionally commit it. Use whenever the user asks to run mutmut, investigate surviving mutants, improve tests through mutation testing, or continue a mutation-testing loop. Mutation score is explicitly not the objective; pursue only changes that materially improve supported behavior, correctness, clarity, or maintainability.
compatibility: Requires Python, mutmut 3.x, a project test environment, and git for commits.
disable-model-invocation: true
---

# Mutation Testing Loop

Perform exactly one improvement iteration and stop. Mutation testing is an investigation aid, not a score target. A lower survivor count is useful evidence only when it results from a well-supported improvement.

## Establish the project contract

Read repository guidance, mutation configuration, test configuration, relevant documentation, and current Git status. Discover the repository's actual commit gate, including configured tracked hooks, before editing so required validation is not first discovered during commit. Use the project's existing environment; do not install or upgrade dependencies unless asked.

Require `mutmut` 3.x and locate its executable. The bundled controller defaults to `.venv/bin/mutmut`; pass `--mutmut <path>` when the project uses another environment.

Protect user work. Do not discard unrelated changes or include them in a commit. Ensure `mutants/` is ignored by Git before running; add the narrow ignore entry when needed, but never commit generated contents. The controller refuses tracked or unignored mutation state and restricts `--fresh` cleanup to `<repository>/mutants` with a recognized generated-state marker. If that check fails, inspect the directory and preserve it rather than bypassing the guard.

## Run quietly from clean state

Resolve this skill's directory as `<skill-dir>`, then run from the project root:

```bash
<project-python> <skill-dir>/scripts/mutmut_control.py --mutmut <mutmut-path> run --fresh --report-name initial
```

The controller suppresses mutmut's high-volume progress display and retains the initial evidence as:

- `mutants/mutmut-initial-run.log` — full progress and diagnostics;
- `mutants/triage-initial.md` — every survivor group with source anchors and deterministic representative mutations;
- `mutants/survivors-initial.json` — machine-readable complete survivor data plus per-symbol status counts;
- `mutants/survivors-initial.md` — complete human-readable survivor data.

Named reports prevent the final pass from overwriting the inventory used to choose the finding.

Do not stream the raw run log, call `mutmut results --all true` directly, load the complete JSON or Markdown reports into context, invoke `mutmut show` for every survivor, or read generated multi-megabyte Python files. Read all of the compact triage inventory, then use the controller's `inspect` command for plausible contenders. Its default output prints every distinct mutation fingerprint with a count while omitting repetitive mutant IDs; use `--verbose` only when individual names are actually needed. The complete reports remain audit artifacts. Read the raw log only around a specific failure.

If the full run fails or has errors that make its evidence unreliable, diagnose that limitation rather than selecting a finding from incomplete results.

## Triage every survivor group

Read all of `mutants/triage-initial.md`. This is the mandatory all-group pass; representative mutations are leads, not a substitute for full inspection of contenders. Use the inventory's source anchors to locate candidate code and focused tests, inspect their relevant contracts, then print complete survivor details only for plausible contenders. Batch nearby contenders in one invocation when the combined output will remain manageable:

```bash
<project-python> <skill-dir>/scripts/mutmut_control.py inspect \
  --report-name initial \
  --symbol '<exact symbol from triage-initial.md>' \
  --symbol '<another plausible contender>'
```

Group further when different symbols expose the same behavioral or design issue. Do not equate syntactic similarity with a common root cause. Keep broad searches and large test modules out of context: locate candidate symbols and focused tests first, then read only relevant ranges unless the whole file is needed.

Rank every group using repository evidence:

1. impact on supported behavior;
2. likelihood of a genuine test or implementation weakness;
3. regression risk;
4. value and maintainability of a resolution.

Select only the highest-value unresolved group. Do not silently substitute the easiest or smallest group: explicitly compare the selected group with its nearest contenders using the four criteria above. If a high-value symbol is broad, consider whether one coherent survivor subgroup is the single issue to resolve rather than deferring it for breadth alone. If no group supports a valuable change, make no change and report that conclusion. Do not move to a second group.

Before editing, inspect the selected production code, callers, behavioral boundaries, tests, types, validation, documentation, and conventions. Classify its relevant survivors as one or more of:

- missing or weak behavioral coverage;
- redundant, unreachable, ambiguous, duplicated, or unnecessarily complex code;
- equivalent mutation;
- impossible or unsupported state;
- low-value or non-contractual behavior;
- mutation-tool limitation;
- unresolved specification question.

Do not invent intended behavior. Equivalent, impossible, low-value, and tool-limited mutants are findings, not invitations to add implementation-coupled tests, rewrite equally clear code merely to change mutant generation, or add score-only exclusions.

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
2. Rerun the selected exact symbol:

   ```bash
   <project-python> <skill-dir>/scripts/mutmut_control.py --mutmut <mutmut-path> rerun \
     --report-name initial --symbol '<exact symbol from triage-initial.md>'
   ```

   The controller uses a symbol wildcard so mutmut regenerates and executes all current mutants in that symbol. It compares baseline survivors by diff fingerprint and groups unresolved current mutations by status and fingerprint; use `--verbose` only when unstable numeric mutant IDs are needed for diagnosis. Treat `not generated` as requiring a legitimate source-change explanation, not as a kill.

3. Run the exact repository commit gate plus required format, lint, type, focused, and broader test checks. Build a deduplicated validation plan: do not separately run a broad check already contained in the discovered gate, but do retain focused checks and any required checks the gate omits. Resolve validation-environment limitations before spending time on the final full mutation pass.
4. Run a final complete mutation pass without deleting generated state:

   ```bash
   <project-python> <skill-dir>/scripts/mutmut_control.py --mutmut <mutmut-path> run --report-name final
   ```

Compare the selected group by diff rather than numeric mutant ID:

```bash
<project-python> <skill-dir>/scripts/mutmut_control.py compare \
  --before initial --after final --symbol '<exact selected symbol>'
```

Confirm that original survivor diffs no longer survive for a legitimate reason, that the affected group has no new relevant survivor, and that its final per-symbol statuses contain no unexplained timeout or error. The comparison can prove persistence or absence from the survivor set; use the scoped rerun and source diff to distinguish killed from no longer generated. Never infer a kill from ordinary tests, unchanged global timeout counts, or a missing old mutant name alone.

## Commit only valuable changes

When valuable changes were made and validation passed, create one Conventional Commits commit containing only this iteration's changes. Use the subject for the change and the body for the behavioral risk, missing guarantee, ambiguity, or maintainability problem it resolves. Do not narrate the diff, invent rationale, commit `mutants/`, or create an empty commit.

## Report compactly

Report:

### Outcome
Whether a material change and commit were made, plus commit hash and message when applicable. Distinguish tracked working-tree status from retained ignored mutation state, and confirm generated state was not committed.

### Mutation run
Initial and final commands and counts for total, killed, survived, timeout, error, and other available statuses; note limitations.

### Ranked findings
List the selected group first, followed by the most important deferred groups. For each give symbol/file, representative mutation, behavioral effect, evidence-based assessment, and disposition. State that all groups in `mutants/triage-initial.md` were reviewed; do not reproduce hundreds of low-value entries. Briefly state why the selected group outranked its nearest contender.

### Selected finding
Explain original behavior, surviving mutation, why it mattered, why tests missed it, and whether the root issue was tests, production, specification, or tooling.

### Resolution and verification
Explain the change's material value, the actual test boundary and any implementation coupling, why that coupling is proportionate, commands and outcomes, and direct mutation evidence. Do not describe an interaction test as end-to-end or claim that it avoids private state when it does not.

### Remaining work
Name the leading deferred groups without changing them. Point to `mutants/triage-initial.md` for the reviewed all-group inventory and the `survivors-*.md` files for complete before-and-after details.
