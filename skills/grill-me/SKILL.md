---
name: grill-me
description: Conduct a rigorous, one-question-at-a-time design interview that challenges assumptions, resolves material product and architecture decisions, and persists a self-contained, implementation-ready design record for a separate handoff session. Use when the user asks to be grilled or wants a feature, system, plan, or technical proposal stress-tested before implementation. Do not use for ordinary troubleshooting, routine code review, or straightforward implementation with settled requirements.
disable-model-invocation: true
---

# Grill Me

Develop and persist an implementation-ready design. Resolve uncertainty material to behavior, architecture, scope, risk, migration, operations, or acceptance; leave safe details to implementation discretion.

The durable `design.md` is the sole downstream contract. Assume handoff sessions receive no conversation, memory, or unstated repository findings.

## Ground the interview

Before asking questions, inspect relevant code, documentation, tests, configuration, and design artifacts in proportion to active decisions. Inspect history only when evidence is ambiguous or prior rationale matters.

Do not ask for facts available in the repository. Evidence may be incomplete or stale, and existing behavior may not be intended behavior. Surface material conflicts among code, tests, documentation, authoritative sources, and user statements. Without a repository, state the assumptions needed to proceed.

Distinguish evidence, provisional beliefs, settled choices, unresolved decisions, and intentionally tolerated or excluded work:

- **Fact** — supported by repository evidence or an authoritative source.
- **Assumption** — provisionally treated as true but not established.
- **Decision** — intentionally settled for this design.
- **Open question** — unresolved and capable of materially changing the design.
- **Blocker** — an open question that would force an implementer to invent product behavior, architecture, risk posture, compatibility, or acceptance semantics.
- **Accepted risk** — understood uncertainty or failure exposure intentionally tolerated by an identified owner.
- **Non-goal** — an intentionally excluded outcome.
- **Constraint** — a boundary the implementation must respect.
- **Deferred work** — desirable work postponed with a reason and, when useful, a trigger for reconsideration.

## Maintain the design record

Maintain a compact conversational design record from the start. Record conclusions and evidence, not dialogue; replace superseded conclusions, and preserve rejected alternatives only when their rationale prevents costly reconsideration.

Use a stable lowercase kebab-case initiative slug and identify `.agent-artifacts/<initiative-slug>/design.md` once clear. Inspect an existing initiative directory before writing and ask before replacing an existing design unless the user explicitly requested its update.

After each answer, summarize new, changed, or removed conclusions under **What I recorded from your answer** so the user can correct the interpretation. Omit bookkeeping and unchanged context. Reprint the full record only at major checkpoints, on request, or at completion.

The record must stand alone for agents in clean contexts. Capture, when material:

- problem, users, current behavior, goals, scope, non-goals, and deferred work;
- numbered, externally observable acceptance criteria;
- stable repository anchors and relevant findings: repository-relative paths where possible, symbols, tests, commands, design artifacts, and authoritative external references;
- decisions, rationale, assumptions, constraints, accepted risks, and rejected alternatives worth preserving;
- architecture, data flow, interfaces, invariants, ownership, dependencies, security boundaries, compatibility, and failure behavior;
- edge and abuse cases, security, privacy, accessibility, capacity, and performance;
- recovery, migration, rollout, rollback, observability, and operations; and
- validation, open questions, blockers, readiness, and an implementation outline sufficient for another agent to decompose without rediscovery.

The implementation outline describes natural implementation seams, not detailed tasks. For each unit, record its concrete outcome, owned behavior or components, dependencies and reusable outputs, relevant anchors, focused validation, and covered acceptance-criterion IDs. Identify independently committable boundaries and unavoidable coupling. Avoid vague phases and incidental file-level prescriptions that should remain implementation discretion.

Include only categories that affect implementation, decomposition, or acceptance. Prefer stable paths and symbols over line numbers, and record durable anchors with their relevant findings rather than relying on conversation.

Do not request or record secrets, credentials, production customer data, or unrelated personal information.

Write only `.agent-artifacts/<initiative-slug>/design.md`; do not modify production code or other repository documentation during the interview. Handoff and Ralph artifacts belong to `handoff`.

## Run the interview

After each user answer:

1. Update the record and reconcile every settled branch, contradiction, changed assumption, and newly opened or closed branch.
2. Select the highest-impact unresolved decision by materiality, dependency impact, uncertainty, and reversal cost, prioritizing foundational choices over local or reversible ones.
3. Ask exactly one concrete, non-compound question.

First confirm what changed because of the preceding answer, then present the next actionable question and its supporting context. Use this order:

1. **What I recorded from your answer:** Summarize only conclusions added, changed, or removed because of the answer. Keep it compact—usually one to three plain-language bullets—so it does not bury the question. Omit it on the first turn.
2. **Question:** Ask exactly one concrete question that advances the design.
3. **Why I'm asking:** Explain the consequence of leaving it unresolved, citing evidence or prior decisions when relevant.
4. **Recommendation:** Recommend an answer when evidence, principles, risk, or reversibility support one, stating assumptions and tradeoffs; otherwise offer two to four viable options and a selection criterion.

Optionally end with **Coming next:** naming the next topic without treating it as a record change. Keep the question easy to find; its recommendation must not obscure or restate it.

Challenge vague success criteria, unsupported assumptions, accidental scope, and solutions without a clear problem. When an answer conflicts with evidence, goals, or prior decisions, explain the conflict and ask which premise should change; never silently reinterpret it.

If the user cannot decide, identify the owner or source of truth. Propose the cheapest useful evidence, experiment, or reversible default and the uncertainty it addresses before seeking approval for environment-changing work. Record the result under the applicable taxonomy.

After each major branch, offer a compact **Design checkpoint** for correction. Summarize settled decisions, changed assumptions, accepted risks, blockers, and remaining high-impact questions. Correct drift, then continue with one question; if none remains, proceed to completion.

## Converge and persist

Before finishing, reread the proposed artifact as both:

1. an implementation agent with no conversation; and
2. a handoff agent that must create small fresh-context tasks from the implementation outline.

Continue the interview or strengthen the record if either reader would need to rediscover a material fact, invent behavior or architecture, guess an acceptance boundary, or infer implementation seams or dependencies.

Declare **ready for handoff** only when:

- goals, boundaries, numbered acceptance criteria, and validation are explicit;
- material behavior, interfaces, constraints, invariants, compatibility, migration, failure handling, and operations are settled in proportion to risk;
- no implementation-critical decision remains unresolved;
- the implementation outline exposes independently verifiable seams, dependencies, reusable outputs, acceptance-criterion coverage, and unavoidable coupling; and
- no unresolved question would force a downstream agent to reopen product or architecture decisions.

Accepted risks may remain only with an explicit consequence and owner and no behavior left to invent. If blocked or stopped early, mark **not ready for handoff**, list each blocker and the decision, owner, or evidence needed, and allow a partial implementation outline.

At completion:

1. Render the self-contained record with initiative, status, and artifact path in the document.
2. Write it to `.agent-artifacts/<initiative-slug>/design.md`, creating only the initiative directory if needed.
3. Reread the persisted file from disk and validate it against the artifact requirements and readiness gate, including anchor validity and acceptance-criterion coverage.
4. Report the exact path, readiness, and remaining non-blocking assumptions and accepted risks.

Do not implement production code or create detailed execution tasks. A separate `handoff` session owns decomposition and packaging from the persisted artifact.
