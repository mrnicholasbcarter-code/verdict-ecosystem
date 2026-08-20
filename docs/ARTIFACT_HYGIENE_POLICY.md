# Artifact Hygiene Policy

Defines how artifacts across the Verdict Portfolio are classified, how the
secret/PII scan behaves, and the only approved cleanup procedure. This
policy documents a **dry-run-first, human-approved** process. No automation
in this repository deletes anything.

## Classification (issue ECO-003)

| Class | Definition | Handling |
|---|---|---|
| 1. Tracked product/source | Committed files that ship as part of the repository | Normal review/merge process |
| 2. Stable published evidence/fixture | Committed, reproducible evidence (benchmarks, receipts, reports) | Must be reproducible from source; never silently overwritten by test/demo runs |
| 3. Ignored runtime state | Untracked, covered by `.gitignore` | Safe to regenerate or delete; not part of any release |
| 4. Temporary output | Build/test byproducts not yet covered by `.gitignore` | Should be added to `.gitignore`; treated as class 3 once covered |
| 5. User-owned uncommitted work | Untracked or modified files representing in-progress work | Never touched by automation, cleanup scripts, or agents without the owner's explicit action |
| 6. Secret/PII requiring quarantine | Anything matching a secret/PII pattern | Never printed, logged, or committed; reported by path and rule name only |

Ignore rules are added only after a human or agent review confirms a
matched path is genuinely class 3/4 and not class 1, 2, or 5. This policy
does not authorize blanket `.gitignore` additions — see the sibling-repo
proposal table in `ARTIFACT_INVENTORY.md`, which are recommendations, not
applied changes.

## Secret/PII scan

`scripts/secret_scan.py`:

- Accepts one or more repository root paths as arguments (default: the
  current repository).
- **Refuses to scan `~/.omniroute` or `~/.claude` (or anything inside
  them), and refuses any target that is not itself a directory git
  recognizes as a repository** (`git rev-parse --git-dir` must succeed in
  it). The deny-list is checked first and is absolute, so it structurally
  cannot reach `~/.omniroute/.env` or `~/.claude/.credentials.json`
  regardless of how the path is spelled or symlinked. The containment
  check has no hard-coded workspace path, so the same script runs
  unchanged both locally (`/home/<user>/dev/verdict-*`) and in CI
  (`/home/runner/work/...`).
- Walks only files known to git (`git ls-files` plus
  `git ls-files --others --exclude-standard`), so it never descends into
  already-ignored runtime directories (class 3) or `.git/` internals.
- Matches file **contents** against a fixed set of named rules (AWS-style
  access keys, generic `api_key`/`secret`/`token` assignment patterns,
  PEM/SSH private key headers, bearer tokens). Rule names are stable
  identifiers, not descriptions of what was found.
- Reports **path + rule name only**. It never prints, logs, or returns the
  matched substring, the surrounding line, or any other file content. A
  finding is a policy failure regardless of whether the matched value
  turns out to be a real secret or a placeholder — false positives are
  resolved by narrowing the rule, not by disabling the report.
- Exits non-zero if any match is found, so it can gate CI or a manual
  pre-publish step.

Running it locally against a sibling repository is read-only and requires
no write access:

```bash
python3 scripts/secret_scan.py ../verdict-node
```

### What this scan does not do (documented limitation, not silently implied)

It is filename/content-pattern based, not an entropy analyzer or a
provider-specific credential validator. It reduces risk; it does not
prove the absence of secrets. Acceptance criterion "Secret/PII scan runs
before publishing artifacts and blocks unsafe output" is satisfied for
this repository's own CI (see below) and for manual local runs against
sibling repositories. It is not wired into any sibling repository's own
CI, because this audit has read-only access to those repositories.

### Blocking behaviour is tested, not assumed

`tests/test_secret_scan.py` proves the gate blocks rather than merely
reports: one synthetic fixture per rule asserts a non-zero exit, a clean
fixture asserts exit 0, and an unscannable target asserts exit 2 — an
unreachable path must never be reported as a clean pass. The tests also
assert the negative-disclosure guarantee, checking that the matched
string never appears anywhere in the emitted report.

