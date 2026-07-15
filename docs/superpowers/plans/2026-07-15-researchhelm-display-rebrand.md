# ResearchHelm Display Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the public display brand with ResearchHelm while preserving every existing repository, Skill, plugin, command, path, mode, and protocol identity.

**Architecture:** Treat branding as a presentation contract layered over the unchanged `autoresearch` runtime identity. Add repository-contract assertions first, then update only current display surfaces; historical plans, frozen run artifacts, executable behavior, and the Research Cockpit component remain unchanged.

**Tech Stack:** Markdown, JSON, YAML text metadata, Python `unittest`, existing zero-dependency validation and release-audit scripts.

## Global Constraints

- Public brand: `ResearchHelm`.
- English tagline: `Human-governed research, from resources to audited claims.`
- Chinese tagline: `人主导科研：从现有资源走向可审计结论。`
- Keep `zhangyiCristino/autoresearch-skill`, `autoresearch`, `autoresearch-skill`, `/autoresearch`, `skills/autoresearch/`, and every documented install command exact.
- Keep modes `pi`, `scout`, and `optimize`, all schemas, security boundaries, human gates, and executable behavior unchanged.
- Keep `Research Cockpit` as the component name.
- Do not rewrite historical specifications, plans, experiment records, or frozen public artifacts.
- Do not publish until tests, state validation, and the full release audit pass.

---

### Task 1: Lock the display-brand and compatibility contract

**Files:**
- Modify: `tests/test_repository_contracts.py`
- Test: `tests/test_repository_contracts.py`

**Interfaces:**
- Consumes: current repository display files and the existing exact install-contract constants.
- Produces: a failing-then-passing contract for `ResearchHelm`, its taglines, and the unchanged machine identities.

- [ ] **Step 1: Write the failing display-brand contract**

Change `EXPECTED_OPENAI_YAML` so its display line is:

```python
EXPECTED_OPENAI_YAML = """interface:
  display_name: "ResearchHelm"
  short_description: "Scout, supervise, and audit bounded research"
  default_prompt: "Use $autoresearch in pi mode to turn my resources into decision-ready research options and audited experiments."
policy:
  allow_implicit_invocation: true
"""
```

Add this test to `RepositoryContractTests`:

```python
def test_researchhelm_is_display_only_brand(self):
    english = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    plugin = json.loads(
        (ROOT / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    market = json.loads(
        (ROOT / ".claude-plugin" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )

    self.assertTrue(english.startswith(
        "# ResearchHelm\n\n"
        "**Human-governed research, from resources to audited claims.**"
    ))
    self.assertTrue(chinese.startswith(
        "# ResearchHelm\n\n"
        "**人主导科研：从现有资源走向可审计结论。**"
    ))
    self.assertIn("\n# ResearchHelm\n", skill)
    self.assertIn("ResearchHelm", plugin["description"])
    self.assertIn("ResearchHelm", market["description"])
    self.assertIn("ResearchHelm", market["plugins"][0]["description"])
    self.assertNotIn("# Human-Governed Autoresearch", english + skill)
```

- [ ] **Step 2: Run the contract test and verify RED**

Run:

```powershell
py -m unittest tests.test_repository_contracts.RepositoryContractTests.test_codex_metadata_is_exact_and_dependency_free tests.test_repository_contracts.RepositoryContractTests.test_researchhelm_is_display_only_brand
```

Expected: `FAIL`; `openai.yaml` still contains `Human-Governed Autoresearch`, and current display files do not yet satisfy the ResearchHelm assertions.

- [ ] **Step 3: Confirm unchanged identity tests remain green before editing display files**

Run:

```powershell
py -m unittest tests.test_repository_contracts.RepositoryContractTests.test_claude_identifiers_remain_exact tests.test_repository_contracts.RepositoryContractTests.test_claude_install_commands_and_paths_remain_exact tests.test_legacy_compatibility
```

Expected: `OK`. If this fails, stop because the baseline already violates the compatibility invariant.

---

### Task 2: Apply the display-only rebrand and verify release readiness

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `skills/autoresearch/SKILL.md`
- Modify: `skills/autoresearch/agents/openai.yaml`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Test: `tests/test_repository_contracts.py`

