---
name: agents-md-comparator
description: Compare two alternative AGENTS.md instruction bundles against the same repository using static analysis and isolated empirical Pi coding-agent runs, then generate a self-contained evidence viewer for human review. Use when choosing between competing AGENTS.md files or instruction hierarchies. Do not use for comparing ordinary implementation branches or documents unrelated to coding-agent instructions.
disable-model-invocation: true
---

# AGENTS.md Comparator

Compare two instruction bundles as operating guidance for a tool-using coding agent. Produce evidence; do not make the decision for the user unless explicitly asked.

Each option is a directory containing a root `AGENTS.md` and any related documentation or artifacts it references. Apply each bundle as an overlay to the same base repository. Never run an option against the user's working tree.

## Principles

Evaluate whether each bundle helps an LLM coding agent inspect, change, and validate a repository correctly and efficiently. Judge:

- correctness and consistency with the repository;
- empirical task performance and instruction adherence;
- terseness, directness, and signal-to-noise ratio;
- whether content belongs in `AGENTS.md` rather than being readily inferable from code or standard tooling;
- unnecessary constraints, repetition, and fluff;
- stale facts, brittle paths, version-sensitive details, and other maintenance hazards;
- whether instructions tell agents when and how to update durable guidance as the repository evolves;
- quality and navigability of referenced, drilled-down documentation.

Treat shorter as better only when it preserves useful guidance. Treat detailed guidance as valuable only when it changes agent behavior or prevents plausible mistakes.

## Inputs and safety

Require:

- an explicitly supplied base repository path;
- an explicitly supplied option A directory;
- an explicitly supplied option B directory; and
- an output workspace path, defaulting to `.agent-artifacts/agents-md-comparison-<timestamp>/`.

If any of the first three paths is missing or ambiguous, ask the user for it and stop. **Do not search the repository for likely candidates, infer options from fixtures or similarly named directories, or choose paths on the user's behalf.** Restate the three resolved paths before invoking the script.

Resolve paths before running anything. Confirm each option has a root `AGENTS.md`. Refuse an option directory that is the same as, contains, or is contained by the base repository when overlaying it could recurse or mutate source inputs.

The runner creates a fresh temporary repository for every option/task pair, overlays the selected bundle, commits that baseline, and runs Pi only there. It must not execute generated tasks in the source repository.

## Phase 1: prepare evidence and proposed evals

Run:

```bash
skills/agents-md-comparator/scripts/compare_agents.py prepare \
  --repo <base-repository> \
  --option-a <option-a-directory> \
  --option-b <option-b-directory> \
  --workspace <output-directory> \
  [--provider <provider>] [--model <model>] [--thinking <level>] \
  [--eval-count <count>] [--timeout <seconds>]
```

The script snapshots both bundles, records deterministic size/reference/staleness indicators, asks a neutral Pi evaluator for a qualitative static review, asks Pi for repository-specific empirical tasks, and writes:

- `manifest.json` — paths, hashes, Pi configuration, and timestamps;
- `static-analysis.json` — deterministic and qualitative static evidence;
- `evals.json` — proposed empirical tasks;
- `review.html` — a self-contained preview.

Read `evals.json` completely. Present every proposed task to the user with its purpose, expected evidence, and validation. Explicitly ask whether they want to add, remove, or revise any task. Do not start empirical runs until the user approves the exact set. If the user requests changes, edit `evals.json`, show the revised set, and request approval again.

A useful eval set is small and discriminating. It should normally cover:

1. a representative code change requiring repository discovery and validation;
2. correct use of genuinely non-obvious project guidance or drilled-down docs;
3. resistance to stale, redundant, or inferable instructions;
4. maintenance of `AGENTS.md` or related guidance when a task makes it materially outdated.

Do not create artificial tasks whose only purpose is to reward wording unique to one option. Tasks must be feasible in isolated copies, avoid external side effects, and have observable completion criteria. Do not include secret-dependent, destructive, deployment, or network-dependent tasks.

## Phase 2: run approved evals

After explicit approval, run:

```bash
skills/agents-md-comparator/scripts/compare_agents.py run \
  --workspace <output-directory> \
  --approved \
  [--provider <provider>] [--model <model>] [--thinking <level>] \
  [--timeout <seconds>] [--concurrency <count>]
```

Use one run per option per task. Keep provider, model, thinking level, tools, timeout, and prompt identical across options. The script runs Pi in JSON mode with ephemeral sessions, disables unrelated skills/extensions/templates/themes and ambient context files, explicitly appends only the staged root `AGENTS.md`, and enables the standard coding tools `read,bash,edit,write`.

The runner stores, for each task and option:

- Pi's event stream and final response;
- elapsed time and available usage data;
- repository status and patch;
- validation command outputs;
- execution errors and timeouts.

It then performs a blind Pi comparison with randomized A/B labels. Blind judgments are supporting evidence, not the user's decision. Preserve ties and evaluator uncertainty rather than forcing a winner.

## Review the result

The completed `review.html` must expose:

- both snapshotted instruction bundles;
- static findings with file-level evidence;
- all approved task prompts and validation rules;
- side-by-side responses, patches, validation results, timing, and usage;
- blind-grader findings with the hidden labels revealed only in the report;
- aggregate factual summaries without an automatic final recommendation.

Open or report the exact path to `review.html`. Summarize material evidence and limitations, including the fact that one run per task does not measure run-to-run variance. Ask the user which option they prefer or what follow-up evidence they need. Recommend a winner or hybrid only if the user asks; if proposing a hybrid, identify exact parts to retain and maintenance costs introduced.

## Interpretation guardrails

- Separate deterministic facts, evaluator judgments, and user judgments.
- Do not reward an option merely for mentioning more topics.
- Do not penalize omitted facts that a competent agent can cheaply and reliably infer.
- Penalize wrong instructions more heavily than missing convenience guidance.
- Treat token count as context, not a quality score. Counts use tiktoken's `o200k_base` encoding as a rough usage estimate.
- Attribute performance differences cautiously when patches are both correct.
- Report contamination, failed validation, malformed evaluator output, timeout, or missing evidence prominently.
- Never silently regenerate approved evals during `run`.
