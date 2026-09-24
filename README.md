# Verdict V2 Ecosystem — Prime + Verdict + OmniRoute

> **Verdict is the policy-gated decision and evidence layer for model routing.**
> Verdict Core owns the goal-to-receipt orchestration (UNDERSTAND → PLAN/DAG → HYDRATE → hard eligibility → exact route selection → bounded execution/recovery → VERIFY → independent review → receipt).
> Prime is the user-facing agent surface and execution harness. OmniRoute exposes and
> executes model routes. Verdict applies hard eligibility and spend policy, selects
> only from admitted routes, and records why a route was accepted or dropped.

## The problem

An agent needs more than a model list or fallback proxy. It needs to know whether a
route is qualified for the task, whether required capabilities and context are
available, whether a cheaper route is allowed, why candidates were excluded, and
what evidence supports the final decision. Catalog presence and a worker's own
success message are not enough.

Verdict V2 combines three explicit owners:

| System | V2 ownership |
|---|---|
| **Prime** | user-facing agent surface, tools and execution harness for work Verdict dispatches |
| **Verdict** | goal-to-receipt orchestration (UNDERSTAND → PLAN/DAG → HYDRATE, hard eligibility, exact route selection, bounded execution/recovery, VERIFY → independent review → receipt), task and spend policy, hard eligibility, model metadata authority, context-plan/receipt contracts, deterministic selection reasons, and verification/evidence policy |
| **OmniRoute** | model/provider inventory, protocol transport, route execution, and observed route health; it is not Verdict's policy or model-metadata authority |

```text
User task in Prime
        |
        v
Verdict: UNDERSTAND task requirements
        |
        v
Verdict: PLAN/DAG + HYDRATE → hard eligibility + spend policy
        |
        v
Verdict: Select exact route and context/proof contract
        |
        v
OmniRoute: Transport and model execution
        |
        v
Prime: Tools / bounded work execution
        |
        v
Verdict: VERIFY + independent review + receipt
        |
        v
Named decision reason or drop reason
```

This is the frozen V2 boundary. Generic harness orchestration, Ruflo/swarm
architecture, gateway agnosticism, and a shared cross-harness memory product are not
V2 product scope. Historical AutoDev Route Lab and Trusted Change Report documents
remain planning history until they are either archived or reconciled. They must not
be cited as shipped V2 behavior.

## Shipped versus planned

The current default branches contain Core routing and receipt primitives plus Node
and Cockpit integration surfaces. This statement is source-level only. Exact behavior, package, and release claims
must be checked against each repository's default branch, registry, CI, and runtime
evidence. The ecosystem compatibility manifest is a bounded source-pin/schema check;
it does not by itself prove end-to-end runtime compatibility.

A credential-free, cross-repository V2 demo and canonical Cockpit receipt explorer
remain planned work. The [Compatibility matrix](docs/COMPATIBILITY_MATRIX.md) and
owning Linear stories record narrower states; planned work must remain labeled
planned.

## Repositories

### V2 active repositories

