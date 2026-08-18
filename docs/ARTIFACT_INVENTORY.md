# Cross-Repository Artifact Inventory

Snapshot date: 2026-08-18. Source: read-only `git status`/`git ls-files`
inspection of each repository's local checkout under `/home/nick/dev`. This
is a point-in-time local audit, not a continuously enforced check — see
`ARTIFACT_HYGIENE_POLICY.md` for the CI-enforceable subset.

## Scope

Covers the seven Verdict Portfolio repositories named in
`compatibility-manifest.json`: `verdict-core`, `verdict-node`,
`verdict-cockpit`, `verdict-risk`, `verdict-strategy`, `verdict-backtest`,
and `verdict-ecosystem` itself.

`verdict-core` is registered locally as a **bare repository** at
`/home/nick/dev/verdict-core` (`git rev-parse --is-bare-repository` →
`true`, no `core.worktree` set). It has no working tree of its own, so
tracked/untracked/modified counts do not apply to that path. Actual
development happens across roughly 60 separate `git worktree` checkouts
(e.g. `/home/nick/dev/verdict-core-memory`, `.claude/worktrees/agent-*`,
`/home/nick/dev/verdict-core-worktrees/*`). Auditing every worktree
individually is out of scope for this inventory — it would require write
access and repository-specific context this audit does not have — and is
listed here as a follow-up recommendation, not a completed item.

## Classification legend

Per issue ECO-003's design section:

1. **Tracked product/source** — committed files that are part of the
   shipped repository.
2. **Stable published evidence/fixture** — committed, reproducible
   evidence artifacts (none currently exist in any audited repository).
3. **Ignored runtime state** — untracked but covered by `.gitignore`;
   safe to regenerate or discard.
4. **Temporary output** — build/test byproducts that should be ignored
   but currently are not.
5. **User-owned uncommitted work** — untracked or modified files that
   represent in-progress work and must never be touched by automation.
6. **Secret/PII requiring quarantine** — anything matching a secret
   pattern; never printed or committed, reported by path + rule name only.

## Per-repository findings

| Repository | Branch | Tracked | Untracked | Modified | Has `.gitignore` | Notes |
|---|---|---|---|---|---|---|
| verdict-core | n/a (bare) | n/a | n/a | n/a | yes (on `main`) | Bare repo, no top-level working tree; ~60 worktrees hold actual work (class 1/5 mixed, not audited here) |
| verdict-node | `feat/con-001-compat-declare` | 57 | 16 | 1 | yes | See untracked breakdown below |
| verdict-cockpit | `master` | 23 | 0 | 0 | yes | Clean tree |
| verdict-risk | `feat/con-001-compat-declare` | 47 | 0 | 0 | yes | Clean tree |
| verdict-strategy | `feat/con-001-compat-declare` | 36 | 1 | 0 | yes | `uv.lock` untracked (class 5 — lockfile, likely intentional/pending commit, not a hygiene issue) |
| verdict-backtest | `feat/con-001-compat-declare` | 43 | 2 | 0 | yes | `.claude-flow/`, `.hive-mind/` untracked (class 3 candidate — see hygiene policy) |
| verdict-ecosystem | (this repo) | — | — | — | **no** (fixed by this change) | `.portfolio-state/` was untracked and not ignored; see below |

### verdict-node untracked files (class 3/4 candidates, not yet ignored)

```
.agents/
.claude-flow/
.claude/
.mcp.json
.pi/
.ruvector/
.verdict/adaptive_state/
.verdict/codex-watch.json
.verdict/memory-manifest.json
.verdict/memory.db
.verdict/memory.db.semantic.json
.verdict/memory.ruvector
.verdict/personal.ruvector
.verdict/session-watch.json
CLAUDE.md
evidence/
```

`.verdict/` here is *this repository's own* local coordination/runtime
directory (agent memory, watch state) — distinct from the `verdict-core`
Python package's `verdict/` module. All entries above are agent/tooling
runtime state or local instruction files (class 3), not product source and
not currently secret-bearing by filename. `evidence/` is untracked and
empty of any committed, reproducible fixture, so it does not yet satisfy
the "stable published evidence" class.

