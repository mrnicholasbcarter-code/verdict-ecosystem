# Nicholas Carter

**Senior Software Engineer | Python · TypeScript · Real-Time Systems**
North Port, FL (Remote) · [linkedin.com/in/nicholas-carter-dev](https://linkedin.com/in/nicholas-carter-dev)

I independently design and ship production systems — from a 57,000-line algorithmic
trading platform with sub-second WebSocket execution to LLM routing middleware that
dynamically dispatches work across 15+ model providers with tier-based criticality gates.

## Portfolio

A set of cleanly extractable, production-grade libraries that showcase specific engineering skills.

| Repo | What it is |
|------|------------|
| [**llm-gate**](https://github.com/mrnicholasbcarter-code/llm-gate) | AI criticality router. Mathematically prevents expensive models (Opus) from doing cheap formatting work — saves ~60% API cost. |
| [**llm-gate-node**](https://github.com/mrnicholasbcarter-code/llm-gate-node) | TypeScript/Express equivalent of the router with strict `Zod` schemas. Proves enterprise backend-JS competence. |
| [**trading-cockpit-ui**](https://github.com/mrnicholasbcarter-code/trading-cockpit-ui) | Next.js dashboard using `Zustand` to surgically render WebSockets at 60fps. |
| [**prediction-market-sdk**](https://github.com/mrnicholasbcarter-code/prediction-market-sdk) | HFT Python SDK using zero-copy `msgspec` structs for Kalshi + Polymarket. |
| [**trade-risk-engine**](https://github.com/mrnicholasbcarter-code/trade-risk-engine) | Pure-functional drawdown / circuit-breaker engine with a sub-millisecond kill-switch. |
| [**edge-mining-framework**](https://github.com/mrnicholasbcarter-code/edge-mining-framework) | YAML-driven evaluation harness accounting for brutal exchange fee-ceilings. |
| [**backtest-harness**](https://github.com/mrnicholasbcarter-code/backtest-harness) | High-fidelity Monte Carlo simulation engine with tick replay. |

## Core Competencies

- **Languages:** Python 3.11+, TypeScript/JavaScript (ES2022+), C#/.NET, Java, Rust (learning), SQL
- **Real-Time:** asyncio, WebSockets, event-driven architecture, sub-second order execution
- **Data/ML:** pandas, numpy, scipy, Monte Carlo, Kelly criterion, Wang Transform
- **APIs:** REST, WebSocket, RSA-PSS auth, OAuth2/OIDC, rate limiting, OpenAPI
- **Infra:** SQLite (WAL), systemd, Linux admin, Docker, Azure
- **AI/LLM:** Multi-provider routing (15+ providers), Claude Code, 9router integration

## Highlights

- 57,000 lines of production Python across 130+ modules
- 6 production bot versions (v35–v60), 3 running as systemd services
- 30+ integrated data sources (Binance, Deribit, Polymarket, economic calendars, news APIs)
- Risk system caught and prevented a $1,163 category loss from repeating
