# Verdict Ecosystem Compatibility Matrix

> **GENERATED FILE — do not edit by hand.**
> Source of truth: [`compatibility-manifest.json`](../compatibility-manifest.json).
> Regenerate with `python3 scripts/generate_compatibility_matrix.py --write`;
> CI fails if this file drifts from the manifest.

Release train `rel-001-schema-hashes-2026-09-04` · schema `4` · contract `1` · policy `1` · validation scope `local-source-directories` · evidence timestamp `2026-09-26T00:36:22Z`

## Repositories

| Repository | Package | Import | CLI | Version | Publication | Registry | Runtime | Maturity | Support | Evidence date | Release-train pin | Schema hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [verdict-core](https://github.com/mrnicholasbcarter-code/verdict-core) | `verdict-core` | `verdict` | `verdict` | `0.3.0` | published | [registry](https://pypi.org/project/verdict-core/0.3.0/) | python >=3.10 | alpha | experimental | 2026-09-26T00:36:22Z | `d0da31a8f0747a7928f45c57f158cb728559e1ce` | `efd4f3babdb4…` (`verdict/contracts.py`) |
| [verdict-node](https://github.com/mrnicholasbcarter-code/verdict-node) | `@bodanglin/verdict-node` | `@bodanglin/verdict-node` | — | `0.2.0` | published | [registry](https://www.npmjs.com/package/@bodanglin/verdict-node) | node >=18 | alpha | experimental | 2026-09-26T00:36:22Z | `65feea5f62f9d219ddfaffeb0e6b03e31b987e70` | not applicable |
| [verdict-risk](https://github.com/mrnicholasbcarter-code/verdict-risk) | `llm-gate-risk` | `trade_risk_engine` | `verdict-risk-benchmark` | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-20T00:00:00Z | `65477ec4a487d5893c988802e559a823202018e7` | not applicable |
| [verdict-strategy](https://github.com/mrnicholasbcarter-code/verdict-strategy) | `verdict-edge` | `edge_mining_framework` | — | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-18T00:00:00Z | `d393ca0a829658e5b7078ed34dddde2aa9830114` | not applicable |
| [verdict-backtest](https://github.com/mrnicholasbcarter-code/verdict-backtest) | `llm-gate-backtest` | `backtest_harness` | — | `0.1.0` | source-only — no released artifact | **not published** | python >=3.10 | alpha | experimental | 2026-08-20T00:00:00Z | `3c89fb8d4dca086a4ac05e476177243148279a91` | not applicable |
| [verdict-cockpit](https://github.com/mrnicholasbcarter-code/verdict-cockpit) | `verdict-cockpit` | — | — | `0.2.0` | private application — not distributed | **not published** | node unspecified | alpha | experimental | 2026-09-26T01:19:37Z | `d5682d5d1c5beac5400ce47e8d5d38dfd77c15ad` | not applicable |
| [verdict-ecosystem](https://github.com/mrnicholasbcarter-code/verdict-ecosystem) | `verdict-ecosystem` | — | — | `0.1.0` | documentation only — not distributed | **not published** | python unspecified | alpha | experimental | 2026-09-26T00:36:22Z | `ee2e00b97eb1d1da04e3d75a95823288d6a09535` | not applicable |

Rows marked **not published** or **unreleased** have no released artifact; they are validated from pinned local source only.

Schema hash records a SHA-256 digest of the repository's canonical contract source; `scripts/check_compatibility.py` recomputes it against the local checkout on every run and fails on drift. **not applicable** means the repository does not currently own a schema in this contract family.

## Legacy names and migration deadlines

| Repository | Legacy name | Kind | Replacement | Sunset date | Migration |
|---|---|---|---|---|---|
| verdict-risk | `llm-gate-risk` | package | `verdict-risk` | 2026-12-31 | [migration](../docs/COMPATIBILITY_MIGRATION.md#verdict-risk) |
| verdict-risk | `llm-gate-risk-benchmark` | cli | `verdict-risk-benchmark` | 2026-12-31 | [migration](../docs/COMPATIBILITY_MIGRATION.md#verdict-risk) |
| verdict-backtest | `llm-gate-backtest` | package | `verdict-backtest` | 2026-12-31 | [migration](../docs/COMPATIBILITY_MIGRATION.md#verdict-backtest) |

## Deferred checks

| Check | Blocked by |
|---|---|
| `cross-repository-contract-smoke-tests` | https://github.com/mrnicholasbcarter-code/verdict-node/issues/31 |

## Migration and rollback

- Migration guide: [COMPATIBILITY_MIGRATION.md](../docs/COMPATIBILITY_MIGRATION.md)
- Rollback guide: [COMPATIBILITY_ROLLBACK.md](../docs/COMPATIBILITY_ROLLBACK.md)
