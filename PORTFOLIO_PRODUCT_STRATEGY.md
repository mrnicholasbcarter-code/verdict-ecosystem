# Verdict Portfolio Product Strategy

**Status:** Approved product boundary; implementation and release evidence pending

**Date:** 2026-08-15

**Audience:** contributors, implementation agents, reviewers, interviewers, and potential clients

## 1. Product decision

Verdict should become an **evidence-gated autonomous development control
plane**.

Its promise is:

> Autonomous coding tools can produce a patch. Verdict determines whether that
> exact patch, produced by that exact route from that exact source state, has
> earned the right to be accepted. It then uses independently verified outcomes
> to recommend which model or OmniRoute combo should receive similar work next.

This is a control and evaluation product for software changes, not another
agent framework or model gateway.

The shared Codex/Claude memory initiative is abandoned. Memory, context
hydration, and generic knowledge retrieval are not a Verdict product pillar.

## 2. The problem worth solving

Teams can already ask coding agents to plan, edit, test, review, and open pull
requests. The hard problem is deciding when their output is trustworthy:

- the model reported success, but did the declared verification actually run?
- did the patch stay inside its work-unit ownership and policy envelope?
- was the selected route really available and qualified for the required tools?
- does the evidence belong to the exact commit and dirty-tree state being reviewed?
- was a cheaper model genuinely successful on this category of task, or merely fast?
- can a route policy be changed without letting learned ranking bypass hard safety rules?
- can a reviewer reproduce why a change or route promotion was allowed?

Verdict should answer these questions with an enforceable development contract
and source-bound evidence, then fail closed when a required fact is unknown.

## 3. Ecosystem boundary

The portfolio is credible only if each project owns a distinct layer.

| System | Reuse it for | Verdict must not duplicate |
|---|---|---|
| **OmniRoute** | provider/model transport, live discovery, task-aware combos, cost/latency/quota/health scoring, fallback, circuit breakers, usage analytics, and eval-assisted target ordering | provider adapters, generic model scoring, static task-fitness tables, combo execution, gateway analytics, or transport failover |
| **Ruflo** | orchestration, swarms, workflows, hooks, memory, worker lifecycle, generic proof envelopes, and coordination ledgers | another swarm runtime, generic workflow engine, shared agent memory, or general-purpose proof ledger |
| **Codex/Claude/other workers** | planning, coding, review, and bounded command execution | another coding model or IDE agent experience |
| **Git and CI** | immutable commits, diffs, tests, checks, and deployment status | source hosting or a replacement CI runner |
| **Verdict** | deterministic task/role eligibility, protected-effect policy, source-state binding, independent acceptance evidence, outcome evaluation, counterfactual comparison, and gated route-policy promotion | everything in the columns above |

The concise division is:

```text
Ruflo coordinates the work.
OmniRoute finds and serves the route.
Workers produce the change.
Git and CI provide source and check evidence.
Verdict decides what that evidence is allowed to authorize.
```

## 4. Capability audit method

Portfolio claims use four distinct evidence states:

1. **Documented** — a guide or design says the capability exists.
2. **Source-implemented** — a named branch, commit, or tagged source snapshot contains an executable path and tests.
3. **Live-configured** — the installed runtime is configured to expose the path.
4. **Behaviorally verified** — a current probe exercised the path and retained evidence.

No lower state implies a higher one. Catalog entries, aliases, configuration,
and test fixtures are not runtime proof.

### Current overlap matrix

This matrix is intentionally conservative. `Yes` means evidence for that state
was found during the 2026-08-15 review and must name the branch, commit,
runtime, or retained probe evidence. `Partial` means the adjacent capability
exists but not the complete portfolio behavior; `no finding` is not a claim of
impossibility.

