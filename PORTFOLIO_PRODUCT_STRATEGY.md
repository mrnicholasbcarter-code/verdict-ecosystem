# Verdict Portfolio Product Strategy

**Status:** Superseded pending OmniRoute overlap and market differentiation review  
**Date:** 2026-08-15  
**Audience:** contributors, implementation agents, reviewers, interviewers, and potential clients

> **Decision hold (2026-08-15):** OmniRoute already implements task-aware
> routing, `auto/<category>:<tier>` virtual combos, cost/latency/quota/health
> scoring, provider fallback, circuit breakers, connection cooldowns, model
> lockouts, Fusion/pipeline strategies, telemetry, and routing transparency.
> The routing-first Verdict thesis below must not drive further implementation
> until the active capability, competitive, and portfolio research establishes
> a non-duplicative product boundary. Treat the remainder as historical input,
> not an approved build specification.

> **Leading replacement hypothesis:** Verdict becomes OmniRoute's local-first
> evidence, authorization, and replay layer: OmniRoute routes and executes;
> Verdict records route/action receipts, enforces protected-action policy,
> replays traffic against policy/model changes, and produces CI/audit evidence.
> This remains under research until the source/runtime capability audit is
> complete.

## 1. The product hypothesis under review

Verdict Core should solve one clear problem:

> Route each AI request to the least expensive currently available model that
> satisfies the task's capability, privacy, reliability, and policy
> requirements, then produce an auditable explanation of the decision.

The near-term product is a **policy-gated, cost-aware model router**. The
long-term autonomous-AI control-plane vision remains a roadmap, not a claim
that blocks the first portfolio release.

Verdict's differentiation is not transport alone. Existing gateways already
forward requests. Verdict owns the enforceable decision boundary:

1. normalize the task and policy;
2. inspect fresh runtime and capability evidence;
3. reject ineligible concrete routes before ranking;
4. select the lowest-cost eligible route;
5. execute with bounded retries and policy-safe fallback;
6. emit a receipt that explains the selection and every exclusion;
7. compare verified success, cost, and latency against a declared baseline.

## 2. Portfolio promise

A visitor should understand Verdict in thirty seconds:

> Teams using multiple AI models either waste money by sending everything to
> frontier models or accept risk from simplistic cheap-model routing. Verdict
> filters candidates through hard capability, privacy, budget, availability,
> and authorization rules, chooses the least-cost eligible route, handles
> failure safely, and records why the decision was made.

The flagship demonstration must show:

1. a routine task selecting a low-cost route;
2. a difficult coding task selecting a stronger route;
3. a protected task rejecting an unverified or disallowed provider;
4. a forced provider failure followed by an allowed fallback or explicit
   denial;
5. the candidate funnel, final receipt, cost, latency, and outcome;
6. an honest comparison with always-frontier and always-cheap baselines.

Two modes are required:

- **Fixture mode:** deterministic, credential-free, and runnable from a clean
  checkout.
- **Live mode:** source-bound to a reachable OmniRoute or other documented
  OpenAI-compatible runtime, with unavailable runtime state reported as
  unknown rather than inferred from a catalog.

Fixture measurements must be labelled simulations. Live savings claims require
published task inputs, provider/model identities, raw results, environment,
and a reproducible analysis command.

## 3. Architecture and repository ownership

```text
Application / agent
        |
        v
    Verdict Core
 policy + eligibility
 availability + cost
 route + fallback
        |
        v
 OmniRoute / OpenAI-compatible runtime
        |
        v
 decision receipt + metrics + explanation
        |
        v
  Verdict Cockpit
```

### verdict-core

The only policy authority and flagship implementation. It owns task/policy
contracts, capability and availability qualification, eligibility, cost-aware
selection, bounded execution/fallback, explainability, receipts, fixture/live
demos, and reproducible benchmarks.

### verdict-node

A thin typed integration layer. It owns the Core client, Express/Next.js
middleware, OpenAI-compatible forwarding, contract-conformance tests, and one
runnable example. It must not become a second policy or routing authority.

### verdict-cockpit

The visual portfolio surface. The first useful views are live decisions,
candidate eligibility/exclusions, provider/model health, and cost/latency/
fallback/success metrics. Mock trading/order-book behavior is outside the AI
routing portfolio path.

### verdict-ecosystem

The portfolio landing page and cross-repository compatibility map. It presents
two separate tracks:

1. AI infrastructure: Core, Node, and Cockpit.
2. Quantitative systems: Risk, Strategy, and Backtest.

It must link only verified claims and current repository status.

### verdict-core-memory

The shared Codex/Claude memory initiative is abandoned and is not a product
pillar, integration dependency, or release blocker. The repository should be
marked experimental/deprecated and removed from the primary portfolio path.

### verdict-risk, verdict-strategy, and verdict-backtest

These form a separate quantitative-systems case study: signal evaluation,
risk authorization, and Monte Carlo validation. They should not be described as
runtime components of the AI router.

## 4. Autonomous-development approach

The existing twelve-stage `AutoDevWorkflow` is not accepted as proof of an
autonomous engineering system merely because it emits stage artifacts. A real
workflow must bind every completion claim to an observed action and source
state.

