# ResearchHelm Repository Rename Design

## Goal

Rename the public GitHub repository from
`zhangyiCristino/autoresearch-skill` to `zhangyiCristino/researchhelm` so the
repository header matches the approved ResearchHelm brand, while preserving
existing users and all runtime identities.

The repository name is a distribution address, not the Skill identity. The
canonical Skill remains `autoresearch`.

## Public Naming Contract

After the rename, current documentation and metadata use these primary
addresses:

- repository: `zhangyiCristino/researchhelm`;
- web URL: `https://github.com/zhangyiCristino/researchhelm`;
- clone URL: `https://github.com/zhangyiCristino/researchhelm.git`;
- community installer source: `zhangyiCristino/researchhelm`.

The README files present the new addresses in all primary install, try-without-
installing, marketplace-add, and clone examples. `TESTING.md` uses the new
source for maintained compatibility commands. Plugin `homepage` and
`repository` fields also use the new URL.

## Legacy Redirect Contract

Both README files include a short `Legacy repository redirect` section after
the primary installation paths. It records the previous repository address and
the exact legacy commands that existing users may already have stored:

- `/plugin marketplace add zhangyiCristino/autoresearch-skill`;
- `git clone https://github.com/zhangyiCristino/autoresearch-skill.git`;
- `cp -r autoresearch-skill/skills/autoresearch ~/.claude/skills/`;
- `npx skills add zhangyiCristino/autoresearch-skill --skill autoresearch`;
- `npx skills use zhangyiCristino/autoresearch-skill@autoresearch`.

The section states only GitHub's documented behavior: web traffic and Git
clone, fetch, and push operations to the old repository location redirect to
the renamed repository. It also tells users to update saved URLs to the new
location. It does not claim that every third-party installer must follow the
redirect.

The old repository name must not be reused because doing so would remove the
redirect.

## Permanent Compatibility Invariants

The rename must not change:

- Skill ID and directory: `autoresearch` and `skills/autoresearch/`;
- plugin and marketplace IDs: `autoresearch` and `autoresearch-skill`;
- invocation command: `/autoresearch`;
- plugin installation command:
  `/plugin install autoresearch@autoresearch-skill`;
- modes `pi`, `scout`, and `optimize`;
- schemas, state paths, human gates, security boundaries, executable behavior,
  or frozen public artifacts.

Historical specifications, plans, and experiment records remain historical and
are not rewritten. The ResearchHelm display-brand specification and plan also
remain unchanged records of the earlier display-only decision.

## Repository Rename Sequence

1. Add failing repository-contract tests for the new primary address and the
   retained legacy redirect section.
2. Update current documentation, tests, and plugin URL metadata locally.
3. Run focused tests, the complete test suite, state validation, and the full
   release-security audit on the committed local tree.
4. Confirm the worktree is clean, GitHub authentication is valid, the current
   remote `master` equals the locally recorded `origin/master` and is an
   ancestor of the verified local `master`, the target name `researchhelm` is
   not occupied, and the authenticated user has repository administration
   access.
5. Rename the GitHub repository through the GitHub API.
6. Update the local `origin` URL to
   `https://github.com/zhangyiCristino/researchhelm.git`.
7. Push the already-verified documentation commit to the renamed repository.
8. Verify the new repository URL, old web redirect, old Git remote behavior,
   default branch, remote commit identity, single-author history, and clean
   local tracking state.

This repository does not contain an `action.yml`, `action.yaml`, or a Pages
`CNAME`, so the known GitHub Actions and project-site rename exceptions do not
apply to the current tree. Existing CI workflow files remain unchanged unless
an exact old repository URL is found during implementation.

## Failure Handling

- If local verification fails, do not rename the repository.
- If authentication, administration access, name availability, or the remote
  commit preflight fails, do not rename the repository.
- If the GitHub rename request fails, leave `origin` and public documentation
  unpublished and report the content-free API failure.
- If the rename succeeds but Git transport fails, keep the new repository name,
  leave the verified local commit intact, and retry the push without rewriting
  history. Do not automatically rename the repository back.
- Never print or persist tokens, account credentials, or credential-derived
  values during preflight or publication.

## Verification

Automated contracts distinguish `PRIMARY_REPOSITORY` from
`LEGACY_REPOSITORY`: primary sections and metadata must use `researchhelm`,
while the dedicated legacy section must retain the previous commands exactly.
Existing tests continue to assert all permanent compatibility invariants.

Final verification requires:

- all unit tests passing with only documented skips;
- valid sanitized demo state;
- a clean worktree, history, and archive release audit;
- local and remote `master` at the same commit;
- one unique commit author and no prohibited release-metadata keywords;
- the GitHub repository reporting the name `researchhelm`.
