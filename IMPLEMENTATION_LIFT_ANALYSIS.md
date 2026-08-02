# Verdict Implementation Lift Analysis

- **Date:** 2026-08-02
- **Estimate scale:** XS < 1 engineer-week; S 1–2; M 3–5; L 6–10; XL 11+ engineer-weeks
- **Order rule:** Reuse → Extend → Integrate → Replace → Build New
- **Important:** estimates include implementation, tests, contract fixtures, and integration verification, not just code volume
- **Scope note:** Memory-unification implementation is owned by another active effort. Memory governance, shared-context, and RuVector/OpenViking write-path items are deferred from the immediate issue batch; retain them as dependencies and integration checks only.

## Capability Lift Matrix

| Capability | Current reuse | Affected repositories | Approach | Effort | Risk | Dependencies |
| --- | --- | --- | --- | ---: | --- | --- |
| Task understanding and normalization | Core contracts, classifier, context pack | Core, contracts, Node | Extend contracts and deterministic intake facade | M | Medium | Contract versioning |
| Decision Kernel | Core eligibility, availability, passports, ranker, escalation | Core, contracts, Node | Compose existing modules behind one public API | L | High | TaskSpec, policy transition rules |
| Universal Execution Envelope | Gateway/runtime schemas and verification plans | Core, contracts, Node, adapters | Build one immutable versioned envelope and parsers | L | High | Decision Kernel |
| Agent Runtime adapter | Core gateway adapter seam; Ruflo available externally | Core, Ruflo, Node | Integrate Ruflo first; add minimal local runtime | L | High | Envelope, lifecycle events |
| Intelligence Provider adapter | Core intelligence/memory/code graph hooks | Core, RuVector, OpenViking | Extend into provider-neutral protocol with health and write receipts | L | High | Memory governance, evidence |
| Execution Provider adapter | OmniRoute qualification/catalog surfaces | Core, OmniRoute, Node | Integrate OmniRoute; add local/direct HTTP provider | M/L | High | Envelope, capability passport |
| Native runtime enforcement | Lifecycle controller and lifecycle-hook specification | Core, Node, Ruflo adapters | Extend to tool, command, edit, loop, and memory gates | XL | Critical | Envelope, adapter integration |
| Verification orchestrator | Evaluation, tests, quality tooling, shadow/counterfactual ADRs | Core, all repos | Build typed verification pipeline and provider hooks | XL | Critical | Evidence, runtime receipts |
| Evidence chain | Evidence ledger, receipts, privacy-safe receipt ADRs | Core, all adapters | Extend append-only chain and portable receipt format | L | High | Envelope, verification |
| Memory governance | Durable write gate and local-first memory ADRs | Core, RuVector/OpenViking, all repos | Centralize redaction, authority, retention, rollback, learning boundary | L | Critical | Evidence, provider protocol |
| Model assignment | Adaptive ranker, catalog, intelligence service | Core, OmniRoute, Node, Ruflo | Build policy-bounded slice assignment after eligibility; replace alias-only confidence with consented, budgeted concrete-model qualification and per-model capability/usage receipts | L | Critical | Decision Kernel, capability data, probe scheduler |  
| Guidance/workflow selection | Guidance specs, lifecycle hooks, environment discovery, external Ruflo guidance patterns | Core, ecosystem, Ruflo/other adapters | Add advisory provider-neutral guidance plugin and workflow selector; recommendations cannot authorize execution or bypass eligibility | L | High | Decision Kernel, plugin runtime, verification |
| Workflow/plugin runtime | Environment discovery, documentation preflight, guidance specs | Core, ecosystem | Build plugin contract and lifecycle runner | L | High | Envelope, context, verification |
| Autonomous Dev workflow | Existing specs and development conventions | Core, ecosystem, Ruflo, Node | Implement flagship plugin in atomic stages | XL | Critical | Plugin runtime, swarm system |
| Governed swarms | Orchestrator/hivemind direction and Ruflo swarm | Core, Ruflo, ecosystem | Define SwarmSpec, supervisor, conflict/evidence rules | XL | Critical | Workflow, envelope, context |
| Shared Context Plane | Context packs, graph bridge, memory plane, OpenViking/RuVector hooks | Core, RuVector, OpenViking, ecosystem | Provider-neutral context API and namespace/version rules | L | High | Memory governance |
| Default standalone providers | Core local capabilities and HTTP primitives | Core | Build deterministic local runtime/intelligence/execution defaults | M/L | Medium | Adapter protocols |
| Node alignment | Existing middleware and canonical contracts dependency | Node, Core/contracts | Delegate/consume Core decisions; add parity and failure tests | L | High | Envelope, adapter API |
| Cockpit control-plane UI | Existing Next.js shell, tests, Zustand components | Cockpit, Node, Core | Replace mock data with typed API/events and evidence views | L | Medium/High | Public API, auth, envelope |
| Risk provider integration | `RiskAuthority`, gates, state, telemetry | Risk, Core | Add provider adapter and signed/portable risk receipt | M | High | Provider contracts, evidence |
| Strategy/edge integration | Feature evaluator and EV gate | Strategy, Core, backtest | Expose evaluation provider and verification result | M | Medium | Domain provider contract |
| Backtest integration | Monte Carlo, fees, tearsheets, walk-forward | Backtest, Core, strategy, risk | Expose simulation/counterfactual provider | M | Medium | Evidence and verification |
| Repository/release alignment | Ecosystem README and independent CI | All repos, ecosystem | Compatibility manifest, release train, contract smoke tests | M | High | Versioned contracts |
| Developer experience | CLI/API/dashboard/examples and package verification | Core, Node, Cockpit, ecosystem | Add init, explain, local defaults, integration harness | M/L | Medium | Default providers |
| Public launch readiness | Separate CI/security/release workflows | All repos | Cross-repo gates, security/privacy/perf/reliability evidence | L | Critical | All epics |

