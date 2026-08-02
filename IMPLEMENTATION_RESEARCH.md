# Verdict Implementation Research and Architecture Decisions

- **Date:** 2026-08-02
- **Purpose:** Record the reuse-first research conclusions that precede ticket generation.

## Product Boundary

Verdict Core is the authority layer between intent and execution. It owns contracts, policy, eligibility, execution envelopes, enforcement, verification, evidence, and governed learning. External systems provide capabilities through adapters.

This boundary is supported by Core's existing platform-neutral guidance ADR, gateway adapter ADR, evidence ADRs, capability passport ADRs, and lifecycle-hook specification.

## Options Considered

### Make Ruflo the core architecture

**Rejected.** This would couple Verdict's public contracts and enforcement semantics to one runtime. Ruflo remains the default runtime/swarm implementation, but a custom runtime must be able to implement the same adapter contract.

### Make OmniRoute the policy/router authority

**Rejected.** OmniRoute can provide model discovery, execution, health, usage, and provider selection. Eligibility, policy, risk, and verification remain Verdict decisions.

### Make RuVector/OpenViking the memory authority

**Rejected.** They can provide retrieval, graph, indexing, and pattern capabilities. Verdict owns memory-write governance, privacy, provenance, retention, and the rule that learning cannot bypass policy.

### Create a second Node policy package

**Rejected as the first move.** Node currently needs compatibility behavior, but a second policy authority would increase drift. First publish canonical schemas and conformance fixtures; then either delegate decisions to Core or generate a strictly equivalent language binding owned by Core.

### Rewrite the domain repositories into Core

**Rejected.** Risk, strategy, and backtest are focused deterministic libraries. Adapting them as providers preserves useful isolation, performance, and testability.

### Build a new orchestration framework

**Rejected.** Core already has routing, lifecycle, gateway, context, evidence, memory, and verification building blocks. Build only missing control-plane primitives and workflow/plugin contracts.

## Chosen Direction

1. **Core-first authority:** extend `verdict-core` rather than introduce a new central repository.
2. **Contract-first integration:** version Python/TypeScript/JSON artifacts together.
3. **Fail-closed qualification:** unknown, stale, missing, or unqualified capabilities cannot authorize execution.
4. **Immutable execution envelope:** every adapter receives a bounded envelope with policy, identity, capabilities, budget, timeout, allowed actions, verification, evidence, and expiry.
5. **Native enforcement:** hooks and guards execute at task, tool, command, edit, runtime, verification, and memory-write boundaries.
6. **Plugin workflows:** Autonomous Dev is the flagship workflow, not hardcoded into the kernel.
7. **Provider-neutral context:** RAG, ADRs, code graph, history, and evidence are context sources with provenance, not policy authorities.
8. **Evidence before learning:** only verified, redacted outcomes may update ranking or patterns.

## Additional Direction: Concrete-Model Qualification and Guidance

Catalog membership and `auto/*` aliases are insufficient evidence for model selection. The execution-provider contract must distinguish aliases from concrete model IDs and require active, consented, budgeted qualification for each concrete model intended for protected work. Qualification should record sanitized, expiring evidence for availability, usage/quota/headroom, context limits, tool calling, structured output, streaming, vision or other declared capabilities, latency, error/fallback behavior, and provider/account attribution. A catalog entry may remain visible as `declared`, but it cannot become `eligible` for protected execution without fresh direct evidence. Existing probe ADRs support this direction: `ADR-007`, `ADR-011`, `ADR-012`, `ADR-013`, `ADR-014`, and `ADR-019`.

Guidance should be integrated as a provider-neutral advisory plugin/workflow, not copied as a second authority. A guidance provider can inspect TaskSpec, repository/context evidence, available capabilities, policy constraints, and freshness, then recommend a workflow, tools, roles, or model-assignment strategy. Core must re-evaluate every recommendation through eligibility, envelope creation, runtime enforcement, verification, and evidence. Ruflo Guidance can be the first adapter/reference implementation; the contract must remain usable by other runtimes.

## Research Gaps Requiring First-Class Tickets

- Exact public API and serialization of `ExecutionEnvelope`.
- Compatibility/version policy between Core contracts and `@bodanglin/verdict-contracts`.
- Ruflo runtime event/status mapping and cancellation semantics.
- RuVector/OpenViking provider health, namespace, retention, and write receipts.
- OmniRoute model discovery/usage attribution and failure states.
- Native guard behavior for each supported host/runtime.
- Verification policy profiles for code, infrastructure, financial, and other high-risk tasks.
- Evidence-chain storage/portability and privacy redaction guarantees.
- Cross-repository release and migration policy for `verdict-strategy`/`verdict-edge` naming.

## Research Conclusion

The shortest credible path is not a rewrite. It is a bounded Core authority milestone with local defaults, a complete envelope/enforcement/evidence path, and one provider of each type. Ruflo, RuVector, and OmniRoute should then be added through conformance-tested adapters. The domain repositories and cockpit follow after the authority path is independently verifiable.
