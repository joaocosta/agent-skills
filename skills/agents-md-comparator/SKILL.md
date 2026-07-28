---
name: agents-md-comparator
description: Measure how a repository's AGENTS.md guidance changes coding-agent performance by running identical evals with and without all root and nested AGENTS.md files, or compare two alternative instruction bundles. Uses static analysis, isolated empirical Pi runs, and a self-contained evidence viewer. Use whenever evaluating whether AGENTS.md helps, whether instructions are worth keeping, or which of two AGENTS.md approaches performs better. Do not use for ordinary implementation-branch or unrelated document comparisons.
disable-model-invocation: true
compatibility: Requires uv, Pi, and git.
---

# AGENTS.md Comparator

Compare coding-agent instruction conditions over the same repository. Produce evidence; do not make the decision for the user unless explicitly asked.

Prefer the single-repository mode: compare the repository exactly as supplied against an otherwise identical copy with every root and nested `AGENTS.md` removed. Retain all referenced documents and other repository files in both conditions so the experiment isolates the effect of `AGENTS.md`. Label the conditions **With AGENTS.md** and **Without AGENTS.md**.

The legacy two-bundle mode remains available when the user explicitly supplies two standalone instruction-bundle directories. Each bundle must contain a root `AGENTS.md` and may contain related documentation or artifacts it references. Apply each bundle as an overlay to the same base repository.

Never run an empirical task in the user's working tree.

## Principles

Evaluate whether guidance helps an LLM coding agent inspect, change, and validate a repository correctly and efficiently. Judge:

- correctness and consistency with the repository;
- empirical task performance and instruction adherence;
- terseness, directness, and signal-to-noise ratio;
- whether content belongs in `AGENTS.md` rather than being readily inferable;
- unnecessary constraints, repetition, and fluff;
- stale facts, brittle paths, and other maintenance hazards;
- whether guidance explains when and how to update durable instructions;
- quality and navigability of referenced, drilled-down documentation.

Treat shorter as better only when it preserves useful guidance. Treat detail as valuable only when it changes behavior or prevents plausible mistakes.

## Inputs and safety

Require:

- an explicitly supplied base repository path; and
- an output workspace path, defaulting to `.agent-artifacts/agents-md-comparison-<timestamp>/`.

For the normal with/without comparison, require no option directories. The repository must contain at least one file named exactly `AGENTS.md`, either at its root or nested beneath it. Stop with an error if it contains none.

For a two-bundle comparison, additionally require both option directories. If only one is supplied, ask for the other and stop. Do not search for or infer bundle paths. Restate the resolved repository and, when applicable, both bundle paths before invoking the runner.

Resolve paths first and reject unsafe symlinks. In two-bundle mode, confirm both options have a root `AGENTS.md`; reject overlapping option directories or an option that overlaps the repository.

The runner creates a fresh temporary repository for every condition/task pair and commits the experimental baseline before running Pi. In with/without mode, it removes every `AGENTS.md` only from the disposable **Without AGENTS.md** copy. In the with condition, root guidance applies repository-wide and nested guidance only to its directory and descendants; deeper guidance takes precedence within its scope.

## Runner invocation

Invoke the PEP 723 runner with `uv run --script`; do not use `python`, install dependencies manually, or create a venv. If `uv` is unavailable, stop and ask the user to install it.

### Phase 1: prepare evidence and proposed evals

For the preferred single-repository comparison:

```bash
uv run --quiet --script skills/agents-md-comparator/scripts/compare_agents.py prepare \
  --repo <repository> \
  --workspace <output-directory> \
  [--provider <provider>] [--model <model>] [--thinking <level>] \
  [--eval-count <count>] [--timeout <seconds>]
```

For two explicit bundles, add both arguments:

```bash
  --option-a <option-a-directory> --option-b <option-b-directory>
```

The script snapshots the instruction conditions, records deterministic size/reference/staleness indicators, requests a neutral static review and repository-specific empirical tasks, and writes:

- `manifest.json` — mode, labels, paths, hashes, Pi configuration, and timestamps;
- `static-analysis.json` — deterministic and qualitative static evidence;
- `evals.json` — proposed empirical tasks;
- `review.html` — self-contained preview.

Read `evals.json` completely. Present every task with its purpose, expected evidence, and validation. Ask whether the user wants to add, remove, revise, or approve tasks. Do not begin empirical runs until the exact set is explicitly approved. If edited, present the revised complete set and request approval again.

Use a small, discriminating eval set. It should normally cover representative implementation and discovery, genuinely non-obvious guidance, resistance to stale or inferable instructions, and instruction maintenance when a task materially changes durable guidance. Do not reward unique wording artificially. Tasks must work in isolated copies, avoid external side effects and network assumptions, and have observable completion criteria.

### Phase 2: run approved evals

```bash
uv run --quiet --script skills/agents-md-comparator/scripts/compare_agents.py run \
  --workspace <output-directory> \
  --approved \
  [--provider <provider>] [--model <model>] [--thinking <level>] \
  [--timeout <seconds>] [--concurrency <count>]
```

Use one run per condition per task. Keep model configuration, tools, timeout, and prompt identical. Pi uses ephemeral JSON sessions, disables unrelated resources and ambient context discovery, receives only the staged condition's explicitly scoped `AGENTS.md` guidance, and has `read,bash,edit,write` tools.

The runner captures event streams, responses, elapsed time, summed provider usage, tool calls and errors, repository status and patch, validations, execution failures, and timeouts. It writes aggregate efficiency evidence and performs a randomized blind comparison. Efficiency supports correctness and completeness; it does not determine the winner. Preserve ties and uncertainty.

## Review the result

The completed `review.html` exposes snapshotted conditions, static evidence, approved tasks, side-by-side outputs and patches, validation, usage and tool metrics, aggregates, and blind grades. It must use **With AGENTS.md** and **Without AGENTS.md** labels in single-repository mode and avoid an automatic recommendation.

Report the exact `review.html` path. Summarize material evidence and limitations, including that one run per task does not measure variance. Ask what the user prefers or what follow-up evidence they need. Recommend a winner or hybrid only when asked.

## Interpretation guardrails

- Separate deterministic facts, evaluator judgments, and user judgments.
- Do not reward guidance merely for mentioning more topics.
- Do not penalize omitted facts a capable agent can cheaply infer.
- Penalize wrong instructions more heavily than missing convenience guidance.
- Treat token and tool-call counts as context only after comparing correctness.
- Static token estimates use `o200k_base`; empirical usage is provider-reported.
- Treat missing usage as unavailable, never zero.
- Attribute differences cautiously when both patches are correct.
- Report contamination, failed validation, malformed output, timeout, or missing evidence prominently.
- Never silently regenerate approved evals during `run`.
