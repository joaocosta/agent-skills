---
name: grill-me
description: Conduct a rigorous, one-question-at-a-time design interview that challenges assumptions, resolves material product and architecture decisions, and persists a self-contained, implementation-ready design record for a separate handoff session. Use when the user asks to be grilled or wants a feature, system, plan, or technical proposal stress-tested before implementation. Do not use for ordinary troubleshooting, routine code review, or straightforward implementation with settled requirements.
disable-model-invocation: true
---

# Grill Me

Develop and persist an implementation-ready design. Resolve uncertainty that could materially change behavior, architecture, scope, risk, migration, operations, or acceptance. Do not pursue details that can safely remain implementation discretion.

The durable `design.md` is the sole contract with downstream handoff sessions. Assume they receive no design-session conversation, memory, or unstated repository findings.

## Ground the interview

Before asking questions, inspect relevant code, documentation, tests, configuration, and existing design artifacts. Keep inspection proportional to active decisions. Inspect history only when current evidence is ambiguous or prior rationale matters.

Do not ask the user for facts available from repository evidence. Treat evidence as potentially incomplete or stale, and do not mistake existing behavior for intended behavior. Surface material conflicts among code, tests, documentation, authoritative sources, and user statements. When no repository is available, state the assumptions needed to begin and proceed.

Use these distinctions:

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

Maintain a compact design record in the conversation from the start. Record conclusions and evidence, not dialogue. Replace superseded conclusions rather than retaining contradictions. Preserve rejected alternatives only when their rationale prevents costly reconsideration.

Use a stable lowercase kebab-case initiative slug. Once clear, identify `.agent-artifacts/<initiative-slug>/design.md`; reuse the slug throughout and state it at major checkpoints. Inspect an existing initiative directory before writing and ask before replacing an existing design unless the user explicitly requested its update.

After each answer, show a brief plain-language summary under **What I recorded from your answer** so the user can verify how their answer changed the design. Include only new, changed, or removed conclusions; omit internal bookkeeping and unchanged context. Reprint the full compact record only at major checkpoints, on request, or at completion.

The record must stand alone for agents in clean contexts. Capture, when material:

- problem, users, current behavior, goals, non-goals, and deferred work;
- numbered, externally observable acceptance criteria;
- stable codebase anchors: repository-relative paths where possible, symbols, tests, commands, design artifacts, and authoritative external references;
- constraints, invariants, interfaces, ownership, security boundaries, compatibility, and failure behavior;
- decisions, rationale, assumptions, accepted risks, and important rejected alternatives;
- architecture, data flow, dependencies, and natural implementation seams;
- edge and abuse cases, recovery, migration, rollout, rollback, observability, and operations;
- security, privacy, accessibility, capacity, and performance implications;
- validation strategy, open questions, blockers, and readiness; and
- an implementation outline sufficient for a different agent to decompose without rediscovering the design.

The implementation outline is not a task list. Describe ordered or dependent implementation units at the smallest natural seams established by the design. For each unit, state its concrete outcome, owned behavior/components, dependencies and reusable outputs, relevant anchors, focused validation, and acceptance-criterion IDs covered. Call out coupling that must remain together and boundaries that can be implemented and committed independently. Avoid vague phases such as “build backend,” “implement module,” or “add tests.” Do not prescribe incidental file structure or sequencing that should remain implementation discretion.

Do not mechanically cover every category; include only what could affect implementation, decomposition, or acceptance. Prefer stable paths and symbols over line numbers. Do not rely on facts merely remaining in conversation: either record a durable anchor and the relevant finding or omit it as immaterial.

Do not request or record secrets, credentials, production customer data, or unrelated personal information.

Write only `.agent-artifacts/<initiative-slug>/design.md`; `handoff.md`, `README.md`, `progress.md`, and `tasks/` belong to `handoff`. Do not modify production code or other repository documentation during the interview.

## Run the interview

After each user answer:

1. Update the record, including every branch the answer settled.
2. Identify contradictions, changed assumptions, and newly opened or closed branches.
3. Select the highest-impact unresolved decision by materiality, dependencies, uncertainty, and reversal cost.
4. Resolve foundational and hard-to-reverse decisions before local or reversible ones.
5. Ask one concrete, non-compound question.

Optimize each turn for the human making the decision: first confirm what was understood from their preceding answer, then present the next actionable question and its supporting context. Use this order:

1. **What I recorded from your answer:** Briefly summarize only conclusions added, changed, or removed because of the user's preceding answer. Use direct domain language rather than unexplained record taxonomy. Keep this confirmation compact—usually one to three bullets—so it does not bury the next question. Omit it on the first turn, when there is no preceding answer.
2. **Question:** Ask exactly one concrete question that advances the design.
3. **Why I'm asking:** Explain the consequence of leaving the decision unresolved. Cite evidence or prior decisions when relevant.
4. **Recommendation:** Recommend an answer when evidence, principles, risk, or reversibility support one; state assumptions and tradeoffs. Otherwise offer two to four viable options and the selection criterion.

If useful, end with the anticipated next topic on a separate **Coming next:** line rather than presenting it as a record change. Keep the question easy to find even when the rationale is substantial. The recommendation supports the question; it must not obscure or restate it.

Challenge vague success criteria, unsupported assumptions, accidental scope, and solutions without a clear problem. If an answer conflicts with evidence, goals, or prior decisions, explain the conflict and ask which premise should change. Never silently reinterpret an answer.

If the user cannot decide, identify the decision owner or source of truth. Propose the cheapest useful evidence, experiment, or reversible default and explain what uncertainty it addresses before requesting approval for environment-changing work. Record the result with the correct status.

After each major branch, show a compact **Design checkpoint**, introduced as a chance for the user to correct the evolving design. Summarize settled decisions, changed assumptions, accepted risks, blockers, and remaining high-impact questions in plain language. Let the user correct drift, then continue with one question. If no material question remains, proceed to completion.

## Converge and persist

Before finishing, reread the proposed artifact as both:

1. an implementation agent with no conversation; and
2. a handoff agent that must create small fresh-context tasks from the implementation outline.

Continue the interview or strengthen the record if either agent would need to rediscover a material repository fact, invent behavior or architecture, guess an acceptance boundary, or group work only because seams and dependencies are unclear.

Declare **ready for handoff** only when:

- goals, boundaries, numbered acceptance criteria, and validation are explicit;
- material interfaces, constraints, invariants, compatibility, failure behavior, migration, and operations are settled to the design's risk;
- implementation-critical decisions are settled;
- the implementation outline exposes independently verifiable seams, dependencies, reusable outputs, and unavoidable coupling; and
- no unresolved question would force a downstream agent to reopen product or architecture decisions.

Accepted risks may remain only when consequence and owner are explicit and no behavior must be invented. If blocked or stopped early, mark **not ready for handoff** and list each blocker with the decision, owner, or evidence needed; an implementation outline may remain partial.

At completion:

1. Render the self-contained record with initiative, status, and artifact path in the document.
2. Write it to `.agent-artifacts/<initiative-slug>/design.md`, creating only the initiative directory if needed.
3. Reread the persisted file from disk, not the conversational draft. Check anchors, numbered criteria, outline coverage, decisions, risks, assumptions, blockers, and readiness.
4. Report the exact path, readiness, and remaining non-blocking assumptions and accepted risks.

Do not implement production code or create detailed execution tasks. A later, separate `handoff` session owns decomposition and packaging from the persisted artifact.