**Interfaces:**
- Consumes: the branding contract introduced in Task 1 and the approved display-copy rules.
- Produces: ResearchHelm-branded public surfaces with byte-for-byte-stable compatibility commands and machine identifiers.

- [ ] **Step 1: Update the README display copy**

In `README.md`:

```markdown
# ResearchHelm

**Human-governed research, from resources to audited claims.**
```

Use `ResearchHelm` for the seven prose references currently written as
`Autoresearch` in the product story, installer disclaimers, portability,
security, and Skill Recommendation sections. Do not alter any backticked
command, URL, path, plugin ID, Skill ID, or lowercase `autoresearch` token.

In `README.zh-CN.md`:

```markdown
# ResearchHelm

**人主导科研：从现有资源走向可审计结论。**
```

Replace the corresponding prose product-name references with `ResearchHelm`.
Keep every command, URL, path, ID, compatibility label, and mode literal exact.

- [ ] **Step 2: Update Skill and client display metadata**

In `skills/autoresearch/SKILL.md`, retain the frontmatter identity and use:

```markdown
---
name: autoresearch
description: Use when a user wants research ideas grounded in available resources, public-work overlap diligence, preregistered human-governed experiments, bounded metric optimization, reproducibility audits, claim-to-artifact evidence control, or approved recommendations for complementary research skills.
---

# ResearchHelm

ResearchHelm turns resources into defensible ideas, human decisions, bounded execution, and audited claims. The human owns scientific decisions.
```

In `skills/autoresearch/agents/openai.yaml`, change only:

```yaml
display_name: "ResearchHelm"
```

Keep `$autoresearch`, the prompt, short description, and invocation policy exact.

- [ ] **Step 3: Update human-readable plugin descriptions**

Use these exact description values while keeping all names, versions, URLs,
keywords, sources, and licenses unchanged.

`.claude-plugin/plugin.json`:

```json
"description": "ResearchHelm is a human-governed research skill for resource-to-idea scouting, supervised bounded experiments, claim auditing, and an offline Research Cockpit."
```

`.claude-plugin/marketplace.json` top-level:

```json
"description": "ResearchHelm supports human-governed research from resource scouting to audited claims, with bounded experiments and an offline Research Cockpit."
```

`.claude-plugin/marketplace.json` plugin entry:

```json
"description": "Use ResearchHelm to scout resource-feasible ideas, supervise Builder-Verifier experiments, and audit claims while preserving the legacy optimize loop."
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
py -m unittest tests.test_repository_contracts tests.test_legacy_compatibility tests.test_skill_contract tests.test_installer_paths
```

Expected: `OK`. The ResearchHelm contract and all legacy identity/install
contracts pass together.

- [ ] **Step 5: Review the exact diff and commit the rebrand**

Run:

```powershell
git diff --check
git diff -- README.md README.zh-CN.md skills/autoresearch/SKILL.md skills/autoresearch/agents/openai.yaml .claude-plugin/plugin.json .claude-plugin/marketplace.json tests/test_repository_contracts.py
```

Expected: only display copy and the matching contract test change; no command,
path, ID, schema, executable, frozen artifact, or historical document changes.

Commit:

```powershell
git add -- README.md README.zh-CN.md skills/autoresearch/SKILL.md skills/autoresearch/agents/openai.yaml .claude-plugin/plugin.json .claude-plugin/marketplace.json tests/test_repository_contracts.py
git commit -m "feat: introduce ResearchHelm display brand"
```

- [ ] **Step 6: Run full verification on the committed tree**

Run:

```powershell
py -m unittest discover -s tests
py skills/autoresearch/scripts/validate_state.py demo/one-gpu-public
py skills/autoresearch/scripts/audit_release.py all --root . --ref HEAD
git status --short --branch
```

Expected:

- all unit tests pass, with only the repository's documented skips;
- state validation returns `{"findings": [], "valid": true}`;
- release audit returns `{"clean": true, "findings": [], "scope": "all"}`;
- the working tree is clean on `human-guided-autoresearch-v2-sanitized`.

Stop after local verification. Remote publication requires a separate explicit
user approval.
