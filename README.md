# Verdict Portfolio — Governed Autonomy for Software Teams

> **Verdict is the policy and evidence layer for autonomous coding agents.**
> It determines whether an exact change, produced from an exact source state by
> an exact route, has earned the right to be accepted.

## The problem

Coding agents can already plan, edit, test, and open pull requests. Their own
“task completed” message is not trustworthy evidence that:

- the required checks actually ran;
- the patch stayed inside its authorized files and effects;
- the selected model was live and qualified for the task;
- the evidence belongs to the exact source being reviewed;
- a cheaper route is genuinely good for this task category;
- a learned recommendation is allowed to change production policy.

Verdict turns those questions into a fail-closed development contract and a
portable **Trusted Change Report**.

This is not another router. It is the acceptance authority after a route
produces a patch.

## Flagship: AutoDev Route Lab

The portfolio's first vertical product evaluates and governs model or combo
policies for software-development tasks using independently verified repository
outcomes.

```text
Objective + source snapshot
          |
          v
Bounded work-unit contract
          |
          v
OmniRoute discovery and execution
          |
          v
Verdict eligibility + protected-effect policy
          |
          v
Ruflo/Codex/Claude worker
          |
          v
Independent diff, test, policy, and CI evidence
          |
          v
Trusted Change Report
          |
          v
Advisory route recommendation
          |
          v
shadow -> candidate -> canary -> active
          or quarantine / rollback
```

The important constraint is that learned ranking and analytics may reorder only
routes that deterministic eligibility already admitted. A recommendation,
counterfactual, or worker self-report cannot authorize mutation, promotion, or
release.

## Ecosystem boundary

Verdict deliberately reuses the existing stack:

| System | Owns |
|---|---|
| [OmniRoute](https://github.com/diegosouzapw/OmniRoute) | provider/model transport, live discovery, task-aware combos, telemetry, scoring, fallback, and circuit breakers |
| [Ruflo](https://github.com/ruvnet/ruflo) | orchestration, swarms, workflows, hooks, memory, worker lifecycle, and generic proof ledgers |
| Codex, Claude, and other workers | planning, coding, review, and bounded command execution |
| Git and CI | immutable source, diffs, checks, and build evidence |
| **Verdict** | deterministic eligibility, protected-effect policy, source-state binding, acceptance evidence, outcome evaluation, and gated route-policy lifecycle |

In one line:

> Ruflo coordinates, OmniRoute serves, workers change code, Git and CI provide
> evidence, and Verdict decides what that evidence may authorize.

## Repositories

### AI development control plane

| Repository | Role |
|---|---|
| [`verdict-core`](https://github.com/mrnicholasbcarter-code/verdict-core) | Flagship policy and evidence authority: work units, eligibility, passports, receipts, evaluation, promotion, quarantine, and rollback |
| [`verdict-node`](https://github.com/mrnicholasbcarter-code/verdict-node) | Thin typed client and Express/Next.js integration; no duplicate policy engine |
| [`verdict-cockpit`](https://github.com/mrnicholasbcarter-code/verdict-cockpit) | Visual inspection of Trusted Change Reports, candidate funnels, verification, route comparisons, and lifecycle state |
| [`verdict-ecosystem`](https://github.com/mrnicholasbcarter-code/verdict-ecosystem) | This portfolio map, demo guide, and evidence index |

### Separate quantitative-systems case study

| Repository | Role |
|---|---|
| [`verdict-risk`](https://github.com/mrnicholasbcarter-code/verdict-risk) | risk authorization and position sizing |
| [`verdict-strategy`](https://github.com/mrnicholasbcarter-code/verdict-strategy) | strategy composition and validation |
| [`verdict-backtest`](https://github.com/mrnicholasbcarter-code/verdict-backtest) | reproducible and Monte Carlo validation |

The quantitative repositories demonstrate policy, risk, and evaluation
engineering. They are not runtime dependencies of AutoDev Route Lab.

`verdict-core-memory` is archived or experimental. The shared Codex/Claude
memory initiative is abandoned and is not a portfolio pillar, installation
dependency, or release blocker.

## Portfolio demonstration

The intended credential-free demo uses a small repository with a failing API
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

## Evidence status

The current repositories already contain useful primitives, but the integrated
flagship demo is still in development.

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

- [Portfolio product strategy](PORTFOLIO_PRODUCT_STRATEGY.md) — product boundary, capability audit, flagship flow, delivery plan, and release gate
- [Core repository](https://github.com/mrnicholasbcarter-code/verdict-core) — implementation workstream; installation claims require current default-branch and clean-install verification
- [Node repository](https://github.com/mrnicholasbcarter-code/verdict-node) — typed integration boundary
- [Cockpit repository](https://github.com/mrnicholasbcarter-code/verdict-cockpit) — visual portfolio surface

## Current status

Active development. The near-term objective is one reproducible, honest
vertical demo with an accepted change, a denied change, source-bound evidence,
an advisory route recommendation, and a tested rollback path.

## Release gate

This portfolio is presentable only after a clean checkout reproduces the
credential-free demo, accepted and denied changes, source-bound report,
advisory route recommendation, rollback path, clean-install checks,
contract-conformance checks, and independent reproduction of every primary
claim from the tagged source.

MIT — see individual repositories for license details.