| Repository | Role |
|---|---|
| [`verdict-core`](https://github.com/mrnicholasbcarter-code/verdict-core) | V2 policy authority: task requirements, hard eligibility, spend-aware selection, context/receipt contracts, and named decision reasons |
| [`verdict-node`](https://github.com/mrnicholasbcarter-code/verdict-node) | Thin typed client and Express/Next.js integration; no duplicate policy engine |
| [`verdict-cockpit`](https://github.com/mrnicholasbcarter-code/verdict-cockpit) | Shipped fixture-mode React/TypeScript viewer; BOD-14 owns the planned canonical receipt explorer |
| [`verdict-ecosystem`](https://github.com/mrnicholasbcarter-code/verdict-ecosystem) | Cross-repository V2 product truth, compatibility evidence, process, and demo/release planning |

### Legacy quantitative case-study repositories (not V2 runtime)

| Repository | Role |
|---|---|
| [`verdict-risk`](https://github.com/mrnicholasbcarter-code/verdict-risk) | risk authorization and position sizing |
| [`verdict-strategy`](https://github.com/mrnicholasbcarter-code/verdict-strategy) | strategy composition and validation |
| [`verdict-backtest`](https://github.com/mrnicholasbcarter-code/verdict-backtest) | reproducible and Monte Carlo validation |

The quantitative repositories are historical case studies. They are not V2 runtime
dependencies.

`verdict-core-memory` is archived (read-only) as a retired duplicate identity. It is not an installation dependency. Useful memory ideas are tracked for verdict-continuity.

## ADR lifecycle index

The authoritative, evidence-bounded ADR lifecycle index lives in
[`docs/ADR_LIFECYCLE.md`](docs/ADR_LIFECYCLE.md), generated from
machine-readable source data in
[`evidence/ADR_LIFECYCLE.json`](evidence/ADR_LIFECYCLE.json), which records
exact repository SHAs, lifecycle classifications, and verification evidence
for every production ADR file.

This index is source-level evidence. It withholds `CURRENT` unless executable
runtime proof is recorded, and it explicitly marks `verdict-continuity`
decisions as V3-deferred for the frozen V2 scope. Re-running the deterministic
check is part of CI (see
[`scripts/check_adr_lifecycle.py`](scripts/check_adr_lifecycle.py) and
[`tests/test_adr_lifecycle.py`](tests/test_adr_lifecycle.py)). Default CI checks the independently generated immutable
[`evidence/ADR_SOURCE_MANIFEST.json`](evidence/ADR_SOURCE_MANIFEST.json), including exact repository/commit/path/content hashes, the full ADR inventory, the excluded fixture, and every citation path. Run
[`scripts/verify_adr_sources.py`](scripts/verify_adr_sources.py) without arguments for that credential-free check, or pass `--repo-root <directory>` to recheck the same facts from local pinned Git objects during refresh or audit.

## Historical AutoDev demonstration plan (not shipped V2)

The historical intended credential-free demo uses a small repository with a failing API
authorization test and a protected policy file:

1. Verdict binds the objective to an immutable source snapshot and bounded work
   units.
2. Fresh route qualification excludes a stale or unverified candidate.
3. One candidate patch is denied because it edits a protected file or weakens a
   test, regardless of the worker's success claim.
4. A second patch stays in bounds and passes focused plus independent regression
   checks.
5. The Trusted Change Report shows requested, selected, and actual route;
   source identity; policy decisions; diff; checks; failure class; latency; and
   measured usage/cost when available.
6. Route Lab compares verified outcomes by task category and recommends a
   shadow or candidate transition without promoting itself.
7. A regression observation demonstrates quarantine or rollback.

Fixture provider responses are labelled simulations. Live mode uses qualified
concrete `cx/gpt-*` routes through OmniRoute and reports unavailable or
unprovable runtime state as `unknown`.

## Demo command

Not available yet. The release gate requires one credential-free command from
a clean checkout that produces accepted, denied, route-recommendation, and
rollback reports. This placeholder must be replaced with the verified command
before the portfolio is described as presentable.

## Historical AutoDev evidence status

This table preserves the older AutoDev planning state. It is non-canonical for V2; the integrated demo described here was not shipped.

| Capability | Current evidence |
|---|---|
| Fail-closed model eligibility and capability passports | Evidence reported across Core branches; not yet reconciled into one default-branch release claim |
| Durable receipt chains and integrity checks | Evidence reported across Core branches; not yet reconciled into one default-branch release claim |
| Real bounded AutoDev patch execution and owned-file verification | Implemented on unmerged `feat/autodev-v0.1` at reviewed commit `cc34e89`; not a default-branch or release claim |
| Replay-only counterfactuals | Source and tests exist on a feature branch; no live integrated proof |
| `unqualified -> shadow -> candidate -> canary -> active` lifecycle | Source and tests exist on a feature branch with degradation, quarantine, kill switch, and rollback; not yet a shipped claim |
| End-to-end Trusted Change Report | Planned integration slice |
| Per-task-category Route Lab recommendations | Planned integration slice |
| Cockpit using production report contracts | Planned integration slice |

The strategy audit distinguishes four evidence states: documented,
source-implemented, live-configured, and behaviorally verified. A lower state
never implies a higher one.

## What this portfolio does not claim

- It is not another generic model router, proxy, swarm framework, or shared
  agent-memory product.
- It does not claim that catalog rows or `auto/*` aliases prove live model
  availability.
- It does not claim provider/model counts that were not verified against the
  current runtime.
- It does not label fixture measurements as live benchmarks.
- It does not claim SONA/RuVector learning loops are part of the flagship.
- It does not claim packages are published until registries and clean installs
  are independently verified.
- It does not claim a worker, route recommendation, or counterfactual can
  authorize its own promotion or release.

## Documentation

- [Spec Kit Lite](docs/SPEC_KIT_LITE.md) — canonical lightweight change contract for significant Verdict V2 work
- [Ecosystem constitution](.specify/memory/constitution.md) — cross-repository governance and proof requirements
- August 2026 audit snapshots (dated, **not current**): [current-state audit](CURRENT_STATE_AUDIT.md), [gap analysis](ARCHITECTURE_GAP_ANALYSIS.md), [lift analysis](IMPLEMENTATION_LIFT_ANALYSIS.md), [research](IMPLEMENTATION_RESEARCH.md), [story status](IMPLEMENTATION_STATUS.md), [roadmap](ROADMAP.md)
- [Portfolio product strategy](PORTFOLIO_PRODUCT_STRATEGY.md) — historical product direction that is under V2 truth audit; do not treat planned AutoDev/Ruflo behavior as shipped
- [Compatibility matrix](docs/COMPATIBILITY_MATRIX.md) — generated from [`compatibility-manifest.json`](compatibility-manifest.json); CI fails on drift, link rot, or a published artifact that does not install
- [Core repository](https://github.com/mrnicholasbcarter-code/verdict-core) — implementation workstream; installation claims require current default-branch and clean-install verification
- [Node repository](https://github.com/mrnicholasbcarter-code/verdict-node) — typed integration boundary
- [Cockpit repository](https://github.com/mrnicholasbcarter-code/verdict-cockpit) — visual portfolio surface

## Current status

Active V2 truth and integration closeout. Canonical scope is Prime + Verdict + OmniRoute. The credential-free demo, Cockpit receipt explorer, current compatibility proof, and public interview surface remain tracked work rather than shipped claims.

## Release gate

This portfolio is presentable only after a clean checkout reproduces the
credential-free demo, accepted and denied changes, source-bound report,
advisory route recommendation, rollback path, clean-install checks,
contract-conformance checks, and independent reproduction of every primary
claim from the tagged source.

MIT — see individual repositories for license details.
