# Verdict Ecosystem — Cross-Repository Coordination

[![Build Status](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/workflows/CI/badge.svg)](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **The coordination layer for the Verdict portfolio.** Ensures all repositories consume compatible contracts, versions, and APIs.

## The Problem

The Verdict portfolio spans 7 repositories across Python and TypeScript. Without coordination:

- Schema drift between Python/TypeScript contracts
- Incompatible major versions deployed together
- No single gate proving cross-repo compatibility
- Release process is manual and error-prone

## The Solution

Verdict Ecosystem provides:

1. **Compatibility Matrix Gate** (CON-001) — CI validates all repos against shared contract fixtures
2. **Versioned Contract Registry** — Single source of truth for schemas, APIs, receipts
3. **Cross-Repo Release Automation** — Coordinated versioning and publishing
4. **Architecture Decision Trail** — ADRs linked to implementation

## Portfolio Repositories

| Repository | Language | Role | Contracts | Status |
|------------|----------|------|-----------|--------|
| [`verdict-core`](https://github.com/mrnicholasbcarter-code/verdict-core) | Python | Control plane / routing | Core contracts, ADRs | ✅ Active |
| [`verdict-node`](https://github.com/mrnicholasbcarter-code/verdict-node) | TypeScript | TS adapter / edge | Core contracts (generated) | ✅ Active |
| [`verdict-risk`](https://github.com/mrnicholasbcarter-code/verdict-risk) | Python | Risk provider | ProviderReceipt v1 | 🚧 In progress |
| [`verdict-strategy`](https://github.com/mrnicholasbcarter-code/verdict-strategy) | Python | Strategy provider | ProviderReceipt v1 | 🚧 In progress |
| [`verdict-backtest`](https://github.com/mrnicholasbcarter-code/verdict-backtest) | Python | Backtest provider | ProviderReceipt v1 | 🚧 In progress |
| [`verdict-cockpit`](https://github.com/mrnicholasbcarter-code/verdict-cockpit) | TypeScript | UI dashboard | Core contracts (generated) | 🚧 In progress |
| **verdict-ecosystem** | — | Coordination | Manifest, CI gates | ✅ This repo |

## Ecosystem Stories (Active)

| ID | Title | Priority | Status | Tracking |
|----|-------|----------|--------|----------|
| **CON-001** | Cross-repo contract & release compatibility gate | P0 | 🚧 In progress | [#17](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/issues/17) |
| **NOD-002** | Enforce Core ExecutionEnvelope at Node edge | P0 | 📋 Planned | [#19](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/issues/19) |
| **CTX-002** | Governed context & memory provider conformance | P1 | 📋 Planned | [#20](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/issues/20) |
| **PRO-001** | Standard provider receipts for risk/strategy/backtest | P1 | 📋 Planned | [#21](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/issues/21) |
| **SWARM-001** | Governed SwarmSpec & supervisor protocol | P1 | 📋 Planned | [#22](https://github.com/mrnicholasbcarter-code/verdict-ecosystem/issues/22) |

## Compatibility Manifest

```json
{
  "schema_version": "1",
  "repositories": [
    {
      "name": "verdict-core",
      "branch": "main",
      "package": "verdict-core",
      "contract_version": "1.0.0",
      "adapter_capabilities": ["routing", "eligibility", "evidence"],
      "test_command": "pytest -x -q",
      "release_status": "active"
    },
    {
      "name": "verdict-node",
      "branch": "main",
      "package": "@bodanglin/verdict-contracts",
      "contract_version": "1.0.0",
      "adapter_capabilities": ["envelope_enforcement", "sse"],
      "test_command": "npm test",
      "release_status": "active"
    }
  ],
  "validation_rules": {
    "schema_drift": "fail",
    "major_version_mismatch": "fail",
    "branch_package_mismatch": "warn"
  }
}
```

## Quick Start

```bash
# Validate compatibility across all repos
python scripts/validate_compatibility.py

# Generate compatibility report
python scripts/generate_matrix.py --output results/compatibility_matrix.json

# Dry-run release
python scripts/dry_run_release.py --version 1.2.0
```

## Architecture Decision Records

| ADR | Title | Status | Repos Affected |
|-----|-------|--------|----------------|
| ADR-021 | Deterministic Provider Receipts | Accepted | core, risk, strategy, backtest |
| ADR-020 | Cross-Repo Compatibility Gate | Proposed | all |
| ADR-019 | Node Envelope Enforcement | Proposed | core, node |
| ADR-018 | Context Provider Conformance | Proposed | core, memory |
| ADR-017 | SwarmSpec Governance | Proposed | core, ruflo |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for cross-repo development workflow.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Part of the Verdict Portfolio** — Built by [Nicholas Carter](https://github.com/mrnicholasbcarter-code)
