# ResearchHelm Repository Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the GitHub repository to `zhangyiCristino/researchhelm`, make the new address primary everywhere, and retain exact old-address commands in a dedicated compatibility section.

**Architecture:** Separate the work into a fully testable local address-contract change and a guarded external rename/publication step. The local commit is verified before any GitHub mutation; the external step uses an expected remote SHA and administration/name-availability checks before renaming, then updates `origin`, pushes, and verifies both new and redirected old addresses.

**Tech Stack:** Markdown, JSON, Python `unittest`, Git, GitHub CLI/API, existing state validator and release-security auditor.

## Global Constraints

- New repository: `zhangyiCristino/researchhelm`.
- New web URL: `https://github.com/zhangyiCristino/researchhelm`.
- New clone URL: `https://github.com/zhangyiCristino/researchhelm.git`.
- Keep `autoresearch`, `autoresearch-skill`, `skills/autoresearch/`, `/autoresearch`, and `/plugin install autoresearch@autoresearch-skill` exact.
- Keep exact legacy old-address commands in a dedicated README compatibility section.
- Never claim third-party installers are guaranteed to follow GitHub redirects.
- Keep modes, schemas, human gates, security behavior, executable files, frozen artifacts, and historical plans/specifications unchanged.
- Never print or persist authentication tokens or credential-derived values.
- Do not reuse the old GitHub repository name after the rename.

---

### Task 1: Make the new repository address primary under contract

**Files:**
- Modify: `tests/test_repository_contracts.py`
- Modify: `tests/test_legacy_compatibility.py`
- Modify: `tests/test_installer_paths.py`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `TESTING.md`
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: the approved primary and legacy repository-address contracts.
- Produces: a committed, release-audited tree whose current instructions use `researchhelm` and whose dedicated legacy sections preserve the old commands exactly.

- [ ] **Step 1: Write failing primary/legacy repository tests**

In `tests/test_repository_contracts.py`, replace `CLAUDE_INSTALL_CONTRACT` with:

```python
PRIMARY_REPOSITORY = "zhangyiCristino/researchhelm"
LEGACY_REPOSITORY = "zhangyiCristino/autoresearch-skill"
CLAUDE_INSTALL_CONTRACT = (
    f"/plugin marketplace add {PRIMARY_REPOSITORY}",
    "/plugin install autoresearch@autoresearch-skill",
    f"git clone https://github.com/{PRIMARY_REPOSITORY}.git",
    "cp -r researchhelm/skills/autoresearch ~/.claude/skills/",
)
LEGACY_REDIRECT_CONTRACT = (
    f"/plugin marketplace add {LEGACY_REPOSITORY}",
    f"git clone https://github.com/{LEGACY_REPOSITORY}.git",
    "cp -r autoresearch-skill/skills/autoresearch ~/.claude/skills/",
    f"npx skills add {LEGACY_REPOSITORY} --skill autoresearch",
    f"npx skills use {LEGACY_REPOSITORY}@autoresearch",
)


def markdown_section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end == -1 else text[start:end]
```

Add these methods to `RepositoryContractTests`:

```python
def test_primary_repository_metadata_and_commands_are_exact(self):
    plugin = json.loads(
        (ROOT / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    self.assertEqual(
        "https://github.com/zhangyiCristino/researchhelm",
        plugin["homepage"],
    )
    self.assertEqual(plugin["homepage"], plugin["repository"])
    for name in ("README.md", "README.zh-CN.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        for command in CLAUDE_INSTALL_CONTRACT:
            self.assertEqual(1, text.count(command), f"{name}: {command}")

def test_legacy_repository_commands_live_only_in_redirect_section(self):
    for name in ("README.md", "README.zh-CN.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        section = markdown_section(text, "## Legacy repository redirect")
        for command in LEGACY_REDIRECT_CONTRACT:
            self.assertEqual(1, text.count(command), f"{name}: {command}")
            self.assertIn(command, section)
```

Change `REPOSITORY` in `tests/test_installer_paths.py` to:

```python
REPOSITORY = "zhangyiCristino/researchhelm"
```

