# Verdict Ecosystem Compatibility Matrix

> **GENERATED FILE — do not edit by hand.**
> Source of truth: [`compatibility-manifest.json`](../compatibility-manifest.json).
> Regenerate with `python3 scripts/generate_compatibility_matrix.py --write`;
> CI fails if this file drifts from the manifest.

Release train `rel-001-partial-2026-08-18` · schema `3` · contract `1` · policy `1` · validation scope `local-source-directories` · evidence timestamp `2026-08-20T00:00:00Z`

## Repositories

| Repository | Package | Import | CLI | Version | Publication | Registry | Runtime | Maturity | Support | Evidence date | Release-train pin |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [verdict-core](https://github.com/mrnicholasbcarter-code/verdict-core) | `verdict-core` | `verdict` | `verdict` | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-18T00:00:00Z | `bc93e455ed4dd7f2c369ff66132b152cfa0da04f` |
| [verdict-node](https://github.com/mrnicholasbcarter-code/verdict-node) | `@bodanglin/verdict-node` | `@bodanglin/verdict-node` | — | `0.1.0` | published | [registry](https://www.npmjs.com/package/@bodanglin/verdict-node) | node >=18 | alpha | experimental | 2026-08-18T00:00:00Z | `48f8189c0e69bd915f1a1dfd7beec7e5e3e05e62` |
| [verdict-risk](https://github.com/mrnicholasbcarter-code/verdict-risk) | `llm-gate-risk` | `trade_risk_engine` | `verdict-risk-benchmark` | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-20T00:00:00Z | `65477ec4a487d5893c988802e559a823202018e7` |
| [verdict-strategy](https://github.com/mrnicholasbcarter-code/verdict-strategy) | `verdict-edge` | `edge_mining_framework` | — | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-18T00:00:00Z | `d393ca0a829658e5b7078ed34dddde2aa9830114` |
| [verdict-backtest](https://github.com/mrnicholasbcarter-code/verdict-backtest) | `llm-gate-backtest` | `backtest_harness` | — | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-20T00:00:00Z | `3c89fb8d4dca086a4ac05e476177243148279a91` |
| [verdict-cockpit](https://github.com/mrnicholasbcarter-code/verdict-cockpit) | `verdict-cockpit` | — | — | `0.1.0` | private application — not distributed | **not published** | node unspecified | alpha | experimental | 2026-08-18T00:00:00Z | `4dbdf403adfbd68f97ed61a10aae64835c0a2e21` |
| [verdict-ecosystem](https://github.com/mrnicholasbcarter-code/verdict-ecosystem) | `verdict-ecosystem` | — | — | **unreleased** | documentation only — not distributed | **not published** | python unspecified | alpha | experimental | 2026-08-18T00:00:00Z | `e0743cea8c9f63a0cd4bbf0d2177ff4c442e03cb` |

Rows marked **not published** or **unreleased** have no released artifact; they are validated from pinned local source only.

## Legacy names and migration deadlines

| Repository | Legacy name | Kind | Replacement | Sunset date | Migration |
|---|---|---|---|---|---|
| verdict-risk | `llm-gate-risk` | package | `verdict-risk` | 2026-12-31 | [migration](../docs/COMPATIBILITY_MIGRATION.md#verdict-risk) |
| verdict-risk | `llm-gate-risk-benchmark` | cli | `verdict-risk-benchmark` | 2026-12-31 | [migration](../docs/COMPATIBILITY_MIGRATION.md#verdict-risk) |
| verdict-backtest | `llm-gate-backtest` | package | `verdict-backtest` | 2026-12-31 | [migration](../docs/COMPATIBILITY_MIGRATION.md#verdict-backtest) |

## Deferred checks

| Check | Blocked by |
|---|---|
| `schema-hashes` | https://github.com/mrnicholasbcarter-code/verdict-core/issues/220 |
| `cross-repository-contract-smoke-tests` | https://github.com/mrnicholasbcarter-code/verdict-node/issues/31 |

## Migration and rollback

- Migration guide: [COMPATIBILITY_MIGRATION.md](../docs/COMPATIBILITY_MIGRATION.md)
- Rollback guide: [COMPATIBILITY_ROLLBACK.md](../docs/COMPATIBILITY_ROLLBACK.md)