| Capability | OmniRoute | Ruflo | Verdict | Portfolio decision |
|---|---|---|---|---|
| Task/category routing | documented and source-implemented; live health verified, route behavior not re-verified in this review | documented and source-implemented | eligibility/ranking foundations implemented | **Reuse OmniRoute** |
| Cost, latency, quota, health, fallback | documented and source-implemented; health endpoint verified | partial orchestration overlap | partial adapters and policy inputs | **Reuse OmniRoute** |
| Eval-driven target reordering | source-implemented and wired behind configuration | candidate comparison exists | evaluation reports exist | **Reuse OmniRoute execution; Verdict consumes results as evidence** |
| Analytics-derived combo recommendation from verified development outcomes | no complete closed loop found | task-bucket and candidate-learning pieces, but gaps remain in per-model selection use | evaluation and promotion primitives exist, not an integrated AutoDev loop | **Extend Verdict at the acceptance boundary** |
| Generic agent orchestration and workflows | cloud-agent/bridge surfaces exist | documented and source-implemented | two AutoDev paths exist, one largely synthetic | **Reuse Ruflo/workers; do not build another generic orchestrator** |
| Real bounded patch execution | agent dispatch exists | worker execution exists | CLI-wired work units, patch boundaries, verification, and durable outcomes exist on the unmerged `feat/autodev-v0.1` branch | **Extend Verdict's real AutoDev runner after integration review** |
| Generic proof envelope or ledger | audits and retained eval artifacts exist | HMAC proof envelopes, hash chaining, and durable run ledger exist | durable receipt chains exist | **Do not sell receipts alone** |
| Exact source/work-unit acceptance contract | partial audit artifacts | partial proof and policy gates | owned-file enforcement and verification receipts exist; full immutable source snapshot binding needs integration | **Verdict flagship boundary** |
| Protected-effect authorization | management/auth/guardrails exist | guidance gates exist | deterministic allow/deny/unknown and policy transitions exist | **Verdict owns development-specific authorization** |
| Counterfactual route replay | reasoning/eval replay pieces exist | comparison harnesses exist | replay-only counterfactuals cannot authorize promotion | **Extend Verdict's authority separation** |
| Shadow/candidate/canary/active route lifecycle | release and routing controls exist, but no complete development-outcome promotion loop was found | promotion/learning pieces exist | source and tests exist on the unmerged AutoDev branch with kill switch, degradation, quarantine, and rollback; no live end-to-end proof | **Integrate and behaviorally verify before marketing** |
| CI regression authority | CI/release gates exist | validation workflows exist | evidence contracts exist, but end-to-end CI-bound acceptance is incomplete | **Verdict consumes CI evidence and decides authorization** |

Important audit corrections:

- OmniRoute already provides far more than transport: `auto/*` category/tier
  combos, task fitness, eval-driven target ordering, analytics, health, quota,
  fallback, and multiple agent protocols. A routing-first Verdict would be a
  weaker duplicate.
- Ruflo already provides broad orchestration, model routing, workflows,
  learning, proof envelopes, ledgers, and governance. An AutoDev framework or
  receipt-ledger-first Verdict would also be a duplicate.
- Verdict feature branches already contain unusually useful primitives:
  fail-closed eligibility,
  capability passports, durable receipts, a real bounded patch runner,
  independently verified evaluation observations, replay-only
  counterfactuals, and gated route lifecycle transitions. These capabilities
  are not all present on the current default branch. The portfolio work is to
  review and integrate the smallest coherent subset into one honest end-to-end
  product.

## 5. Flagship product: Verdict AutoDev Route Lab

The first product slice should be **AutoDev Route Lab**, a local-first workflow
that evaluates and governs model/combo policies for software-development task
categories using verified repository outcomes.

### Input contract

Each run begins with:

- an objective and task category;
- repository and immutable source-state identity;
- bounded work units with exact owned paths;
- required capabilities and role policy;
- allowed effects, commands, spend, retries, and escalation rules;
- candidate concrete routes or OmniRoute combos;
- acceptance commands and independent evidence requirements.

### Runtime flow

```text
Objective + source snapshot
          |
          v
Bounded work-unit contract
          |
          v
Fresh route discovery from OmniRoute
          |
          v
Verdict deterministic eligibility and protected-effect gate
          |
          v
Ruflo/Codex/Claude worker execution in an isolated scope
          |
          v
Independent diff-boundary, test, policy, and CI verification
          |
          v
Tamper-evident acceptance bundle bound to source + route + outcome
          |
          v
Per-category Route Lab comparison and recommendation
          |
          v
Shadow -> candidate -> canary -> active, or quarantine/rollback
```

Learned ranking and analytics may reorder only routes that deterministic
eligibility already admitted. A recommendation cannot mutate source, promote a
route, or publish an artifact. Those remain separate protected actions.

### Output contract

One run produces a redacted, portable report answering:

- what objective and source snapshot were evaluated;
- which work units and effects were authorized;
- which routes were considered, excluded, requested, selected, and actually served;
- what files changed and whether ownership boundaries held;
- what tests, checks, and reviews ran, with exit status and artifact digests;
- whether the change is accepted, denied, or unknown, and why;
- measured latency, token usage, cost when available, and failure class;
- whether the observation is eligible for learning or promotion;
- what route-policy change is recommended, with confidence and limitations.