## Epic-by-Epic Lift

| Epic | Priority | Recommended implementation | Repositories | Effort | Definition of meaningful progress |
| --- | --- | --- | --- | ---: | --- |
| 1. Decision Kernel | P0 | Extend Core; do not rewrite routing modules | Core, contracts | L | One deterministic API returns decision, exclusions, rationale, policy version, and receipt |
| 2. Execution Envelope | P0 | Build from existing schemas and gateway contracts | Core, contracts, Node | L | Every execution request validates one immutable envelope with expiry and limits |
| 3. Adapter Architecture | P0 | Formalize three provider protocols and conformance harness | Core, contracts | L | A fake provider can be tested without provider-specific imports |
| 4. Standalone Default Providers | P1 | Build offline deterministic defaults | Core | M/L | Fresh install runs a complete governed demo without Ruflo/RuVector/OmniRoute |
| 5. Ruflo Integration | P1 | Implement runtime and swarm adapters behind contracts | Core, Ruflo, ecosystem | L | Ruflo run receives envelope and emits status/results/evidence |
| 6. RuVector Integration | P1 | Implement governed intelligence/memory adapter | Core, RuVector, ecosystem | L | Search can inform ranking; writes require verification and receipt |
| 7. OmniRoute Integration | P1 | Implement execution/catalog/health adapter | Core, OmniRoute, Node | M/L | Model discovery and execution are qualified, attributed, and fail closed |
| 8. Runtime Enforcement Kernel | P0 | Extend lifecycle controller into native gateway/guards | Core, Node, adapters | XL | Out-of-envelope tool/command/edit/memory actions are denied and evidenced |
| 9. Verification System | P0 | Build typed verification orchestrator | Core, all repos | XL | Completion requires requirements, tests, security, regression, and performance evidence as configured |
| 10. Evidence System | P0 | Close the append-only chain | Core, all repos | L | One portable chain joins decision, runtime, changes, verification, and outcome |
| 11. Memory Governance | P0 | Centralize governed memory writes and learned outcomes | Core, providers | L | Unverified or secret-bearing writes are rejected; rollback is possible |
| 12. Autonomous Development Workflow | P1 | Implement plugin stages and slice contracts | Core, ecosystem, Ruflo, Node | XL | A repository task runs discovery→research→architecture→slice→implementation→verification |
| 13. Governed Swarm System | P1 | Add SwarmSpec and supervisor | Core, Ruflo, ecosystem | XL | Supervisor delegates bounded slices and resolves conflicts with evidence |
| 14. Shared Context Plane | P1 | Normalize provider-neutral context records and namespaces | Core, providers, ecosystem | L | Agents receive same scoped ADR/RAG/graph/history context with provenance |
| 15. Model Assignment Engine | P1 | Add policy-bounded role/slice assignment | Core, OmniRoute, Ruflo | L | Assignment records reasoning tier, tool/context/risk needs, availability, and provider |
| 16. Repository Alignment | P0 | Fix package names, versions, CI, and compatibility manifest | All repos, ecosystem | M | A release matrix catches incompatible contract/package combinations |
| 17. Developer Experience | P1 | Add CLI setup, explainability, local demo, and integration harness | Core, Node, Cockpit, ecosystem | M/L | New developer can install and inspect a governed execution locally |
| 18. Public Launch Readiness | P0 | Run cross-repo security, privacy, perf, docs, and release gates | All repos | L | Launch checklist is backed by reproducible evidence, not README claims |