In `tests/test_legacy_compatibility.py`, keep the immutable plugin IDs and
`/plugin install` assertions, but change primary `npx skills` expectations to
`zhangyiCristino/researchhelm`. Preserve the old-address assertions in
`test_every_readme_preserves_legacy_commands_and_paths`.

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
py -m unittest tests.test_repository_contracts tests.test_legacy_compatibility tests.test_installer_paths
```

Expected: `FAIL`; the README files, `TESTING.md`, and plugin URL metadata still
use `autoresearch-skill` as the primary repository and have no dedicated legacy
redirect section.

- [ ] **Step 3: Update primary documentation and metadata**

Apply these exact primary replacements in both README files:

```text
zhangyiCristino/autoresearch-skill -> zhangyiCristino/researchhelm
https://github.com/zhangyiCristino/autoresearch-skill.git -> https://github.com/zhangyiCristino/researchhelm.git
cp -r autoresearch-skill/skills/autoresearch ~/.claude/skills/ -> cp -r researchhelm/skills/autoresearch ~/.claude/skills/
```

Update the two maintained installer commands in `TESTING.md` to use
`zhangyiCristino/researchhelm`.

Set both fields in `.claude-plugin/plugin.json` to:

```json
"homepage": "https://github.com/zhangyiCristino/researchhelm",
"repository": "https://github.com/zhangyiCristino/researchhelm"
```

Keep `.claude-plugin/plugin.json` name `autoresearch`, marketplace name
`autoresearch-skill`, and every mode/command identity unchanged.

- [ ] **Step 4: Add exact legacy redirect sections**

Add this section to `README.md` after the primary Claude Code installation
block and before portable-agent instructions:

````markdown
## Legacy repository redirect

GitHub redirects the previous repository location to ResearchHelm for web and Git operations. Update saved URLs to `zhangyiCristino/researchhelm`; third-party installers are not guaranteed to follow GitHub redirects. Do not reuse the old repository name.

```text
/plugin marketplace add zhangyiCristino/autoresearch-skill
git clone https://github.com/zhangyiCristino/autoresearch-skill.git
cp -r autoresearch-skill/skills/autoresearch ~/.claude/skills/
npx skills add zhangyiCristino/autoresearch-skill --skill autoresearch
npx skills use zhangyiCristino/autoresearch-skill@autoresearch
```
````

Add the equivalent section to `README.zh-CN.md` with the heading kept exactly
as `## Legacy repository redirect` so the same contract helper can isolate it:

````markdown
## Legacy repository redirect

GitHub 会把旧仓库位置的网页和 Git 操作重定向到 ResearchHelm。请把保存的地址更新为 `zhangyiCristino/researchhelm`；第三方安装器不保证遵循 GitHub 重定向。不要重新占用旧仓库名。

```text
/plugin marketplace add zhangyiCristino/autoresearch-skill
git clone https://github.com/zhangyiCristino/autoresearch-skill.git
cp -r autoresearch-skill/skills/autoresearch ~/.claude/skills/
npx skills add zhangyiCristino/autoresearch-skill --skill autoresearch
npx skills use zhangyiCristino/autoresearch-skill@autoresearch
```
````

- [ ] **Step 5: Run focused tests and verify GREEN**

Run:

```powershell
py -m unittest tests.test_repository_contracts tests.test_legacy_compatibility tests.test_installer_paths
```

Expected: `OK`, with only existing environment-dependent installer skips.

- [ ] **Step 6: Review, commit, and fully verify the local tree**

Run:

```powershell
git diff --check
git diff -- README.md README.zh-CN.md TESTING.md .claude-plugin/plugin.json tests/test_repository_contracts.py tests/test_legacy_compatibility.py tests/test_installer_paths.py
```

Expected: only primary address changes, exact legacy sections, and matching
contract updates.

Commit:

```powershell
git add -- README.md README.zh-CN.md TESTING.md .claude-plugin/plugin.json tests/test_repository_contracts.py tests/test_legacy_compatibility.py tests/test_installer_paths.py
git commit -m "docs: move ResearchHelm to canonical repository"
```

Run on the committed tree:

```powershell
py -m unittest discover -s tests
py skills/autoresearch/scripts/validate_state.py demo/one-gpu-public
py skills/autoresearch/scripts/audit_release.py all --root . --ref HEAD
git status --short --branch
```

Expected: all tests pass with only documented skips; demo state is valid;
release audit is clean; worktree is clean and local `master` is ahead of
`origin/master` only by the approved unpublished commits.

---

### Task 2: Rename and publish the GitHub repository

