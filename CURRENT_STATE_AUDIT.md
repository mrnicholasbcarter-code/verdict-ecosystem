# Verdict Ecosystem Current-State Audit

- **Audit date:** 2026-08-02
- **Scope:** `verdict-core`, `verdict-node`, `verdict-risk`, `verdict-strategy`, `verdict-backtest`, `verdict-cockpit`, and `verdict-ecosystem`
- **Evidence:** local repository snapshots, source files, tests, manifests, ADRs, CI workflows, README files, Git history, and existing GitHub issue metadata
- **Authority:** this audit describes the current repositories; learned-agent suggestions are advisory only

## Executive Summary

Verdict is not starting from zero. `verdict-core` already contains a substantial deterministic routing and policy-control plane: versioned contracts, eligibility, capability passports, availability qualification, routing, evidence receipts, gateway adapters, lifecycle specifications, memory-plane integrations, and verification-oriented ADRs. `verdict-node` is a TypeScript gateway surface with canonical contract consumption, request validation, forwarding, and package verification.

The ecosystem is not yet a single execution-control-plane product. The repositories have different maturity levels and partially overlapping product identities. Core is the authority, but Node still contains policy-adjacent routing behavior; the domain repositories are specialized quantitative engines; the cockpit is currently a small UI/demo surface; and the umbrella repository is documentation-only. Ruflo, RuVector, OpenViking, and OmniRoute are referenced as integrations, but the architecture needs explicit adapter contracts, conformance tests, and fail-closed provider behavior to make those relationships contractual rather than operational convention.

The recommended direction is **reuse Core, extend its contracts and enforcement kernel, integrate external systems through adapters, and avoid a rewrite**. Do not move authority into Node or make Ruflo/RuVector/OmniRoute the architecture. Use versioned contracts and cross-language conformance fixtures to prevent policy drift instead of creating a second policy authority.

## Repository Inventory

| Repository | Current role | Evidence | Maturity | Reuse disposition |
| --- | --- | --- | --- | --- |
| `verdict-core` | Python control plane and routing authority | `verdict/`, `contracts/`, `schemas/`, `docs/adr/`, `tests/` | Alpha, largest and most mature | **Retain and extend** |
| `verdict-node` | TypeScript/Express middleware and OpenAI-compatible gateway | `src/middleware/`, `src/adapters/`, `tests/`, `package.json` | Alpha, package-focused | **Integrate and align** |
| `verdict-risk` | Deterministic risk gates and stateful risk authority | `src/trade_risk_engine/`, `tests/` | Alpha, focused library | **Adapt as a policy/risk provider** |
| `verdict-strategy` | Published package namespace `verdict-edge`; feature and expected-value evaluation | `src/edge_mining_framework/`, `tests/` | Alpha | **Adapt as a domain workflow/provider** |
| `verdict-backtest` | Monte Carlo, fee models, tearsheets, walk-forward primitives | `src/backtest_harness/`, `docs/ARCHITECTURE.md`, `tests/` | Alpha, focused library | **Adapt as simulation and verification provider** |
| `verdict-cockpit` | Next.js routing/trading dashboard prototype | `src/`, `tests/`, `.github/workflows/ci.yml` | Prototype/demo | **Replace mock data with control-plane APIs; retain UI shell** |
| `verdict-ecosystem` | Product directory and portfolio README | `README.md` | Documentation-only | **Use as portfolio, roadmap, and cross-repo governance home** |

## Existing Architecture

```text
                    User or system intent
                              |
                              v
                    verdict-core decision plane
        contracts -> classification -> eligibility -> ranking
             |              |              |             |
             v              v              v             v
       context/memory   passports       availability   evidence
                              |
                              v
                    gateway adapter boundary
                         /      |       \
                        /       |        \
                 verdict-node  OmniRoute  custom provider
                        |
                        v
                OpenAI-compatible execution

   Specialized providers and workflows:
   verdict-risk | verdict-strategy/edge | verdict-backtest | Ruflo | RuVector

   Observability surface:
   verdict-cockpit (currently partially mocked)
```

