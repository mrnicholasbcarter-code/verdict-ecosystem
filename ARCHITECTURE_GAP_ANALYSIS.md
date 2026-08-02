# Verdict Target Architecture Gap Analysis

- **Date:** 2026-08-02
- **Target:** Verdict Core as an ecosystem-neutral AI execution control plane and enforcement layer
- **Baseline:** `CURRENT_STATE_AUDIT.md`
- **Scope note:** Memory-unification implementation is being handled separately. Memory governance, shared-context, and RuVector/OpenViking write-path work remain documented as dependencies but are deferred from the immediate issue batch to avoid duplicate ownership.

## Target Invariant

```text
Eligibility -> Ranking -> Execution Authorization -> Runtime Enforcement
           -> Verification -> Evidence -> Governed Learning
```

Learning may improve ranking. It must never create eligibility, authorize execution, weaken a policy, or bypass verification.

## Target Layers and Current Gaps

| Target layer | Existing pieces | Gap | Recommended treatment | Complexity |
| --- | --- | --- | --- | --- |
| Intent and `TaskSpec` | Core contracts and routing decisions; Node contract dependency | Task understanding is not yet a complete cross-runtime intake contract with normalized risk/capability requirements | Extend versioned Core contracts; add canonical fixtures and error semantics | M |
| Decision Kernel | Core classification, catalog, eligibility, availability, ranking, escalation, passports | Decision output is distributed across contracts/modules; no single public decision-kernel API with explicit invariant | Compose existing modules behind a deterministic `DecisionKernel` facade; retain fail-closed semantics | L |
| Universal `ExecutionEnvelope` | Gateway adapter schemas, runtime passport, task/routing/verification contracts | No single envelope covering decision ID, policy version, models, tools, agents, budgets, timeout, risk, verification, evidence, expiry | Add versioned envelope schema and Python/TypeScript parsers; require it at every gateway | L |
| Agent Runtime adapter | Gateway adapter interfaces and lifecycle specifications | Ruflo/default/custom runtime adapters are not all implemented and conformance-tested | Implement adapter protocol plus Ruflo adapter first; keep custom runtime adapter minimal | L |
| Intelligence Provider adapter | Intelligence adapter and memory/code-graph integration points | RuVector/OpenViking/local provider capabilities and write authority are not uniform | Define search/retrieve/ingest/pattern/outcome protocol and provider health semantics | L |
| Execution Provider adapter | OmniRoute catalog qualification and gateway references | OmniRoute, direct API, local inference, and standalone defaults lack one provider contract | Define execute/health/capabilities/usage/discovery protocol; implement OmniRoute and deterministic local default | M/L |
| Native enforcement kernel | `lifecycle_controller.py` and lifecycle-hook specification | Required native guards and fail-closed behavior are not proven across all runtime/tool boundaries | Build gateway and hook middleware around immutable envelope; add command/edit/tool/memory guards | XL |
| Workflow/plugin system | Environment discovery, documentation preflight, guidance, examples, specs | Autonomous Dev is not a versioned plugin with portable stage contracts | Add workflow protocol and ship Autonomous Dev as first-party plugin | L |
| Governed swarm system | Hivemind/orchestrator references and Ruflo integration direction | No public `SwarmSpec`, supervisor protocol, conflict resolution, or evidence model spanning agents | Add swarm contracts and Ruflo adapter; require per-slice envelopes and supervisor verification | XL |
| Shared Context Plane | Context packs, local-first memory ADRs, code graph, OpenViking/RuVector bridges | Provider-specific memory conventions and namespaces are not unified | Define context-provider protocol, namespaces, retention, authority, and verified writes | L |
| Verification | Evaluation, verification plans, test/quality tooling, shadow/counterfactual ADRs | No demonstrated universal gate that consumes requirements, architecture, security, performance, and regression evidence | Add verification orchestrator and typed `VerificationResult`; integrate Core and providers | XL |
| Evidence | Evidence ledger/receipt modules and ADRs | Chain is not yet guaranteed from request through adapter, runtime, verification, and learning | Add append-only `EvidenceChain` and portable receipt projection with privacy controls | L |
| Model assignment | Adaptive ranker, intelligence service, catalog, capability qualification | Ranking and assignment are not exposed as a policy-bounded slice-assignment engine; catalog metadata and `auto/*` aliases cannot stand in for per-model proof | Add `ModelAssignmentEngine` after eligibility; record rationale and model/provider attribution; actively probe each concrete model for availability, usage/quota, context, tools, structured output, streaming, vision, and failure behavior under consented budgets | L | High | Decision Kernel, capability data |  
| Guidance and workflow selection | Guidance specifications, lifecycle hooks, environment discovery, external Ruflo guidance patterns | No provider-neutral guidance plugin contract that recommends tools/workflows without becoming execution authority | Add advisory `GuidanceProvider`/workflow selector plugin; require TaskSpec, policy, capability, freshness, and evidence inputs; guidance may recommend but never authorize | L | High | Decision Kernel, plugin runtime, verification |
| Memory governance | Durable memory write gate, privacy-safe receipts, local-first plane | Governance is distributed and learning/memory adapters need one write API | Add `MemoryGovernance` with schema, redaction, verification, provenance, rollback | L |
| Developer experience | CLI/API/dashboard, Node middleware, docs, examples | No single install, local-provider, adapter, workflow, or evidence path is documented and smoke-tested | Add `verdict init`, provider manifests, examples, and integration test harness | M |
| Repository alignment | Ecosystem README and independent CI | Package/repository names, versions, contracts, release checks, and issue ownership are inconsistent | Publish compatibility manifest and cross-repo release workflow | M |

