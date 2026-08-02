# Verdict Ecosystem — Policy-Gated LLM Routing Control Plane

> **The gate rules on each task** — deterministic safety verdicts, availability-aware routing, quantitative-trading-grade execution, closed-loop telemetry.

---

## Repository Map

| Repo | Purpose | Language | Status |
|------|---------|----------|--------|
| [`verdict-core`](https://github.com/mrnicholasbcarter-code/verdict-core) | Python control plane (flagship) | Python | ✅ 321 tests |
| [`verdict-node`](https://github.com/mrnicholasbcarter-code/verdict-node) | Express/Next.js middleware (`@bodanglin/verdict-node`) | TypeScript | ✅ 169 tests |
| [`verdict-cockpit`](https://github.com/verdict/verdict-cockpit) | Next.js dashboard | TypeScript | 🚧 |
| [`verdict-risk`](https://github.com/verdict/verdict-risk) | Zero-allocation risk engine | Python | 🚧 |
| [`verdict-edge`](https://github.com/verdict/verdict-edge) | Edge mining framework | Python | 🚧 |
| [`verdict-backtest`](https://github.com/verdict/verdict-backtest) | Monte Carlo harness | Python | 🚧 |
| `verdict` | Umbrella/meta repo | — | 🚧 |

---

## What is Verdict?

Verdict is a **policy-gated, availability-aware LLM routing control plane** — not a simple proxy. It provides:

- **Deterministic safety floors**: Hard gate checks (capability, budget, privacy, availability) run locally before any upstream call
- **Availability-aware routing**: Bounded cache with stale-while-revalidate, explicit `unknown`/`error` states, concurrent refresh deduplication
- **Explainability first**: `GET /v1/route/explain` surfaces observed_at, expires_at, age, source, confidence, candidate/eligible counts, per-candidate exclusion reasons, cache refresh/error state
- **Quantitative-trading-grade execution**: Monte Carlo backtest harness, capacity admission with deterministic effort reservations, conservative runtime headroom
- **Closed-loop telemetry**: SONA feedback loop feeds outcomes (latency, success, cost) back to RuVector for continuous MoE ranking improvement

---

## Quick Start

```bash
# Install Python control plane
pipx install verdict-core

# Or with server extras
pipx install 'verdict-core[server]'

# Configure
verdict setup

# Route a task
verdict route "Refactor this Python module to use type hints" --terse
```

---

## OmniRoute Integration

Verdict integrates natively with **OmniRoute** (`http://localhost:20128/v1`) for:
- **3,318+ models** across **250+ providers**
- **107+ free tiers** — no API keys needed
- Auto-fallback, RTK compression (15–95% token savings)
- Smart routing: `auto/best-coding`, `auto/best-reasoning`, `auto/best-fast`

```bash
# Start OmniRoute
docker run -d -p 20128:20128 omnibus/omniroute

# Configure Verdict
export OMNIROUTE_BASE_URL=http://localhost:20128
verdict serve
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VERDICT CORE                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Gate      │  │ Eligibility │  │ Intelligence│              │
│  │  (Policy)   │──▶│  (Filter)   │──▶│  (Ranking)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │               │               │                        │
│         ▼               ▼               ▼                        │
│  ┌─────────────────────────────────────────────────┐             │
│  │          Availability Cache (SWR)                │             │
│  │  TTL + stale-window, explicit unknown/error,     │             │
│  │  isolation by provider/model/policy-version      │             │
│  └─────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Module | Purpose |
|--------|---------|
| `verdict.gate` | Deterministic policy enforcement — capability, budget, privacy, capacity |
| `verdict.eligibility` | Availability-aware filtering with explicit unknown handling |
| `verdict.intelligence` | Advisory ranking (cannot bypass hard gate) |
| `verdict.availability_cache` | Bounded SWR cache, `explain_freshness()` for `/v1/route/explain` |
| `verdict.omniroute` | Native OmniRoute transport (250+ providers, 90+ free tiers) |
| `verdict.contracts` | Versioned Pydantic contracts for all public APIs |

---

## Ecosystem Integration

```
┌────────────────────────────────────────────────────────────────────┐
│                         VERDICT ECOSYSTEM                           │
├──────────────┬──────────────┬──────────────┬──────────────────────┤
│  verdict     │  verdict     │  verdict     │  verdict             │
│  -core       │  -node       │  -cockpit    │  -risk               │
│  (Python)    │  (TypeScript)│  (Next.js)   │  (Python)            │
│  Control     │  Middleware  │  Dashboard   │  Risk Engine         │
│  Plane       │  Express/    │  Visualizer  │  Drawdown/           │
│              │  Next.js     │              │  Position Sizing     │
├──────────────┼──────────────┼──────────────┼──────────────────────┤
│  verdict     │  verdict     │  RuVector    │  Ruflo               │
│  -edge       │  -backtest   │  (Vector DB) │  (Agent Orch)        │
│  (Python)    │  (Python)    │  Semantic    │  Swarms/             │
│  Edge Mining │  Monte Carlo │  Search +    │  Hive Mind           │
│  Framework   │  Harness     │  Graph RAG   │                      │
└──────────────┴──────────────┴──────────────┴──────────────────────┘
```

---

## Documentation

- **Architecture**: [docs/architecture.md](verdict-core/docs/architecture.md)
- **CLI Reference**: [docs/CLI_REFERENCE.md](verdict-core/docs/CLI_REFERENCE.md)
- **API Reference**: [docs/API_REFERENCE.md](verdict-core/docs/API_REFERENCE.md)
- **Configuration**: [docs/CONFIGURATION.md](verdict-core/docs/CONFIGURATION.md)
- **Local Development**: [docs/guides/local-development.md](verdict-core/docs/guides/local-development.md)
- **Production Deployment**: [docs/guides/production-deployment.md](verdict-core/docs/guides/production-deployment.md)
- **Memory System**: [docs/guides/memory-system.md](verdict-core/docs/guides/memory-system.md)

---

## License

MIT — see individual repos for details.

---

## Links

- **Core**: https://github.com/mrnicholasbcarter-code/verdict-core
- **Node**: https://github.com/mrnicholasbcarter-code/verdict-node
- **Cockpit**: https://github.com/verdict/verdict-cockpit
- **Risk**: https://github.com/verdict/verdict-risk
- **Edge**: https://github.com/verdict/verdict-edge
- **Backtest**: https://github.com/verdict/verdict-backtest
- **OmniRoute**: https://github.com/verdict/omniroute
- **RuVector**: https://github.com/ruvnet/ruvector
- **Ruflo**: https://github.com/ruvnet/claude-flow