Unsafe fixtures are synthesized into throwaway git repositories under the
OS temp directory at run time. No secret-shaped string is committed to
this repository, which would otherwise make `drift-check` fail on its own
test suite; for the same reason the sample values in that module are
assembled by concatenation, so no single line matches a scanner rule.

## Stable published evidence fixtures (class 2)

Class-2 artifacts live in `evidence/` and are the only committed files in
this repository that are *generated*. Two properties are enforced, not
merely asserted:

**Reproducible.** Every fixture is a pure function of committed source —
today, `compatibility-manifest.json` alone. The generator
(`scripts/build_evidence.py`) reads no clock, no environment, no absolute
path, and never probes the filesystem for sibling repositories. Machine-
local fields such as `path` are projected out, precisely because a fixture
containing one developer's `/home/<user>/dev/...` could not be regenerated
byte-identically anywhere else. `evidence/EVIDENCE_MANIFEST.json` records
the SHA-256 of each fixture *and* of the source it was derived from, so
provenance is checkable without trusting the commit that introduced it.

**Not overwritten by tests or demos.** The generator writes only under an
explicit `--write` flag; its default mode is a read-only `--check` that
regenerates in memory and diffs. Any caller that runs it without
arguments — CI, a test, a demo, an agent — is structurally unable to
mutate `evidence/`. `tests/test_evidence_fixture.py` asserts this
directly: it snapshots the digests of `evidence/`, runs the fixture test
suite, and fails if any digest moved.

To change a fixture you must change its source and regenerate:

```bash
python3 scripts/build_evidence.py --write
```

A stale or hand-edited fixture fails CI with the exact path and both
digests. Hand-editing a file under `evidence/` is never correct — the
regeneration check will revert the meaning of the edit at the next build.

## CI drift check

Sibling repositories are checked out fresh in `.github/workflows/*` and
therefore never contain local untracked artifacts by construction —
"detect drift in sibling repos" would be vacuously true in CI and would
not actually test anything. The check that CI *can* meaningfully enforce
is scoped to this repository: after running the compatibility checker and
secret scan against the `verdict-ecosystem` checkout itself, `git status
--porcelain` must be empty. Any script in this repository that writes a
file it forgets to declare as generated/ignored, or that leaves behind a
stray output, fails the build with the exact modified/untracked paths
`git status --porcelain` reports. See the `drift-check` job in
`.github/workflows/ci.yml`.

Local, cross-repository drift detection (comparing sibling repos' working
trees against a known-clean baseline) remains a manual procedure — run
`scripts/inventory_check.py <repo-path>` locally; it is not part of the
automated CI gate because CI does not have access to developer working
trees.

## Dry-run cleanup procedure (documentation only — no execution tooling shipped)

This repository does not ship a script that deletes files. The approved
procedure, to be run manually by a repository owner:

1. **Inventory.** Run `git status --porcelain=2 --branch` and
   `git ls-files --others --exclude-standard` in the target repository.
   Classify every untracked/modified path using the table above.
2. **Dry run.** List candidate deletions (class 3/4 only) without
   deleting anything, e.g. `git clean -ndx` (the `-n`/dry-run flag is
   mandatory; never pass `-f` in this step). Review the output against
   the classification from step 1. Anything not confidently class 3 or 4
   is excluded.
3. **Explicit approval.** A human owner of that repository reviews the
   dry-run list and explicitly approves it (e.g. by signing off on a PR
   comment or a checklist). No agent or automation may self-approve this
   step.
4. **Execution, scoped.** Only after approval, the owner runs the
   narrowest possible command against the approved paths (e.g.
   `git clean -dx -- <approved-path>` or manual `rm` of the specific
   approved paths) — never a blanket `git clean -fdx` across an entire
   working tree, and never against a path classified as 1, 2, 5, or 6.
5. **Record.** Note what was removed, by whom, and when, in the
   requesting issue or PR.

This procedure is intentionally manual at step 3 and step 4. Automating
approval or execution is out of scope for this change and is not
recommended until there is a track record of the classification step
being reliable across repositories.