## Adapter Contracts

Verdict should own these interfaces and semantics:

### Agent Runtime

```text
submit(envelope) -> run_id
status(run_id) -> RunStatus
pause(run_id)
resume(run_id)
cancel(run_id)
collect_results(run_id) -> RuntimeResult
```

The adapter may schedule agents, but it may not alter the envelope's policy, allowed tools, model set, budget, expiry, or verification requirements.

### Intelligence Provider

```text
search(query, scope) -> SearchResults
retrieve(reference) -> ContextRecord
ingest(record, authority) -> IngestReceipt
store_pattern(pattern, provenance) -> PatternReceipt
record_outcome(outcome, evidence_ref) -> OutcomeReceipt
health() -> ProviderHealth
```

Retrieval and patterns are advisory. Writes require Core governance and evidence.

### Execution Provider

```text
execute(envelope, request) -> ExecutionResult
health() -> ProviderHealth
capabilities() -> CapabilitySet
usage(run_id) -> UsageRecord
discover_models() -> ModelCatalog
```

The provider is not allowed to substitute an unapproved model or tool. Unknown capability or stale health must be represented explicitly.

## Key Architecture Decisions

### 1. Core remains the authority

`verdict-core` owns contracts, policies, eligibility, execution envelopes, enforcement, evidence, verification, and learning governance. Node, Ruflo, RuVector, OpenViking, OmniRoute, and domain libraries are adapters/providers.

### 2. Contracts before implementations

Extend the existing `contracts/` package and JSON schemas rather than introducing independent contract definitions in every repository. Generate or publish Python and TypeScript artifacts from the same versioned source. Add fixture-based parity tests before changing policy behavior.

### 3. Do not create a second policy authority in Node

Node may retain a compatibility classifier only while it is explicitly marked and proven equivalent. The preferred path is Core decision delegation over a stable API or shared decision artifact. A new `@verdict/policy` package should not become an ungoverned second authority; if created, it must be a generated/conformance surface owned by Core.

### 4. Provider failure is a decision state

Provider outages, stale catalogs, failed qualification, and missing capabilities must yield `unknown`, `degraded`, `approval_required`, or `deny` according to policy. They must not silently trigger an unsafe fallback.

### 5. Workflows are plugins

The autonomous development lifecycle is a workflow/plugin. Core supplies task, slice, context, envelope, hook, evidence, and verification primitives. Ruflo is the default swarm/runtime implementation, not a required architectural dependency.

### 6. Domain packages stay domain packages

Risk, strategy/edge, and backtest should expose provider protocols and receipts. They should not import AI orchestration concerns into deterministic hot paths or become part of the core gateway dependency graph.