The portfolio-facing name for this artifact is a **Trusted Change Report**.

## 6. The 3–5 minute portfolio demonstration

The demo must be understandable without credentials and impressive with a live
runtime.

### Fixture scenario

Use a small versioned repository containing a realistic failing API
authorization test and one protected file outside the task boundary.

1. Show the objective: fix the authorization bug without modifying the policy
   definition or weakening tests.
2. Show fresh candidate qualification and why an unverified route is excluded.
3. Dispatch a bounded implementation to a cheap `cx/gpt-*` route through
   OmniRoute. If fixture mode is used, label the recorded worker responses as
   deterministic fixtures.
4. Demonstrate one rejected candidate patch that edits a protected file or
   weakens a test. The worker's self-reported success does not matter.
5. Demonstrate one accepted patch whose diff stays in bounds and whose focused
   tests plus independent regression check pass.
6. Open the Trusted Change Report: exact source, requested/actual route, policy
   decisions, diff, checks, costs/tokens when measured, and receipt integrity.
7. Show Route Lab comparing verified outcomes for a cheaper route and a stronger
   route in this task category. It recommends shadow/candidate promotion but
   cannot promote itself.
8. Trigger a regression observation and show quarantine or rollback.

The closing sentence should be:

> OmniRoute made model choice operational and Ruflo made agents operational.
> Verdict makes accepting and learning from autonomous changes governable.

### Live mode

Live mode uses qualified concrete `cx/gpt-*` routes through OmniRoute and
records the requested, selected, and actually served identities. If the runtime
cannot prove availability, identity, or required capabilities, the run reports
`unknown` or denies the protected action. It never silently substitutes a
catalog claim.

## 7. Marketability standard

A visitor should understand the project at three depths.

### Thirty-second skim

- one sentence describing the trust problem;
- one architecture diagram showing the ecosystem boundary;
- one screenshot of an accepted and rejected autonomous change;
- one command that runs the credential-free demo;
- explicit status and limitations.

### Three-to-five-minute review

- the fixture walkthrough above;
- a Trusted Change Report that can be inspected without a running service;
- a visible deny path, not only a successful happy path;
- a route recommendation backed by independently verified outcomes;
- a clear explanation of why the recommendation cannot self-authorize.

### Deep technical review

- versioned contracts and JSON schemas;
- threat model and authorization invariants;
- deterministic fixture data plus optional source-bound live evidence;
- tests for stale/unknown state, tampering, boundary escape, route mismatch,
  forged promotion, and rollback;
- architecture decision records that explicitly assign OmniRoute, Ruflo, Git,
  CI, and Verdict ownership;
- reproducible benchmark inputs and honest methodology.

Avoid vanity provider/model counts, generated dashboards without a real data
path, synthetic success labelled as a benchmark, unsupported performance
claims, giant feature lists, and an autonomous system whose only evidence is
its own completion message.

## 8. Repository roles

### verdict-core

The flagship authority and implementation. It owns work-unit contracts,
deterministic eligibility, capability/runtime passports, protected-effect
policy, source-bound evidence, acceptance decisions, outcome evaluation,
counterfactual authority separation, and promotion/quarantine rules.

### verdict-node

A thin typed client and integration layer. It should expose Core contracts to
Node/Express/Next.js users and pass cross-language conformance tests. It must
not implement a second policy engine, route learner, or receipt authority.

### verdict-cockpit

The visual inspection surface for Trusted Change Reports and Route Lab. Its
first views should be run timeline, work-unit status, candidate funnel,
diff/check evidence, route comparison, and promotion/quarantine state. It
should render fixture data through the same contracts as live data.

### verdict-ecosystem

The portfolio landing page, compatibility map, demo guide, and evidence index.
It should distinguish verified-current, fixture-only, experimental, and roadmap
claims.

### verdict-core-memory

Archived or experimental only. It is not part of the flagship narrative,
installation path, architecture diagram, or release gate.

### verdict-risk, verdict-strategy, and verdict-backtest

A separate quantitative-systems case study. Preserve it as evidence of policy,
risk, and evaluation engineering, but do not present it as a dependency of the
autonomous-development product.

## 9. Fastest credible delivery plan

### Phase 0 — preserve credibility

- keep the already-pushed credential-free Core quickstart repair;
- align this landing page and every primary README to the approved product boundary;
- remove or qualify routing-first, shared-memory, SONA, provider-count, package,
  benchmark, and production claims that lack current evidence;
