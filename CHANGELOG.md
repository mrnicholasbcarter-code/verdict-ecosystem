# Changelog

All notable changes to verdict-ecosystem are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-09-26

### Added
- **Portfolio hub** (`README.md`): single source of truth for the seven-repository
  Verdict portfolio — links, maturity levels, and release status for every artefact.
- **Compatibility gate** (`compatibility-manifest.json` + `scripts/check_compatibility.py`):
  machine-verifiable manifest of all portfolio repositories with per-row
  `release_train_pin`, `schema_hash`, `publication_status`, and
  `evidence_timestamp`; CI fails closed on any drift.
- **ADR lifecycle index** (`docs/ADR_INDEX.md`): authoritative index of all
  Architecture Decision Records across the portfolio with status, supersession
  chains, and immutable source pins.
- **Docs truth pass** (BOD-193/BOD-204): ecosystem README and all ecosystem
  documentation brought into agreement with ratified evidence; no unverified
  claims published.
- **OpenSpec foundation** (`openspec/`): `verdict-change-v1` schema with
  deterministic validator and section-based integrity checks (BOD-204).
- **Evidence fixtures** (`evidence/`): stable, reproducible evidence artefacts
  with a secret-scan gate enforced in CI.
- **Release-train manifest** (`compatibility-manifest.json`):
  - `verdict-core` pinned to v0.3.0 (`d0da31a8f0747a79`),
    `schema_hash` computed from `verdict/contracts.py`.
  - `verdict-node` updated to v0.2.0 (`65feea5f62f9d219`).
  - `verdict-cockpit` pinned to current master (`53cd186186b87256`);
    will be updated by the controller after the cockpit v0.2.0 merge.