## Gap by Required Epic

| # | Epic | Gap closure | Primary repositories | Dependency |
| ---: | --- | --- | --- | --- |
| 1 | Decision Kernel | Public deterministic facade for intent normalization, policy, eligibility, ranking, and decision receipts | Core, contracts | None beyond current contracts |
| 2 | Execution Envelope | Universal immutable, versioned execution authorization | Core/contracts, Node | Decision Kernel |
| 3 | Adapter Architecture | Runtime, intelligence, and execution provider protocols plus conformance suite | Core/contracts | Envelope |
| 4 | Standalone Default Providers | Local deterministic runtime/intelligence/execution implementations for usable offline install | Core | Adapter protocols |
| 5 | Ruflo Integration | Ruflo agent runtime and swarm adapter with bounded envelopes | Core, Ruflo, ecosystem | Runtime adapter, SwarmSpec |
| 6 | RuVector Integration | RuVector retrieval/pattern/outcome adapter with governed writes | Core, RuVector | Intelligence adapter, memory governance |
| 7 | OmniRoute Integration | OmniRoute catalog/execute/health provider with qualification and attribution | Core, OmniRoute, Node | Execution provider |
| 8 | Runtime Enforcement Kernel | Native lifecycle hooks, tool/command/edit guards, loop controls, gateway | Core, Node, provider adapters | Envelope, adapter architecture |
| 9 | Verification System | Requirements, test, architecture, security, regression, and performance verification orchestrator | Core, all provider repos | Evidence and envelope |
| 10 | Evidence System | End-to-end append-only evidence chain and portable receipts | Core, all adapters | Verification |
| 11 | Memory Governance | Redaction, authority, retention, verified writes, rollback, learning boundary | Core, memory providers | Evidence |
| 12 | Autonomous Development Workflow | Plugin with inventory, repository understanding, research, architecture, slices, implementation, verification | Core, ecosystem, Node/Ruflo adapters | Kernel, context, verification |
| 13 | Governed Swarm System | `SwarmSpec`, supervisor, role/model assignment, shared context, conflict handling | Core, Ruflo, ecosystem | Workflow and envelope |
| 14 | Shared Context Plane | Provider-neutral context API for ADRs, RAG, graph, research, history, evidence | Core, RuVector/OpenViking/code graph | Memory governance |
| 15 | Model Assignment Engine | Policy-bounded role/slice assignment considering reasoning, tools, context, risk, availability, cost | Core, OmniRoute, Node | Decision Kernel |
| 16 | Repository Alignment | Names, versions, package metadata, schemas, CI, compatibility manifest | Ecosystem and all repos | Contract release |
| 17 | Developer Experience | CLI, install, examples, local defaults, explainability, integration harness | Core, Node, cockpit, ecosystem | Default providers |
| 18 | Public Launch Readiness | Security, privacy, performance, reliability, docs, release, support, demo gates | All repos | All preceding epics |

## Non-Goals and Replace Boundaries

- Do not rewrite deterministic risk mathematics, feature evaluation, Monte Carlo simulation, or working Core routing primitives.
- Do not embed Ruflo-specific APIs into Core domain objects.
- Do not make the cockpit a policy authority.
- Do not treat model ranking, memory similarity, or learned patterns as eligibility.
- Do not claim production readiness from package builds alone; require integration evidence and provider failure tests.

## Acceptance-Level Definition of Target Architecture

The target architecture is reached only when a request can be demonstrated end to end:

1. Core accepts intent and produces a validated `TaskSpec`.
2. Core gathers context and produces a deterministic decision with policy/version evidence.
3. Core emits an immutable `ExecutionEnvelope` with allowed models, tools, agents, budget, timeout, risk, verification, evidence, and expiry.
4. An adapter executes only within that envelope.
5. Native guards reject out-of-envelope tool, command, edit, loop, and memory writes.
6. Verification produces a typed `VerificationResult` with required checks and receipts.
7. Core appends an `EvidenceChain` that identifies decision, policy, runtime, model, tools, changes, verification, and outcome.
8. Learning receives only verified, privacy-safe outcomes and can improve ranking without changing eligibility.