**Files:**
- Modify local Git configuration: `origin` URL only
- Modify external state: GitHub repository name and remote `master`

**Interfaces:**
- Consumes: Task 1's clean, committed, release-audited local `master`.
- Produces: public repository `zhangyiCristino/researchhelm`, updated local tracking, and verified old-address Git redirect behavior.

- [ ] **Step 1: Run content-free publication preflight**

Run:

```powershell
gh auth status *> $null
if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication unavailable' }

$repo = gh api repos/zhangyiCristino/autoresearch-skill | ConvertFrom-Json
if (-not $repo.permissions.admin) { throw 'Repository administration unavailable' }

gh api repos/zhangyiCristino/researchhelm *> $null
if ($LASTEXITCODE -eq 0) { throw 'Target repository name is occupied' }

$remote = gh api repos/zhangyiCristino/autoresearch-skill/git/ref/heads/master --jq .object.sha
$tracked = git rev-parse origin/master
if ($remote -ne $tracked) { throw 'Remote tracking reference is stale' }

git merge-base --is-ancestor origin/master master
if ($LASTEXITCODE -ne 0) { throw 'Verified local master is not a descendant of remote master' }

if (git status --porcelain) { throw 'Worktree is not clean' }
```

Expected: no output containing secrets; authenticated admin access is true;
`researchhelm` is absent; remote `master` equals `origin/master`; local master
is a clean descendant.

- [ ] **Step 2: Rename the GitHub repository**

Run:

```powershell
$renamed = gh api --method PATCH repos/zhangyiCristino/autoresearch-skill -f name=researchhelm | ConvertFrom-Json
if ($renamed.full_name -ne 'zhangyiCristino/researchhelm') { throw 'Repository rename did not complete' }
```

Expected: repository full name is exactly `zhangyiCristino/researchhelm`.

- [ ] **Step 3: Update `origin` and push verified commits**

Run:

```powershell
git remote set-url origin https://github.com/zhangyiCristino/researchhelm.git
git push origin master
```

Expected: `master -> master` fast-forward push. If HTTPS transport is reset,
retry once with:

```powershell
git -c http.version=HTTP/1.1 push origin master
```

If both attempts fail, keep the new repository name and verified local commit,
report the transport failure, and stop without rewriting history.

- [ ] **Step 4: Verify new repository and old Git redirect**

Run:

```powershell
$local = git rev-parse HEAD
$new = gh api repos/zhangyiCristino/researchhelm/git/ref/heads/master --jq .object.sha
$oldLine = git ls-remote https://github.com/zhangyiCristino/autoresearch-skill.git refs/heads/master
$old = ($oldLine -split '\s+')[0]
$origin = git remote get-url origin
$repository = gh api repos/zhangyiCristino/researchhelm | ConvertFrom-Json
$redirectedWeb = (Invoke-WebRequest -Uri https://github.com/zhangyiCristino/autoresearch-skill -UseBasicParsing).BaseResponse.ResponseUri.AbsoluteUri.TrimEnd('/')

if ($new -ne $local -or $old -ne $local) { throw 'New repository or old redirect does not resolve to local master' }
if ($origin -ne 'https://github.com/zhangyiCristino/researchhelm.git') { throw 'Origin URL is stale' }
if ($repository.name -ne 'researchhelm' -or $repository.default_branch -ne 'master') { throw 'Repository identity is incorrect' }
if ($redirectedWeb -ne 'https://github.com/zhangyiCristino/researchhelm') { throw 'Old web URL did not redirect' }
```

Then run a content-free metadata check that reports only counts:

```powershell
@'
import json, re, subprocess
repo = "zhangyiCristino/researchhelm"
commits = json.loads(subprocess.check_output(
    ["gh", "api", f"repos/{repo}/commits?sha=master&per_page=100"]
))
authors = {
    (item["commit"]["author"]["name"], item["commit"]["author"]["email"])
    for item in commits
}
messages = "\n".join(item["commit"]["message"] for item in commits)
print("reachable_commits=" + str(len(commits)))
print("unique_authors=" + str(len(authors)))
print("forbidden_commit_metadata=" + str(bool(
    re.search(r"codex|gpt|claude", messages, re.I)
)))
'@ | py -
git status --short --branch
```

Expected: one unique author, no prohibited commit-metadata matches, and local
`master` synchronized with `origin/master`.
