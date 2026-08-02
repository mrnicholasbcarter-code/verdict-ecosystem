# Verdict Ecosystem Story Completion

- **Date:** 2026-08-02
- **Scope:** CON-001, NOD-002, CTX-002, PRO-001, SWARM-001
- **Authority:** `verdict-core`; Node, Ruflo, memory, and domain repositories remain adapters/providers.
- **Rule:** Reuse existing contracts and fail closed. No second policy authority.

## Stories

| ID | Story | Priority | Dependency | Status |
| --- | --- | --- | --- | --- |
| CON-001 | Cross-repository contract and release compatibility gate | P0 | Shared fixtures and package metadata | Planned |
| NOD-002 | Enforce Core `ExecutionEnvelope` at the Node edge | P0 | Core envelope contract and TypeScript parity | Planned |
| CTX-002 | Governed context and memory provider conformance | P1 | `MemoryGate`, `MemoryPlane`, context schemas | Planned |
| PRO-001 | Standard provider receipts for risk, strategy, and backtest | P1 | Shared receipt contract | In progress |
| SWARM-001 | Governed `SwarmSpec` and supervisor protocol | P1 | Envelope, evidence, and Ruflo lifecycle contracts | Planned |

## Existing Foundations

- Core: `verdict/contracts.py` already exposes `ExecutionEnvelope`, `TaskSpec`, `VerificationPlan`, and strict v1 parsing.
- Core: `verdict/gateway_adapters.py` and `verdict/gateway_adapter_runtime.py` define versioned adapter manifests, requests, responses, route identity, capability negotiation, and failure normalization.
- Core: `verdict/evidence_receipts.py` provides append-only, privacy-safe `EvidenceReceipt` and `EvidenceItem` contracts.
- Core: `verdict/memory_adapters.py`, `verdict/memory_gate.py`, and `verdict/memory_plane.py` provide provider-neutral adapters, redaction, provenance, retention, supersession, tombstones, and explicit unavailable states.
- Core: `verdict/ruflo_adapter.py`, `verdict/swarm_contracts.py`, `verdict/swarm_dispatcher.py`, and `verdict/lifecycle_controller.py` provide bounded orchestration, pause/resume/cancel, budgets, capability filtering, and verification hooks.
- Node: `@bodanglin/verdict-contracts` is the canonical TypeScript dependency; `src/middleware/forwarder.ts` shares one pre-forward path for JSON and SSE.
- Domain repositories: risk, strategy, and backtest expose deterministic APIs that must remain free of orchestration and network authority.

## Execution Order

1. Freeze Core Python/TypeScript/JSON fixtures for the shared envelope, context, receipt, and swarm contracts.
2. Add Node envelope parsing and enforcement before upstream forwarding; use the same guard for streaming and non-streaming requests.
3. Add Core context-provider conformance around the existing memory gate/plane and adapter registry.
4. Add thin deterministic provider receipt adapters for risk, strategy, and backtest.
5. Add validated `SwarmSpec` and supervisor evidence on top of existing Ruflo/swarm lifecycle primitives.
6. Add the ecosystem compatibility manifest, deterministic checker, report artifact, and CI release gate.

## Acceptance Gates

### CON-001

- Matrix covers Core, Node, risk, strategy/edge, backtest, cockpit, and ecosystem.
- Schema/API fixture drift, incompatible major versions, missing repositories, and untrusted generated schemas fail with exact field/repository diagnostics.
- Package/repository naming mismatches are explicit policy-controlled warnings or failures.
- Dry-run release validation is offline and emits no credentials or PII.

### NOD-002

- Valid canonical envelopes round-trip Python to TypeScript.
- Missing, expired, tampered, wrong-version, over-budget, disallowed-model, and disallowed-tool requests fail before forwarding.
- Node never recalculates Core eligibility.
- JSON and SSE use the same enforcement path.
- Denials expose stable machine-readable codes.

### CTX-002

- Retrieval is advisory and cannot authorize execution.
- Writes pass through `MemoryGate`; unverified or secret-bearing writes are rejected or quarantined.
- Namespace, provenance, authority, retention, redaction, and rollback/supersession survive round trips.
- Provider outages produce explicit `unknown`, `degraded`, or `unavailable` health states.

### PRO-001

- Risk, strategy, and backtest pass one shared request/result fixture.
- Receipts contain run ID, provider identity/version, input/config hashes, outcome, provenance, and evidence references.
- Replaying identical inputs is deterministic.
- Providers cannot authorize execution.
- Malformed, timed-out, or unavailable output becomes explicit degraded/unknown state.

### SWARM-001

- Invalid roles, duplicate IDs, missing verification, invalid budgets, and unbounded concurrency are rejected.
- Every delegated slice has a bounded envelope and evidence reference.
- Pause, resume, cancel, deterministic conflict resolution, and replay are tested.
- Supervisor messages cannot mutate envelopes or escalate capabilities.

## Verification Record

Every story requires targeted tests plus repository-native checks. Minimum commands:

```text
Core: uv run pytest -q; ruff check; ruff format --check; mypy --strict; python -m build; git diff --check
Node: npm run typecheck; npm run format:check; npm run build; npm test; npm run verify:package; npm run pack:dry-run
Domain repos: pytest; ruff; mypy; package build; git diff --check
Ecosystem: offline compatibility checker; fixture drift/missing-repository tests; workflow validation; git diff --check
```

Generated evidence belongs in ignored or explicit evidence directories. Existing uncommitted user work, story files, generated evidence, and worktree changes must not be reset, cleaned, or overwritten.

## Current Implementation Note

`verdict/provider_receipts.py` defines the first shared deterministic provider receipt primitive. It stores hashes instead of raw inputs, rejects sensitive metadata, validates schema/version, and remains informational rather than authoritative. Domain adapters and conformance tests must build on this primitive before the compatibility gate is finalized.
