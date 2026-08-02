# Verdict Autonomous AI Control-Plane Roadmap

- **Date:** 2026-08-02
- **Status:** Proposed execution roadmap derived from the current-state audit and lift analysis
- **Scope note:** Memory-unification work is intentionally deferred from this execution batch because another effort owns it. Do not create duplicate memory tickets; resume with integration and verification after that work lands.

## Phase 0 — Baseline and Contract Freeze

**Goal:** Establish the source of truth before implementation.

- Accept and publish the current-state, gap, lift, and research documents.
- Inventory existing GitHub issues and link duplicates/superseded work.
- Freeze contract versioning and generate Python/TypeScript/JSON compatibility fixtures.
- Resolve package/repository naming and release metadata inconsistencies.
- Publish a compatibility manifest from `verdict-ecosystem`.

**Gate:** No new execution feature proceeds without an owning contract, policy, evidence, and verification story.

## Phase 1 — Decision Kernel and Execution Envelope

**Goal:** Make the authority path explicit and testable.

- Compose Core's existing classifier, eligibility, availability, capability passport, ranking, and escalation into a public `DecisionKernel`.
- Add `ExecutionEnvelope` and parsers in Core/contracts.
- Add policy version, decision ID, expiry, allowed models/tools/agents, budget, timeout, risk constraints, verification requirements, and evidence references.
- Add explainability and denial reasons.

**Gate:** A deterministic request produces a validated decision and immutable envelope without any provider execution.

## Phase 2 — Adapter Architecture and Default Providers

**Goal:** Make Verdict usable without a mandatory external runtime.

- Formalize Agent Runtime, Intelligence Provider, and Execution Provider interfaces.
- Build deterministic local runtime/intelligence/execution defaults.
- Add provider health, capabilities, usage, discovery, and explicit unknown/degraded states.
- Implement conformance tests and a fake provider test harness.
- Add a concrete-model qualification scheduler: enumerate real model IDs, exclude alias-only entries from qualification, run consented/budgeted probes per model, and persist expiring sanitized receipts for capability, usage/quota, headroom, latency, and failure behavior.

**Gate:** Every model eligible for protected work has fresh direct evidence; `auto/*` aliases alone never qualify a route.

**Guidance boundary:** Add an advisory provider-neutral guidance plugin/workflow contract. Ruflo Guidance may be the first adapter, but guidance recommendations must flow back through Core eligibility and envelope enforcement.


**Gate:** Offline end-to-end demo runs through the same envelope path as external providers.

## Phase 3 — Native Runtime Enforcement

**Goal:** Ensure the envelope is enforced, not advisory.

- Extend Core lifecycle controller and hook specification into native guards.
- Enforce pre-tool, pre-command, pre-edit, loop, runtime, verification, and memory-write boundaries.
- Add command/edit root and credential protections.
- Add pause/resume/cancel/timeout/approval behavior.
- Emit receipts for allowed, approval-required, denied, degraded, and failed transitions.

**Gate:** Adversarial tests demonstrate that an adapter cannot exceed the envelope.

## Phase 4 — Verification and Evidence Closure

**Goal:** Replace agent claims with independent evidence.

- Implement typed `VerificationResult` and verification profiles.
- Run requirements, tests, architecture, regression, security, privacy, and performance checks according to policy.
- Implement append-only `EvidenceChain` and portable receipt projection.
- Link decision, policy, runtime, model, tools, changes, verification, and outcome.

**Gate:** Completion is impossible without configured verification evidence; evidence is privacy-safe and portable.

## Phase 5 — First-Class Integrations

**Goal:** Add opinionated defaults without changing the architecture.

- Ruflo runtime and governed swarm adapter.
- RuVector/OpenViking/context provider adapters.
- OmniRoute execution/catalog/health adapter.
- Node middleware delegation and envelope enforcement.
- Cross-provider failure, qualification, attribution, and cancellation tests.

**Gate:** Each provider passes the same conformance suite and produces evidence-bearing runs.

## Phase 6 — Autonomous Dev and Governed Swarms

**Goal:** Ship the flagship workflow as a plugin.

- `EnvironmentInventory` stage.
- `RepositoryUnderstanding` stage using source, ADRs, memory, RAG, code graph, and provider capabilities.
- Memory-first tool selection and documentation preflight.
- `IMPLEMENTATION_RESEARCH` and architecture decision stage.
- Atomic work-slice compiler.
- Model assignment engine.
- `SwarmSpec`, supervisor, shared context, conflict handling, and per-slice verification.

**Gate:** A repository task completes the full lifecycle with bounded delegation and a complete evidence chain.

## Phase 7 — Product Surfaces and Launch

**Goal:** Make the control plane adoptable and supportable.

- Replace cockpit mock data with typed control-plane APIs/events.
- Add policy decision explorer, envelope viewer, evidence-chain viewer, verification status, provider health, and audit views.
- Publish install, local development, provider setup, adapter authoring, and migration guides.
- Run security/privacy/performance/reliability launch gates.
- Publish compatible package versions and release notes.

**Gate:** Public launch checklist is satisfied by reproducible CI and demo evidence.

## Critical-Path Ordering

```text
Contract freeze
  -> Decision Kernel
  -> Execution Envelope
  -> Adapter conformance + defaults
  -> Native enforcement
  -> Verification + Evidence
  -> Ruflo/RuVector/OmniRoute integrations
  -> Autonomous Dev + governed swarms
  -> Cockpit and public launch
```

Risk, strategy/edge, and backtest integration can proceed in parallel after provider contracts are stable, but they must not block the core authority path.

## Operating Rules

- Use Ruflo as the default swarm/runtime implementation where available, but keep all contracts and enforcement in Verdict.
- If a provider or swarm is unavailable, continue only with explicitly bounded local defaults or mark the work blocked; never silently weaken policy.
- Every implementation story must include acceptance criteria, security considerations, tests, evidence, dependencies, and definition of done.
- Preserve uncommitted user work in every repository; no cleanup or reset without explicit approval.