Core's model catalog currently exposes a strong qualification direction, but the audit must distinguish catalog identity from operational proof. `verdict/omniroute.py` reads the OpenAI-compatible `/v1/models` catalog; catalog membership is declared evidence, not proof that a concrete model is usable for a specific task. ADR-007, ADR-011, and ADR-012 require consented, bounded probes, while ADR-019 requires fresh negotiated runtime evidence for runtime capabilities. The remaining product gap is a complete per-concrete-model qualification record covering availability, usage/quota/headroom, context, tool calling, structured output, streaming, vision where applicable, latency, errors, provider/account attribution, expiry, and evidence authority. `auto/*` aliases must remain aliases and cannot satisfy that proof requirement.

Core's existing ADR set already points toward the requested direction. Relevant decisions include:

- `docs/adr/ADR-001-evidence-ledger.md` — evidence-ledger direction.
- `docs/adr/ADR-002-orchestrator-routing.md` — orchestrator routing.
- `docs/adr/ADR-003-platform-neutral-guidance-boundary.md` — neutral guidance boundary.
- `docs/adr/ADR-004-local-first-memory-plane.md` — local-first memory.
- `docs/adr/ADR-006-authoritative-documentation-preflight.md` — documentation preflight.
- `docs/adr/ADR-009-durable-memory-write-gate.md` — governed memory writes.
- `docs/adr/ADR-010-fail-closed-capability-passports.md` — capability eligibility.
- `docs/adr/ADR-015-evidence-authority-and-portable-receipts.md` — portable evidence.
- `docs/adr/ADR-016-deterministic-policy-and-transition-graphs.md` — deterministic policy transitions.
- `docs/adr/ADR-019-runtime-negotiated-passports.md` — runtime capability negotiation.
- `docs/adr/ADR-020-gateway-adapter-contracts.md` — gateway adapter contracts.
- `docs/architecture/LIFECYCLE_HOOKS_SPECIFICATION.md` — platform-neutral lifecycle hook matrix.

## Implemented Capabilities

### `verdict-core`

Core contains the majority of the target platform primitives:

- Versioned Python and TypeScript contracts under `contracts/`, including `TaskSpec`, routing decisions, verification plans, and contract validation.
- JSON schemas for contracts, evaluation, context packs, runtime health, runtime passports, and gateway adapters under `schemas/`.
- Policy-adjacent routing components including classification, catalog discovery, eligibility, availability, adaptive ranking, escalation, and dispatch.
- Capability qualification and fail-closed passport concepts in `capability_passports.py` and the related ADRs.
- Evidence and receipt components in `evidence.py` and `evidence_receipts.py`.
- Gateway adapter interfaces and runtime/conformance helpers in `gateway_adapters.py`, `gateway_adapter_runtime.py`, and `gateway_conformance.py`.
- Lifecycle controller and a detailed lifecycle-hook specification covering task, prompt, tool/command, edit, session, verification, and error boundaries.
- Environment discovery, documentation preflight, code-graph integration, intelligence adapters, and memory-plane integration points.
- CLI, API/server, dashboard, benchmarking, examples, and a large test suite.

Core is therefore the natural home for the Decision Kernel, Execution Envelope, native runtime enforcement, verification, evidence, memory governance, and model-assignment authority.

### `verdict-node`

The Node package provides:

- Express/Next.js middleware entry points in `src/middleware/`.
- Boundary validation in `src/middleware/validator.ts`.
- Forwarding and SSE/response handling in `src/middleware/forwarder.ts`.
- Contract conversion in `src/adapters/contract-to-middleware.ts`.
- TypeScript package exports, declarations, build, tests, package verification, and dry-run packaging.
- A dependency on `@bodanglin/verdict-contracts`, which is the correct direction for canonical cross-language contracts.

Node is useful as an edge/runtime adapter, but it must not become a second policy authority. Any policy-adjacent classification or fallback logic should be explicitly marked as a compatibility shim, delegated to Core, or proven equivalent through versioned conformance fixtures.

### `verdict-risk`