- identify the authoritative Core branch before integrating any old worktree.

### Phase 1 — one vertical contract

- define versioned work-unit, source-state, route-decision, verification, Trusted
  Change Report, and route-recommendation schemas;
- connect the real `verdict autodev` runner to capability passports,
  deterministic eligibility, and evaluation receipts;
- bind dirty-tree state as an immutable snapshot rather than using `HEAD` alone;
- classify operational failures separately from code-quality failures;
- ensure counterfactual observations and recommendations cannot authorize
  mutation or promotion.

### Phase 2 — reproducible demo

- add the small authorization-bug fixture repository and recorded provider fixtures;
- produce accepted, rejected, stale-evidence, regression, and rollback reports;
- add one command that generates all fixture evidence from a clean checkout;
- add an optional live command using qualified `cx/gpt-*` routes.

### Phase 3 — Route Lab and Cockpit

- aggregate independently verified outcomes by task category and exact route;
- compare success, quality, latency, token usage, cost, and operational failures;
- emit advisory combo/route recommendations with sample size and confidence;
- gate route lifecycle transitions through existing
  `shadow -> candidate -> canary -> active` policy;
- render the exact same report and recommendation contracts in Cockpit.

### Phase 4 — portfolio conversion

- publish the architecture boundary, threat model, benchmark methodology, and
  limitations;
- capture one concise screenshot set and a three-to-five-minute walkthrough;
- run clean-install, full regression, security, schema-conformance, and demo
  reproduction checks against the exact release source;
- tag or release only after explicit authorization and green independent evidence.

## 10. Autonomous delivery policy

Research, architecture, security, and cross-repository decisions use the
strongest qualified reasoning route available. Once a contract is approved,
bounded implementation, fixtures, focused tests, formatting, and documentation
use the cheapest qualified worker.

For GPT workers, requests use the OmniRoute-facing `cx/gpt-*` identity, such as
`cx/gpt-5.4-mini` or `cx/gpt-5.5`. A native worker API may normalize that to an
unprefixed model name; reports must preserve the requested route separately
from the actual served identity rather than claiming the prefix was executed.

Every delegated work unit specifies:

- objective and measurable acceptance criteria;
- repository, isolated worktree, and exact write ownership;
- prohibited actions and protected paths;
- model/route class and escalation condition;
- focused and integration checks;
- required source-bound handoff evidence.

One worktree has one writer. The integration owner alone changes shared
manifests or lockfiles. Read-only reviewers may share a checkout. When the
repository owner has authorized commit and push, atomic safe slices are pushed
immediately because the development host is disposable. No merge, release,
publication, destructive action, or protected promotion is implied by
permission to implement and push a feature branch.

## 11. Portfolio release gate

The flagship is ready to present when:

- a clean checkout runs the credential-free demo with one documented command;
- the same versioned contracts support fixture and optional live modes;
- at least one accepted and one denied change are reproducible;
- source identity includes tracked and untracked changes or requires a clean commit;
- requested, selected, and actual route identities are retained;
- worker self-report is never sufficient verification;
- stale, unknown, mismatched, or tampered evidence fails closed;
- operational failures are not scored as model-quality failures;
- route recommendations show sample size, confidence, and limitations;
- counterfactual evidence cannot authorize learning, mutation, or promotion;
- promotion and rollback paths are independently tested;
- Cockpit renders real report contracts rather than bespoke mock shapes;
- Core and Node pass clean-install and contract-conformance checks;
- the README, screenshots, demo, schemas, CI, and release tag describe the same behavior;
- an independent reviewer can reproduce every primary claim from the tagged source.

## 12. Immediate implementation slices

After this strategy is committed, the next work should be specified and
dispatched in this order:

1. **Contract gap audit:** map existing Core types to the vertical report and
   identify the smallest schema additions.
2. **Source-state binding:** define and test clean-commit and dirty-snapshot
   identities for AutoDev runs.
3. **Eligibility integration:** make the real AutoDev runner consume fresh
   passports and deterministic route decisions before worker execution.
4. **Trusted Change Report:** project existing receipts, verification, and
   route evidence into one portable redacted report.
5. **Fixture demo:** generate accepted, rejected, and rollback paths using the
   production contracts.
6. **Route Lab recommendation:** aggregate verified outcomes by task category
   and emit advisory recommendations that cannot self-promote.
7. **Cockpit adapter:** render the report and route lifecycle without adding
   policy logic to the UI.

Each slice should land as a small conventional commit on an isolated branch and
be pushed as soon as its focused verification passes.