## Highest-Risk Work

1. **Runtime enforcement kernel:** a bypass here invalidates the product claim. It requires adversarial tests and adapter-specific integration tests.
2. **Verification/evidence closure:** an agent-reported success cannot be accepted without independent evidence and immutable provenance.
3. **Memory governance:** learning and retrieval can silently become policy bypasses or privacy leaks if write authority is not centralized.
4. **Cross-language contracts:** Python/TypeScript drift can cause incompatible enforcement decisions at the Node boundary.
5. **Ruflo/provider adapters:** provider behavior must be bounded and observable; provider availability cannot be treated as authority.
6. **Public release alignment:** independent repositories and package names currently make compatibility assumptions easy to miss.

## Reuse Decisions

### Reuse directly

- Core policy, eligibility, availability, passport, evidence, contract, context-pack, lifecycle, gateway, and verification primitives.
- Risk gates and typed state.
- Strategy feature/EV evaluation.
- Backtest fee, simulation, and analytics primitives.
- Node middleware transport and package verification.
- Cockpit UI components and test harness where not coupled to mock data.

### Extend

- Core contracts into `ExecutionEnvelope`, `VerificationResult`, `EvidenceChain`, `SwarmSpec`, and plugin stage objects.
- Core lifecycle controller into native enforcement gateway and guards.
- Existing provider qualification into all adapter health/capability semantics.
- Existing CI into cross-repo compatibility and evidence gates.

### Integrate

- Ruflo as the first agent runtime/swarm adapter.
- RuVector/OpenViking/code graph as intelligence/context providers.
- OmniRoute as the first execution provider.
- Specialized domain packages as risk/evaluation/simulation providers.

### Replace selectively

- Cockpit mock state/data path with typed control-plane API/event adapters.
- Node policy-adjacent heuristics with Core decisions or generated conformance behavior.
- Ambiguous package/repository metadata with canonical names and compatibility aliases where migration requires them.

### Build new

- Universal immutable execution envelope.
- Native enforcement kernel across all required lifecycle boundaries.
- Provider-neutral plugin and swarm contracts.
- End-to-end verification/evidence chain.
- Public compatibility/release manifest and launch gate.

## Overall Estimate

A credible first public control-plane milestone is approximately **70–110 engineer-weeks** distributed across parallel workstreams, with the enforcement, verification, evidence, and swarm areas on the critical path. This is a planning range, not a delivery commitment. A narrower alpha milestone can be reached sooner by limiting the first supported path to Core + Node + OmniRoute + local defaults, then adding Ruflo/RuVector and domain providers behind the same contracts.