Risk is a strong reusable deterministic provider for:

- Pure drawdown, concentration, expected-value, and loss-sequence gates.
- Stateful kill switches, timed circuit breakers, and consecutive-loss gates.
- Typed risk state and decisions in `state.py`.
- A `RiskAuthority` orchestration surface in `engine.py`.
- Optional OpenTelemetry spans and webhook emission.
- Paper execution adapter and benchmark tooling.

This is not an AI execution gateway. It is a specialized risk/policy evaluator that can implement a Verdict `RiskProvider` or verification plugin without importing network I/O into the hot path.

### `verdict-strategy` / published `verdict-edge`

The repository implements a small, composable domain evaluator:

- Expected-value gate and Kelly-style sizing in `gate.py`.
- Safe scalar and time-series feature evaluation in `evaluator.py`.
- No `eval()`-based expression execution and no exchange SDK requirement in the evaluator.
- Integration tests for backtest and live-pipeline boundaries.

The repository/package naming is inconsistent: the Git repository is `verdict-strategy`, while `pyproject.toml` and README identify `verdict-edge`. This is a release and ecosystem-alignment issue, not a reason to rewrite the evaluator.

### `verdict-backtest`

Backtest provides:

- Numba-accelerated Monte Carlo equity-path simulation.
- Fee-model protocol and concrete exchange fee models.
- Tearsheets, risk statistics, and walk-forward splitting.
- Deterministic configuration intent and a clear no-live-trading boundary documented in `docs/ARCHITECTURE.md`.

It is reusable as a simulation, counterfactual evaluation, and verification provider. It should not be coupled directly into the core request path.

### `verdict-cockpit`

The cockpit has a working Next.js/React structure and tests for dashboard/store/order-book behavior. Its current source is primarily a UI prototype:

- `src/components/VirtualizedOrderBook.tsx` renders virtualized order-book data.
- `src/lib/tradingStore.ts` owns state and embeds large mock bid/ask arrays.
- `src/hooks/useOrderBook.ts` and the dashboard tests provide reusable UI/test patterns.

The cockpit does not yet have a versioned control-plane API client, evidence views, policy decision explorer, authentication/authorization boundary, or live contract-backed data model. Retain the UI shell and replace mock data behind typed API adapters.

### `verdict-ecosystem`

The umbrella repository currently provides product-directory documentation and links. It is the right place for cross-repository release alignment, public roadmap, compatibility matrix, and issue-generation references, but it is not an execution component.

## Reusable Components and Relationships

1. **Core contracts are the canonical boundary.** The `contracts/` package and `schemas/` should be treated as the source of truth for Python/TypeScript interoperability.
2. **Core gateway adapters are the extension seam.** `gateway_adapters.py`, runtime helpers, and conformance tests should be extended for Ruflo, OmniRoute, direct APIs, and custom runtimes.
3. **Risk and backtest are provider libraries.** Their deterministic APIs fit evaluation, risk, counterfactual, and verification roles.
4. **Node is the edge transport.** It should consume contracts and invoke Core decisions, not reproduce the full policy engine.
5. **Cockpit is an observability/control UI.** Its state and components can be retained while data and authorization move to typed control-plane endpoints.
6. **Existing ADRs are a design asset.** The target architecture can be delivered by closing gaps in the existing decisions rather than discarding them.

## Duplication and Technical Debt

- Policy-adjacent classification and fallback behavior appears in both Core and Node. Without conformance tests, behavior can drift.
- Contract artifacts exist in multiple generated/source locations (`contracts/src`, generated TypeScript output, Python contracts, and JSON schemas). The generation/versioning process is not yet an explicit release gate.
- Repository and package names do not consistently match (`verdict-strategy` versus `verdict-edge`; several README links reference old or alternate names).
- Core contains generated/runtime directories and extensive agent/tooling artifacts alongside product code; this increases discovery noise and packaging risk.
- Core has multiple architecture/audit locations (`docs/`, `Docs/`, and archived material), which can make authority and freshness ambiguous.
- Node's local policy instructions reference Core behavior but there is no automated cross-repository ADR or contract synchronization gate.
- Cockpit stores mock market data inside a global store and has no stable external data contract.
- Specialized Python packages have separate manifests, versions, and CI policies; cross-repository compatibility is largely convention-based.
- Existing issues already cover some memory replacement and lifecycle work in Core (`#210`–`#217`), Node packaging/forwarding (`#8`, `#9`), and ecosystem manifest work (`#1`). New issue generation must link to or supersede these rather than duplicate them.

