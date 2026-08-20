# Compatibility Migration

This guide applies to the source pins in `compatibility-manifest.json`. The
checker resolves local repository directories; it does not install or validate
released artifacts. Schema hashes and cross-repository contract smoke tests are
not part of this partial REL-001 gate. They remain blocked by
[`verdict-core#220`](https://github.com/mrnicholasbcarter-code/verdict-core/issues/220)
and [`verdict-node#31`](https://github.com/mrnicholasbcarter-code/verdict-node/issues/31).

## Before changing a pin

1. Create clean local checkouts for all seven repositories at the manifest pins.
2. Confirm the repository, package, import, CLI, runtime, provider, maturity, and
   support metadata against the pinned source.
3. Update only the repository entries whose evidence changed, and set their
   evidence timestamps to the observation time.
4. Run `python3 scripts/check_compatibility.py` from `verdict-ecosystem`.
5. Run each entry's `test_command` in that entry's local directory before
   proposing a release-train update.
6. Record any source/package naming difference rather than hiding it with an
   unsupported alias.

A successful checker run proves that the manifest is structurally valid and
that its local directories exist. It does not prove registry publication,
artifact integrity, schema compatibility, or cross-repository behavior.
Registry publication and link integrity are verified separately by the
`released-artifacts` CI job (`scripts/verify_links.py` and
`scripts/consumer_smoke.py`), which installs each published artifact in an
isolated consumer project and marks unreleased entries as skipped.

## verdict-core

Use the `verdict` Python import and `verdict` CLI. The manifest records source
package version `0.1.0`. No registry artifact was verified as corresponding to
this source distribution and release-train pin.

## verdict-node

Use the `@bodanglin/verdict-node` npm package on Node 18 or newer. The recorded
version is published, but migrate by source pin until released-artifact
validation is added. OmniRoute compatibility describes the adapter transport;
it does not transfer policy authority from Verdict Core.

## verdict-risk

Use the `trade_risk_engine` Python import. The primary CLI is
`verdict-risk-benchmark`; the legacy `llm-gate-risk-benchmark` alias remains in
source but is not the canonical manifest name. The legacy `llm-gate-risk`
package name and the `llm-gate-risk-benchmark` CLI alias are recorded in the
manifest with a sunset date of 2026-12-31; migrate to `verdict-risk` and
`verdict-risk-benchmark` before that date. No published registry artifact
was verified for this release train.

## verdict-strategy

The repository remains `verdict-strategy`, while its source distribution is
`verdict-edge` and its Python import is `edge_mining_framework`. Preserve that
explicit mapping during migration. No published registry artifact was verified.

## verdict-backtest

Use the `backtest_harness` Python import from the `llm-gate-backtest` source
distribution. The legacy `llm-gate-backtest` package name is recorded in the
manifest with a sunset date of 2026-12-31; migrate to `verdict-backtest`
before that date. No canonical CLI or published registry artifact was
verified.

## verdict-cockpit

Treat Cockpit as a private application, not a public package. It has no public
registry URL, import name, CLI name, or declared Node engine in this release
train. Validate it against the pinned Verdict Core API source.

## verdict-ecosystem

Treat this repository as compatibility metadata and documentation, not a
released package. Run the local checker from its pinned source directory.
