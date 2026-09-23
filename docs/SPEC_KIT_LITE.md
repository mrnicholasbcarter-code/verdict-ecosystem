# Spec Kit Lite

**Status:** Canonical Verdict V2 change contract  
**Owner:** [`verdict-ecosystem`](../README.md)  
**Linear owner:** [BOD-167](https://linear.app/bodanglin/issue/BOD-167/ecosystemp0-restore-canonical-spec-kit-lite-change-contract-for)

## Definition

**Spec Kit Lite** is Verdict project shorthand for the minimum written contract
required before significant work starts. It is not a claim of conformance to an
external formal standard. It keeps the useful parts of specification-driven work
without requiring full Spec Kit commands, generated plans, or ceremonial task
files.

The contract answers **what outcome is required, what evidence is known, what may
change, and what exact proof makes the change complete**. Linear owns planning and
work state. Git and GitHub own source, review, and merge truth. CI and runtime
receipts own verification. A Spec Kit Lite record links those systems; it does not
replace them.

## V2 boundary

This process covers significant Verdict V2 work in the **Prime + Verdict +
OmniRoute** product boundary. Harness-agnostic and gateway-agnostic product work is
V3-deferred. A V2 change may document a concrete Prime or OmniRoute interface; it
must not broaden the product into generic harness or gateway support by implication.

## When it is required

Create or update a Spec Kit Lite record before implementation when a change affects
one or more of:

- public behavior, commands, configuration, packages, or documentation claims;
- architecture or an Architecture Decision Record (ADR);
- a cross-repository, API, schema, receipt, compatibility, or version contract;
- security, trust, privacy, authorization, or protected effects;
- routing, context, memory, model-selection, or spend semantics;
- persistent data, migration, rollback, deployment, release, or recovery;
- benchmark, performance, cost, quality, or other public evidence claims; or
- more than one repository.

A typo-only documentation edit, mechanical formatting change, or local refactor that
does not change behavior or a contract may use the repository's ordinary issue and
pull-request description. If the boundary is unclear, use Spec Kit Lite.

## Evidence language

Use these labels where an evidence boundary affects a decision or claim:

- **KNOWN** — directly supported by an authoritative source, exact repository state,
  deterministic check, CI result, registry, deployment, or runtime receipt. Cite it.
- **INFERRED** — a reasoned conclusion from named evidence. State the inference and
  do not present it as observed behavior.
- **NOT AVAILABLE** — evidence was sought but cannot currently be obtained. Name the
  missing evidence and the resulting blocker or claim limit.

`INFERRED` and `NOT AVAILABLE` cannot satisfy an acceptance criterion that requires
observed runtime, release, security, or compatibility proof.

## Minimum change contract

A conforming record contains every heading in the copy-ready template below. A
heading may say `Not applicable` only with a short reason. It must not be omitted.

### Problem / desired outcome

State the user or product problem and the observable result. Do not prescribe an
implementation unless it is an actual constraint.

### Evidence boundary

List material **KNOWN**, **INFERRED**, and **NOT AVAILABLE** facts with source paths,
issue/PR links, exact revisions, commands, or receipts.

### Scope

Name owning repositories, allowed surfaces, and the smallest coherent change.

### Non-goals

Name nearby work that this change intentionally does not own. Include V3-deferred
work when the boundary could otherwise be ambiguous.

### Acceptance criteria

Use verifiable outcomes. Separate shipped behavior from planned behavior. A file edit
or PR-open state is not an outcome.

### Affected interfaces / contracts

List APIs, schemas, packages, CLI commands, configuration, receipts, cross-repository
consumers, and compatibility/version boundaries. Say `None` with evidence when there
is no interface impact.

### Implementation constraints

Record branch/worktree ownership, dependency or version limits, performance budgets,
platform requirements, and files or lanes that must not be touched.

### Security / trust implications

Cover input and context trust, credentials, privacy, authorization, fail-open versus
fail-closed behavior, protected effects, supply chain, and publication risk.

### Routing / context / memory implications

When applicable, cover admission and model selection, context provenance and budget,
memory reads/writes/retention, cost controls, receipts, and degraded behavior. Use
`Not applicable — <reason>` when the change cannot affect these semantics.

### Test / proof requirements

Name deterministic local commands, focused and regression tests, contract checks,
failure paths, independent review, CI checks, runtime proof, and exact-SHA binding.
Do not substitute LLM judgment for checks that can be deterministic.

### ADR impact

Choose one and explain it: no ADR impact; update a current ADR; supersede an ADR while
preserving history and naming its successor; or add a missing decision record. Never
rewrite an old ADR to imply that its superseding decision was always true.

### Documentation impact

List canonical documents and examples to update, stale documents to label/archive,
and links/commands to verify. Planned behavior must stay labeled planned.

### Migration / rollback

Describe ordering, compatibility windows, data/config migration, reversible steps,
rollback triggers, and the last known-safe state. Use `Not applicable — <reason>` for
changes with no migration or rollback effect.

### Evidence required for completion

List the artifacts required to move through review, PR, CI, merge, and
`MAIN_VERIFIED`: exact source SHA, commands/results, CI URL or run identity, merged PR,
resulting default-branch SHA, registry/deployment/runtime receipt where applicable,
and unresolved limits.

## Copy-ready template

Copy this block into the owning repository's normal specification location or into
the Linear story when no repository-local spec file is useful.

```markdown
# <change title>

## Problem / desired outcome

## Evidence boundary
- KNOWN:
- INFERRED:
- NOT AVAILABLE:

## Scope

## Non-goals

## Acceptance criteria
- [ ]

## Affected interfaces / contracts

## Implementation constraints

## Security / trust implications

## Routing / context / memory implications

## Test / proof requirements

## ADR impact

## Documentation impact

## Migration / rollback

## Evidence required for completion
```

## Lifecycle and authority

Use the project lifecycle without inventing parallel status systems:

`DISCOVERED → OWNED → SPECIFIED → IMPLEMENTING → LOCAL_VALIDATION → REVIEW → PR_OPEN → CI_GREEN → MERGED → MAIN_VERIFIED → DONE`

- **OWNED:** Linear names the accountable story, repository, and dependencies.
- **SPECIFIED:** the minimum contract is complete enough to implement safely.
- **LOCAL_VALIDATION:** required local proof passes at the recorded SHA.
- **REVIEW:** changed behavior, interfaces, trust boundary, docs, and ADR impact are
  independently checked.
- **CI_GREEN:** required checks finish successfully on the exact PR head SHA.
- **MAIN_VERIFIED:** the resulting default-branch SHA is pulled or queried and the
  relevant proof is rerun or confirmed there.
- **DONE:** all acceptance criteria have evidence and remaining gaps have explicit
  Linear owners. `PR_OPEN` and `MERGED` are not completion.

If code, current runtime behavior, GitHub, CI, or Linear contradicts the record,
reconcile the record before acting. Current authoritative evidence wins over a stale
specification.

## Relationship to legacy Spec Kit material

Repository-local `specs/` and `.specify/` files remain historical or feature-specific
evidence. A repository may use them, a stricter local template, or the contract above.
Do not duplicate a record only to satisfy directory ceremony.

[BOD-16](https://linear.app/bodanglin/issue/BOD-16/corephase-0-reconcile-and-close-legacy-spec-kit-mirror-issues-across)
closed the obsolete mirrored-task reconciliation process. It is not the owner of this
change contract, and its canceled mirror workflow must not be revived. Existing
artifacts and closed issues retain their historical state; real remaining work belongs
in bounded Linear stories.

## Review checklist

- [ ] Trigger and V2/V3 boundary are correct.
- [ ] Every minimum heading is present and substantive or explicitly not applicable.
- [ ] Evidence labels do not overstate inference as observation.
- [ ] Repository and interface owners agree on contract and rollout order.
- [ ] Security, routing, context, memory, spend, and failure paths were considered.
- [ ] Tests and proof bind claims to exact source and runtime/release evidence.
- [ ] ADRs and canonical docs preserve history and shipped/planned truth.
- [ ] Rollback is executable or explicitly not applicable.
- [ ] Linear owns every remaining gap.
- [ ] Default-branch verification is required before `DONE`.
