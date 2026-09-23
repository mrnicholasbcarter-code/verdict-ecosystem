# Verdict V2 ADR Lifecycle Index

> **Evidence boundary:** This index records where each architectural decision
> is claimed and how that claim was verified. Classification counts are generated
> from `evidence/ADR_LIFECYCLE.json`, which in turn derives from exact
> default-branch snapshots. Source-level checks only; see *Proof status* below.

**Base SHA:** `7de8fc2e85e3ed07829583e30c848bb44d75bc21` (`origin/main` after BOD-167).

## Scope

Frozen V2 = Prime + Verdict + OmniRoute.

`verdict-continuity` decisions are classified `V3_DEFERRED` because
harness-independent continuity is outside the frozen V2 scope. They are retained
here for traceability, not as active V2 behavior.

## Source snapshots (authoritative, exact)

| Repository | Branch | SHA |
|---|---|---|
| verdict-core | origin/main | cae6aa673f606ac9a5315ae1e968acac5652a957 |
| verdict-core-memory | origin/main | c8935bb5222f3962f48e36567114d0a3e5f9d1b4 |
| verdict-node | origin/master | 3e1a5ba78ba3a24de85d48e663113a3a7bf7e3c2 |
| verdict-continuity | origin/main | 9d07081661efa51f7570b13b1e54f69975de7cfb |

Captured at `2026-09-23T03:01:40.745326Z`. Branch refs are provenance labels at
capture time; the exact commit SHAs are the durable authority and may no longer
match moving default branches.

## Counts (production files only)

| Metric | Value |
|---|---|
| Raw ADR-like files discovered | 72 |
| Benchmark fixtures excluded | 1 |
| Production files audited | 71 |
| Exact duplicate SHA-256 groups | 23 |
| Files covered by exact duplicates | 46 |

## Lifecycle classifications

| Classification | Count |
|---|---|
| CURRENT | 0 |
| PARTIALLY_TRUE | 35 |
| SUPERSEDED | 1 |
| DUPLICATE | 25 |
| STALE | 8 |
| MISSING_SUCCESSOR | 1 |
| INVALID | 1 |

## Evidence levels

| Level | Meaning | Count |
|---|---|---|
| VERIFIED | Exact path/hash/code evidence at the snapshot | 55 |
| INFERRED | Namespace/logical inference, not byte-identity or test proof | 8 |
| NOT_VERIFIED | Declaration found, executable evidence not established | 8 |

## Exact duplicates

`verdict-core-memory` publishes byte-identical copies of `verdict-core` ADRs.
verdict-core owns these decisions. The full hash groups are in
`evidence/ADR_LIFECYCLE.json` under `duplicate_groups`.

## Production ADR index

Each source locator has the form `repository@exact-commit:path`. These are immutable source identifiers; repository access may require authorization.