## Coupling and Risk Areas

### Authority coupling

If Node, Ruflo, or an external model router can independently approve an execution, Verdict's authority invariant is broken. Core must produce the decision and envelope; adapters may execute only within that envelope.

### Contract coupling

Core and Node currently rely on related but separately released artifacts. Schema version, unknown-field handling, secret rejection, and error-category compatibility need automated fixtures and compatibility tests.

### Provider coupling

The README architecture names Ruflo, RuVector, and OmniRoute, but an adapter capability/health contract is required before they can be treated as reliable providers. Provider unavailability must produce explicit `unknown`, `degraded`, or `denied` outcomes, not silent fallback.

### Memory coupling

Core has local-first and governed-memory ADRs, while other repositories inherit operational instructions and may use shared bridges. Namespaces, retention, privacy, authority, and write verification must be versioned; memory retrieval can inform ranking but never bypass eligibility.

### UI coupling

Cockpit currently couples market/order-book state to components and mock data. A typed API/event boundary is needed before it can represent decisions, envelopes, evidence, verification, or policy changes safely.

### Release coupling

Seven repositories have independent versions and workflows. A compatibility manifest, release matrix, and cross-repo contract smoke test are required for public launch readiness.

## Blockers to the Target End State

1. No single, explicitly published universal `ExecutionEnvelope` spanning task, decision, policy, capabilities, budget, timeout, tools, agents, verification, evidence, and expiration.
2. No complete framework-neutral execution gateway enforcing the envelope at every required native boundary (`pre-tool`, `pre-command`, `pre-edit`, runtime, verification, memory write) across all adapters.
3. Adapter protocols are present in Core but Ruflo, RuVector, OmniRoute, and standalone defaults are not yet all implemented and conformance-tested as first-class providers.
4. Verification and evidence primitives exist, but the end-to-end chain from decision to runtime receipt to verification result to durable evidence is not yet demonstrated across each integration.
5. Learning/ranking exists, but governance, provenance, rollback, and proof that learning cannot bypass policy need a single public contract.
6. The autonomous development workflow is described by specifications and repository instructions but is not yet a versioned plugin with portable `EnvironmentInventory`, `RepositoryUnderstanding`, `ImplementationResearch`, `AtomicWorkSlice`, and `SwarmSpec` contracts.
7. Shared context support is fragmented across Core, memory bridges, code graph, OpenViking, and RuVector conventions.
8. Cross-language and cross-repository CI does not yet provide a complete compatibility/release gate.
9. Existing local untracked artifacts in some repositories must be preserved and classified before any cleanup or migration.

## Existing GitHub Work to Reuse

At audit time, open issues included:

- `verdict-core`: #210–#217 covering hybrid memory, Ruflo/RuVector memory replacement, statusline, compaction/autopilot, retirement/rollback, ADRs, and governed graph learning.
- `verdict-node`: #1 (router middleware epic), #8 (forwarding/SSE parity), and #9 (package boundary/publication evidence).
- `verdict-risk`: #1 (risk engine epic).
- `verdict-ecosystem`: #1 (ecosystem compatibility and release manifest).

New stories should use `relates to`, `depends on`, or `supersedes` references instead of creating parallel duplicate epics.

## Audit Conclusion

Verdict Core already has the architectural seed and several implemented primitives for the requested end state. The highest-leverage work is contract consolidation, runtime enforcement, adapter conformance, evidence/verification closure, and cross-repository release alignment. The specialized risk, strategy, and backtest libraries should remain composable providers. The cockpit and Node package should become governed surfaces over Core, not independent authorities.