One tracked file is locally modified: `README.md` (class 5 — user-owned
in-progress edit; left untouched, not inspected further per the read-only
constraint on sibling repositories).

### verdict-ecosystem: `.portfolio-state/`

The coordinator's working assumption was that `.portfolio-state/` is
already git-ignored. It is not: `git check-ignore .portfolio-state` exits
1 (not ignored) and this repository had no `.gitignore` file at all before
this change. `.portfolio-state/CHECKPOINT.md` is coordinator runtime
checkpoint state (class 3). This change adds a `.gitignore` entry for it;
the directory and its contents are left untouched — no deletion, no
content read beyond a directory listing.

## Secret/PII scan result

`scripts/secret_scan.py` was run read-only against each repository root
listed above. It refuses `~/.omniroute` and `~/.claude` outright (verified
directly against `/home/nick/.omniroute`, which is correctly rejected with
exit code 2) and refuses any target that is not itself a git repository —
so it structurally cannot open `/home/nick/.omniroute/.env` or
`/home/nick/.claude/.credentials.json`. See `ARTIFACT_HYGIENE_POLICY.md`
for the tool's rule set and output contract (path + rule name only,
content never printed or logged).

`verdict-cockpit`, `verdict-risk`, `verdict-strategy`, and
`verdict-backtest` returned no matches. `verdict-node` returned 6 matches,
all against the `generic-secret-assignment` rule, all in test fixtures and
agent-skill documentation (paths only, per the tool's contract — content
was not inspected or recorded):

```
tests/middleware/forwarder.test.ts
tests/router.test.ts
.claude/agents/flow-nexus/authentication.md
.claude/agents/sparc/refinement.md
.claude/agents/testing/production-validator.md
.claude/skills/flow-nexus-platform/SKILL.md
```

These are consistent with documentation/test-fixture placeholder patterns
(auth test doubles, example API-usage docs) rather than committed
credentials, but this audit did not open the matched lines to confirm —
that determination is left to the `verdict-node` owners, per the
read-only constraint on sibling repositories. Reported here as findings
requiring owner review, not as confirmed secrets.

## Sibling-repository `.gitignore` proposals (proposals only — not applied)

These are recommendations for the owning teams. This audit has read-only
access to sibling repositories and has not modified any of them.

| Repository | Proposed rule | Justification |
|---|---|---|
| verdict-node | `.agents/` | Local agent/tooling scaffolding, matches the pattern already ignored in `verdict-strategy`'s `.gitignore` |
| verdict-node | `.claude/` | Local Claude Code project state, same as above |
| verdict-node | `.claude-flow/` (whole directory, not just `data/`/`logs/`) | Current rule only covers two subdirectories; other `.claude-flow/*` runtime files remain untracked |
| verdict-node | `.mcp.json` | Local MCP server configuration, environment-specific |
| verdict-node | `.pi/`, `.ruvector/` | Local tooling/vector-store runtime state |
| verdict-node | `.verdict/` | Local agent memory/session-watch runtime state (distinct from any product directory of the same name) |
| verdict-node | `CLAUDE.md` | Already ignored in `verdict-strategy`; local instruction file, not product source |
| verdict-node | `evidence/` | Currently untracked and empty of committed fixtures; ignoring it (or documenting it as an explicit tracked evidence directory) avoids ambiguity about whether it is class 2 or class 4 |
| verdict-backtest | `.claude-flow/` | Untracked local tooling runtime state, same as verdict-node |
| verdict-backtest | `.hive-mind/` | Untracked local swarm/coordination runtime state |
| verdict-risk | `.agents/`, `.claude/`, `.claude-flow/` | No current rule for these; tree is clean today but the pattern is missing compared to `verdict-strategy`, so a future checkout could accumulate the same untracked sprawl seen in `verdict-node` |

## Not covered by this audit (explicitly out of scope)

- The ~60 `verdict-core` worktrees beyond the bare repository root.
- Any repository not listed in `compatibility-manifest.json`.
- Content of `/home/nick/.omniroute/.env` and
  `/home/nick/.claude/.credentials.json` — never opened, per instruction.
