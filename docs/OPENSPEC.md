# OpenSpec Integration for Verdict

**Status:** Active  
**Owner:** [`verdict-ecosystem`](../README.md)  
**Linear owner:** [BOD-204](https://linear.app/bodanglin/issue/BOD-204)  
**Schema version:** verdict-change-v1  
**OpenSpec version:** 1.13.2 (pinned)

## Overview

Verdict V2 uses OpenSpec with a custom `verdict-change-v1` schema as the executable
significant-change contract. This schema preserves all required fields from BOD-167
Spec Kit Lite while leveraging OpenSpec's proposal → specs → design → tasks lifecycle
and tooling.

OpenSpec replaces manual Spec Kit Lite workflow for NEW significant changes. Historical
`docs/SPEC_KIT_LITE.md`, `specs/`, `.specify/`, and ADR files remain as evidence and
are not mass-migrated.

## Authority Boundaries

OpenSpec adoption preserves clear authority boundaries:

| Authority | Responsibility |
|-----------|---------------|
| **Linear** | Planning, priority, work state, dependencies |
| **OpenSpec** | Change contract structure, artifacts (proposal/specs/design/tasks) |
| **Git/GitHub** | Source truth, pull requests, merge, history |
| **Verdict** | Plan admission, execution, verification, review, receipt, certification |
| **Prime Agent** | Execution harness (NOT an OpenSpec authority) |

**Critical:** OpenSpec is a contract format, not a planning or execution authority.
Linear remains the source of truth for work ownership and state. Git/GitHub remains
the source of truth for code and merge decisions. Verdict remains the authority for
admission, verification, and certification.

## Significant-Change Triggers

Create a verdict-change-v1 OpenSpec change when work affects one or more of:

- **Public behavior** — commands, configuration, packages, documentation claims
- **Architecture** — structure, patterns, or Architecture Decision Records (ADRs)
- **Cross-repository contracts** — APIs, schemas, receipts, compatibility, versions
- **Security/trust** — input trust, credentials, privacy, authorization, protected effects
- **Routing/context/memory** — admission, model selection, context budget, memory semantics
- **Persistence/migration** — data models, migration, rollback, deployment, release
- **Benchmark/claims** — performance, cost, quality, or other public evidence claims
- **Multi-repository** — changes spanning more than one repository

## Exemptions

These changes MAY use ordinary issue/PR workflow without OpenSpec ceremony:

- **Typo-only documentation** — fixing spelling/grammar with no claim changes
- **Small local refactors** — internal renames, formatting, or structure with no behavior change
- **Mechanical formatting** — linting, whitespace, or style-only changes

**When in doubt, use OpenSpec.** The significant-change trigger list is inclusive; the
exemptions are narrow.

## BOD-167 Field Mapping to verdict-change-v1

OpenSpec verdict-change-v1 preserves all 14 BOD-167 Spec Kit Lite required fields
across its artifacts:

| BOD-167 Field | verdict-change-v1 Location |
|---------------|---------------------------|
| 1. Problem / desired outcome | proposal.md: ## Why, ## What Changes |
| 2. Evidence boundary (KNOWN/INFERRED/NOT AVAILABLE) | proposal.md: inline labels |
| 3. Scope | proposal.md: ## Capabilities (new/modified), ## Impact |
| 4. Non-goals | proposal.md: ## What Changes (exclusions), design.md: ## Goals / Non-Goals |
| 5. Acceptance criteria | proposal.md: ## Acceptance criteria |
| 6. Affected interfaces/contracts | spec.md: requirements, design.md: ## Decisions |
| 7. Implementation constraints | design.md: ## Context, ## Decisions |
| 8. Security/trust implications | design.md: ## Decisions, ## Risks / Trade-offs |
| 9. Routing/context/memory implications | design.md: ## Decisions, ## Risks / Trade-offs |
| 10. Test/proof requirements | tasks.md: verification per task |
| 11. ADR impact | design.md: ## ADR impact (documented in Decisions or Risks) |
| 12. Documentation impact | tasks.md: task group with docs updates |
| 13. Migration/rollback | design.md: ## Migration Plan (in Decisions or separate) |
| 14. Evidence required for completion | tasks.md: verification per task + PR/CI binding |

Every BOD-167 field is either directly present in a verdict-change-v1 artifact or
explicitly mapped to an equivalent section. No required field is lost.

## verdict-change-v1 Artifacts

A conforming verdict-change-v1 change contains:

### 1. proposal.md

**Purpose:** Establish WHY the change is needed and WHAT will change.

**Required sections:**
- `## Why` — motivation, problem, opportunity (1-2 sentences)
- `## What Changes` — bullet list of changes, mark **BREAKING** where applicable
- `## Capabilities` — new or modified capability paths (maps to specs)
- `## Impact` — affected code, APIs, dependencies, systems
- Evidence boundary labels: `KNOWN:`, `INFERRED:`, `NOT AVAILABLE:` inline where applicable
- `## Acceptance criteria` — verifiable outcomes (not just PR state)

### 2. specs/\<capability-path\>/spec.md

**Purpose:** Define observable behavioral requirements (the WHAT, not the HOW).

**Required sections:**
- `# Spec Delta` — header
- `## Purpose` — (new capabilities only) what this capability is for
- `## ADDED Requirements` / `## MODIFIED Requirements` / `## REMOVED Requirements` — as applicable
- Each requirement: `### Requirement: <name>` with description
- Requirements use `SHALL` or `MUST` for normative statements
- Each requirement MUST have at least one scenario
- Scenarios use `#### Scenario: <name>` with `WHEN` / `THEN` format

**Spec files:**
- One spec file per capability listed in proposal
- New capabilities: `specs/<capability-path>/spec.md`
- Modified capabilities: delta at same path, will update main spec at archive time
- Changes with no spec-level behavior change set `skip_specs: true` in `.openspec.yaml`

### 3. design.md

**Purpose:** Explain HOW to implement (technical approach, not line-by-line details).

**Required sections:**
- `## Context` — current state and constraints (reference proposal for motivation)
- `## Goals / Non-Goals` — design-level boundaries
- `## Decisions` — key technical choices with rationale, alternatives considered
- `## Risks / Trade-offs` — limitations, mitigations

**Additional sections (when applicable):**
- ADR impact (document in Decisions or Risks)
- Migration/rollback plan (in Decisions or separate section)
- Security/trust implications (in Decisions or Risks)
- Routing/context/memory implications (in Decisions or Risks)
- Open questions (genuinely deferrable unknowns only)

### 4. tasks.md

**Purpose:** Break down implementation into trackable, verifiable units.

**Required sections:**
- `# Tasks` — header
- `## 1. <Group Name>` — numbered task groups
- `- [ ] X.Y Task description with verification method`

**Task requirements:**
- Each task MUST state how to verify completion (test, command, behavior, artifact)
- Tasks ordered by dependency
- Each group MUST include its own tests and documentation (no final cleanup phase)
- Repository/write ownership documented where non-obvious

### 5. .openspec.yaml (optional)

Set `skip_specs: true` only when no spec-level behavior changes (pure refactor, tooling, docs).

## Commands

All commands use the pinned OpenSpec version and disable telemetry:

```bash
# Set telemetry opt-out (required for every shell session)
export OPENSPEC_TELEMETRY=0

# Initialize OpenSpec (repo-local only, no tool integrations)
npx -y @fission-ai/openspec@1.13.2 init --tools none

# Verify schema (already forked to verdict-change-v1 in this repo)
npx -y @fission-ai/openspec@1.13.2 schema validate verdict-change-v1

# List available schemas
npx -y @fission-ai/openspec@1.13.2 schemas

# Create a new change (interactive)
npx -y @fission-ai/openspec@1.13.2 change new

# Validate a change (OpenSpec built-in)
npx -y @fission-ai/openspec@1.13.2 validate <change-name>

# Validate verdict-change-v1 contract (deterministic, required for admission)
python3 scripts/validate_openspec_change.py openspec/changes/<change-name>

# List all changes
npx -y @fission-ai/openspec@1.13.2 list

# Show a change
npx -y @fission-ai/openspec@1.13.2 show <change-name>

# List main specs
npx -y @fission-ai/openspec@1.13.2 list --specs
```

## Validation

Two validation layers ensure compliance:

### 1. OpenSpec built-in validation

```bash
npx -y @fission-ai/openspec@1.13.2 validate <change-name>
```

Checks schema structure and artifact templates.

### 2. verdict-change-v1 deterministic validator (REQUIRED)

```bash
python3 scripts/validate_openspec_change.py openspec/changes/<change-name>
```

Enforces:
- Required artifacts present (proposal.md, specs/, design.md, tasks.md)
- Required headings in each artifact
- Evidence boundary labels (KNOWN/INFERRED/NOT AVAILABLE) in proposal
- Acceptance criteria section in proposal
- Spec files present unless `skip_specs: true` in `.openspec.yaml`
- Spec Delta header in all spec files

**Exit codes:**
- `0` — valid change
- `1` — invalid change (prints precise reason to stderr)
- `2` — usage error

The deterministic validator is stdlib-only (no external dependencies) and MUST pass
before a change is admitted to Verdict workflow.

## Agent Integration Support (OpenSpec 1.13.2)

OpenSpec 1.13.2 supports these agent tool integrations via `--tools`:

- `amazon-q`, `claude`, `codex`, `cursor`, `devin`, `github-copilot`, `hermes`, and others
- `agents` — vendor-neutral target writing `.agents/skills/`

**Verdict uses:** `--tools none` (repo-local only)

This prevents OpenSpec from writing home directory configs or tool-specific integration
files. All OpenSpec artifacts live under `openspec/` in the repository.

**Verified integrations for verdict-ecosystem:** None (by design, repo-local only)

If future work requires tool integration, use `--tools agents` and review generated
files before committing. NEVER allow OpenSpec to write outside the repository or to
global home directory configs.

## No Mass Migration

**Historical artifacts remain unchanged:**

- `docs/SPEC_KIT_LITE.md` — marked superseded for new changes, not deleted
- `specs/` — historical specifications remain as evidence
- `.specify/` — legacy artifacts remain as evidence
- ADR files — preserved with history, not rewritten

OpenSpec applies to NEW significant changes only. Old artifacts remain valid evidence
and are not migrated, rewritten, or deleted.

## Relationship to Spec Kit Lite

- **BOD-167** established Spec Kit Lite as the canonical V2 change contract
- **BOD-204** operationalizes that contract using OpenSpec tooling
- Spec Kit Lite definition (`docs/SPEC_KIT_LITE.md`) is superseded for new changes but preserved
- All BOD-167 required fields are mapped to verdict-change-v1 artifacts
- Verdict is NOT running Spec Kit Lite and OpenSpec as competing processes

For new significant changes, use OpenSpec verdict-change-v1. Spec Kit Lite remains
historical reference.

## Example: Creating a Change

```bash
# Set telemetry opt-out
export OPENSPEC_TELEMETRY=0

# Create a new change (interactive prompts for name and initial proposal)
npx -y @fission-ai/openspec@1.13.2 change new

# Or create manually:
mkdir -p openspec/changes/my-change
cd openspec/changes/my-change

# Copy templates from openspec/schemas/verdict-change-v1/templates/
cp ../../../schemas/verdict-change-v1/templates/proposal.md .
cp ../../../schemas/verdict-change-v1/templates/design.md .
cp ../../../schemas/verdict-change-v1/templates/tasks.md .

# Create spec for each capability
mkdir -p specs/my-capability
cp ../../../schemas/verdict-change-v1/templates/spec.md specs/my-capability/

# Fill in each artifact

# Validate with both validators
npx -y @fission-ai/openspec@1.13.2 validate my-change
python3 scripts/validate_openspec_change.py openspec/changes/my-change
```

## Testing

Test coverage in `tests/test_openspec_change.py`:

- Valid sample change passes validation
- Malformed fixture fails validation
- Missing artifacts reported individually
- Missing required headings reported individually
- Missing evidence labels reported
- `skip_specs: true` allows changes without specs/

Run tests:

```bash
python3 -m unittest tests.test_openspec_change -v
```

## CI Integration

Verdict CI runs:

1. `python3 scripts/validate_openspec_change.py openspec/changes/<change-name>` — deterministic validator
2. `npx -y @fission-ai/openspec@1.13.2 validate <change-name>` — OpenSpec built-in
3. Standard repo checks (check_local_links, unittest, check_adr_lifecycle, etc.)

All must pass before PR merge.

## Fresh Clone Proof

Before admitting a change to Verdict workflow:

```bash
# Clone the branch into a temporary directory
git clone -b <branch-name> <repo-url> /tmp/verify-change
cd /tmp/verify-change

# Set telemetry opt-out
export OPENSPEC_TELEMETRY=0

# Validate the change
python3 scripts/validate_openspec_change.py openspec/changes/<change-name>

# Record the exact command, output, and head SHA
git rev-parse HEAD
```

Include this proof in the PR description.

## Version Pinning

**OpenSpec version:** 1.13.2 (pinned)

**Rationale:** Pinning ensures reproducibility and prevents breaking changes from
upstream OpenSpec updates.

**Latest published version** (as of 2024-09-24): 1.13.2

**Upgrade path:** Future OpenSpec upgrades require:
1. Test with new version against verdict-change-v1 schema
2. Validate all existing changes still pass
3. Update pin in docs/OPENSPEC.md and all command examples
4. Update CI/validation scripts if needed
5. Create a change using OpenSpec itself to document the upgrade

## References

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [BOD-204](https://linear.app/bodanglin/issue/BOD-204) — Adopt OpenSpec
- [BOD-167](https://linear.app/bodanglin/issue/BOD-167) — Spec Kit Lite contract (source material)
- [docs/SPEC_KIT_LITE.md](./SPEC_KIT_LITE.md) — Historical contract (superseded for new changes)
