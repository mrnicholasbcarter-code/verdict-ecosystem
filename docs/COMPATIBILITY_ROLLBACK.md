# Compatibility Rollback

Rollback restores the last accepted set of exact source pins and metadata. It
must not be represented as released-artifact rollback: the current validator
checks local source directories only.

## Rollback procedure

1. Identify the last merged manifest revision whose local checker and required
   repository test commands passed.
2. Revert the manifest and compatibility documentation changes through a normal
   pull request. Do not rewrite shared Git history or move published tags.
3. Check out every local repository at the restored `release_train_pin`.
4. Run `python3 scripts/check_compatibility.py` from `verdict-ecosystem` and run
   each restored entry's `test_command` in its repository.
5. Keep release publication separately gated. If any registry artifact was
   already published, use that registry's non-destructive deprecation or
   yanking process; never assume a Git revert removes a package.
6. Record why the candidate train was rejected and keep schema/hash or contract
   claims open unless independent evidence proves them.

The current rollback cannot verify schema hashes or cross-repository contract
behavior. Those checks remain deferred to
[`verdict-core#220`](https://github.com/mrnicholasbcarter-code/verdict-core/issues/220)
and [`verdict-node#31`](https://github.com/mrnicholasbcarter-code/verdict-node/issues/31).

## verdict-core

Restore the previous Core commit pin and the matching policy/version metadata.
Roll back the manifest from published `verdict-core 0.2.0` to the previous
pinned source state only after recording a replacement compatibility receipt.

## verdict-node

Restore the previous Node commit pin and package metadata. Do not publish or
unpublish npm versions as part of a source-manifest rollback.

## verdict-risk

Restore the previous Risk pin and retain the explicit `trade_risk_engine`
import plus canonical benchmark CLI mapping.

## verdict-strategy

Restore the previous Strategy pin while preserving the documented
`verdict-strategy` repository to `verdict-edge` distribution mapping.

## verdict-backtest

Restore the previous Backtest pin and `backtest_harness` import mapping.

## verdict-cockpit

Restore the previous private-application pin. Do not introduce a registry
claim as part of rollback.

## verdict-ecosystem

Revert the ecosystem manifest and its migration/rollback documentation through
a reviewed commit, then rerun the local checker from that exact source state.