| Source locator | Lifecycle | Evidence | V2 relevance |
|---|---|---|---|
| `verdict-continuity@9d07081661efa51f7570b13b1e54f69975de7cfb:docs/adr/001-independent-core.md` | STALE | VERIFIED | V3_DEFERRED |
| `verdict-continuity@9d07081661efa51f7570b13b1e54f69975de7cfb:docs/adr/002-foundation-contract-boundary.md` | STALE | VERIFIED | V3_DEFERRED |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/0001-verdict-control-plane-invariants.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-001-evidence-ledger.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-002-orchestrator-routing.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-003-platform-neutral-guidance-boundary.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-004-local-first-memory-plane.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-005-code-intelligence-graph-memory-bridge.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-006-authoritative-documentation-preflight.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-007-omniroute-catalog-qualification.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-008-global-runtime-ownership.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-009-durable-memory-write-gate.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-010-fail-closed-capability-passports.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-011-omniroute-catalog-qualification-baseline.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-012-consented-budgeted-probes.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-013-independent-protocol-surface-qualification.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-014-tool-and-structured-output-qualification.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-015-evidence-authority-and-portable-receipts.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-016-deterministic-policy-and-transition-graphs.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-017-durable-privacy-safe-receipt-ledger.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-018-shadow-and-counterfactual-evaluation.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-019-runtime-negotiated-passports.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-020-gateway-adapter-contracts.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-021-deterministic-provider-receipts.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-022-context-provider-conformance.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-023-governed-swarm-supervision.md` | MISSING_SUCCESSOR | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-024-cross-repo-compatibility-gate.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-025-node-envelope-enforcement.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-026-responses-compatibility-boundary.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-027-observed-free-status-and-context-omissions.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-028-launch-gate-tooling.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-029-portfolio-repositioning-plan.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-030-proof-carrying-decision-plane.md` | PARTIALLY_TRUE | NOT_VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-031-prime-workflow-skills.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-032-core-model-metadata-store.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-033-shared-memory-provider.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-034-memory-outbox-mirror-and-fail-open-shared-recall.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/ADR-ORCHESTRATOR-ROUTING.md` | SUPERSEDED | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/adr/README.md` | INVALID | VERIFIED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/architecture/ADR-EVIDENCE-LEDGER.md` | DUPLICATE | INFERRED | ACTIVE |
| `verdict-core@cae6aa673f606ac9a5315ae1e968acac5652a957:docs/architecture/ADR-ORCHESTRATOR-ROUTING.md` | DUPLICATE | INFERRED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-001-evidence-ledger.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-002-orchestrator-routing.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-003-platform-neutral-guidance-boundary.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-004-local-first-memory-plane.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-005-code-intelligence-graph-memory-bridge.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-006-authoritative-documentation-preflight.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-006-hybrid-code-intelligence-graph.md` | STALE | INFERRED | OUTSIDE_ACTIVE_V2 |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-007-omniroute-catalog-qualification.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-007-unified-memory-replacement.md` | STALE | INFERRED | OUTSIDE_ACTIVE_V2 |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-008-global-runtime-ownership.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-008-infinite-context-and-observability.md` | STALE | INFERRED | OUTSIDE_ACTIVE_V2 |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-009-durable-memory-write-gate.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-009-governed-learning-and-retirement.md` | STALE | INFERRED | OUTSIDE_ACTIVE_V2 |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-010-fail-closed-capability-passports.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-011-omniroute-catalog-qualification-baseline.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-012-consented-budgeted-probes.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-013-independent-protocol-surface-qualification.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-014-tool-and-structured-output-qualification.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-015-evidence-authority-and-portable-receipts.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-016-deterministic-policy-and-transition-graphs.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-017-durable-privacy-safe-receipt-ledger.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-018-shadow-and-counterfactual-evaluation.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-019-runtime-negotiated-passports.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-020-gateway-adapter-contracts.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-020-responses-compatibility-boundary.md` | STALE | INFERRED | OUTSIDE_ACTIVE_V2 |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-021-deterministic-provider-receipts.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/adr/ADR-ORCHESTRATOR-ROUTING.md` | STALE | INFERRED | OUTSIDE_ACTIVE_V2 |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/architecture/ADR-EVIDENCE-LEDGER.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-core-memory@c8935bb5222f3962f48e36567114d0a3e5f9d1b4:docs/architecture/ADR-ORCHESTRATOR-ROUTING.md` | DUPLICATE | VERIFIED | ACTIVE |
| `verdict-node@3e1a5ba78ba3a24de85d48e663113a3a7bf7e3c2:docs/adr/ADR-001-execution-envelope-enforcement.md` | PARTIALLY_TRUE | VERIFIED | ACTIVE |

## Proof status and limitations

- **This index is source-level evidence.** Source/test path presence alone does
  not constitute end-to-end runtime proof.
- `CURRENT` is **withheld** for every record unless this audit establishes
  executed semantic proof against the exact snapshot. No record is marked CURRENT.
- `ADR-023` (Governed Swarm Supervision) is `MISSING_SUCCESSOR`; it declares
  itself superseded but names no successor ADR. BOD stories and dispatcher components
  are implementation references, not a successor decision record.
- Legacy `docs/architecture/` copies in verdict-core and verdict-core-memory
  overlap the canonical `docs/adr/` namespace; they are classified `DUPLICATE`
  based on topic overlap unless exact hashes establish them.
- Non-identical `verdict-core-memory` decisions are classified `STALE` for V2
  with `INFERRED` evidence because repository authority is unresolved, not
  because their code is disproved.
- Continuity decisions are `V3_DEFERRED`.

Full machine-readable data is in `evidence/ADR_LIFECYCLE.json`. Default CI protects
the reviewed semantic digest and rendered index, then verifies the independently
generated immutable `evidence/ADR_SOURCE_MANIFEST.json`. That manifest binds the
exact repository URL, commit, complete ADR inventory, source and fixture hashes,
and every required citation path without requiring private-repository credentials.
It is pinned by a trusted code digest, so source/index/manifest drift fails closed.
Run `python3 scripts/verify_adr_sources.py` for this default check. Reviewers with
local repositories containing the pinned commits run
`python3 scripts/verify_adr_sources.py --repo-root <directory>` to independently
recompute the manifest facts from exact Git objects during refresh or audit.