Use this lean execution loop:

1. **Frame** — read the ticket, repository instructions, dirty state, relevant
   ADRs/contracts, and define measurable acceptance criteria.
2. **Research and decide** — use a strong model for product, architecture,
   security, or ambiguous cross-repository decisions; record rejected options
   and write an ADR only for a durable decision.
3. **Slice and route** — create bounded work units with exact repository,
   worktree, file ownership, tests, dependencies, model tier, retry budget, and
   escalation condition.
4. **Execute** — assign each writing unit to exactly one writer in an isolated
   worktree. Prefer deterministic tools and lesser models for mechanical edits,
   docs, fixtures, focused tests, and straightforward adapters.
5. **Verify independently** — run focused checks, failure paths, repository
   regression gates, clean-install/demo smoke, and independent diff review.
6. **Integrate and receipt** — the parent reconciles source-bound outputs and
   reports exact evidence. Commit, push, PR, merge, release, or publication only
   occur when explicitly authorized and the relevant gate is green.

The loop stops at the authorized objective. It does not automatically choose
and merge the next backlog issue.

### Model allocation policy

| Work | Preferred route | Escalate when |
|---|---|---|
| Search, inventory, documentation comparison | OmniRoute free/fast explorer or `cx/gpt-5.4-mini` | evidence conflicts or the decision changes scope |
| Mechanical edits, fixtures, focused tests, formatting | deterministic tool, free/fast worker, or `cx/gpt-5.4-mini` | two failed attempts or ownership ambiguity |
| Bounded implementation from an approved spec | cheapest qualified coding route | contract/security implications emerge |
| Architecture, product scope, security boundaries, integration synthesis | `cx/gpt-5.5` or stronger qualified reasoner | human authority or product choice is required |
| Independent review | provider-diverse model where available | critical finding needs senior adjudication |

Catalog registration, aliases, and `auto/*` names are not proof of live
availability. Runtime qualification should precede model assignment. If a
requested route cannot be verified, use an available lesser route for bounded
work or escalate; do not silently claim the requested model executed.

### Work-unit contract

Every delegated implementation task must specify:

- objective and acceptance criteria;
- repository, branch/worktree, and exact write scope;
- prohibited actions and protected paths;
- expected tests and evidence commands;
- model/route class and why it is sufficient;
- retry/time budget and escalation trigger;
- required handoff: changed paths, commands/results, limitations, and source
  state.

One worktree has one writer. Read-only reviewers may share a checkout. The
integration owner alone changes shared manifests or lockfiles.

## 5. Portfolio release gates

The portfolio release is ready when all of these are true:

- a clean checkout can install and run the fixture demo using documented
  commands;
- the live demo either executes through a qualified runtime or fails explicitly
  as unavailable/unknown;
- three routing scenarios and one forced-failure scenario produce explainable,
  privacy-safe receipts;
- benchmarks compare always-frontier, always-cheap, and Verdict routing on a
  published fixed task set;
- cost is reported per verified successful task, with latency, route errors,
  fallback rate, and policy-denial rate;
- Core and Node default branches have green required CI and clean-install
  checks;
- Node delegates policy to Core and passes contract-conformance tests;
- Cockpit renders real Core decisions and exclusions;
- README, repository descriptions, badges, package names, links, screenshots,
  and status claims agree;
- unsupported shared-memory, SONA, throughput, latency, and production claims
  are removed or explicitly labelled experimental;
- an independent reviewer can reproduce the demo and evidence from the tagged
  source state.

## 6. Fast execution order

### Phase 0 — credibility repair

- select the authoritative Core branch and reconcile open work;
- fix Core and Node default-branch CI/security/clean-install failures;
- fix the clean-checkout fixture demo;
- align repository descriptions, links, badges, and product terminology;
- deprecate the shared-memory narrative and remove unsupported claims.

### Phase 1 — real golden path

- implement request -> qualification -> eligibility -> route -> execution ->
  fallback -> receipt against fixture and live adapters;
- include policy denial and provider failure paths;
- freeze Core/Node contracts and add cross-repository conformance tests.

### Phase 2 — evidence

- publish the fixed task set and baselines;
- run source-bound fixture and live benchmarks;
- preserve raw evidence and generate a concise case study.

### Phase 3 — presentation

- connect Cockpit to Core;
- add architecture and decision-funnel visuals;
- record a three-to-five-minute walkthrough;
- publish an honest limitations section and a tagged release after approval.

## 7. First delegated workstreams

These streams may run in parallel only in separate worktrees:

1. **Core credibility:** clean-checkout quickstart, demo truthfulness, default
   branch CI/security root causes.
2. **Node boundary:** thin-client contract audit, clean-install/lint repairs,
   duplicated-policy removal plan.
3. **Cockpit surface:** current-state audit and minimal real-Core dashboard spec.
4. **Portfolio alignment:** landing-page rewrite, repository status matrix,
   stale/unsupported claim removal.
5. **Autodev golden path:** replace synthetic stage-completion claims with the
   lean work-unit loop and a real small-repository proof, keeping release and
   external mutation human-authorized.

The parent agent owns architecture, cross-repository integration, evidence
adjudication, and final release recommendation.
