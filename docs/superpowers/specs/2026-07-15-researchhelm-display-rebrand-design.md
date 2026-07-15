# ResearchHelm Display Rebrand Design

## Goal

Rename the public-facing product brand from Human-Governed Autoresearch to
**ResearchHelm** without changing any compatibility identity, installation
path, command, protocol, or runtime behavior.

Approved English tagline:

> Human-governed research, from resources to audited claims.

The name communicates the product position: the human remains at the helm,
while the skill supports resource-aware scouting, supervised bounded
experiments, and claim-to-artifact auditing. It does not imply an autonomous
scientist or guaranteed research outcomes.

## Display Surfaces

Update only current public-facing display surfaces:

- `README.md`: use `ResearchHelm` as the title and product name, and place the
  approved English tagline directly below the title.
- `README.zh-CN.md`: use `ResearchHelm` as the title and product name, with a
  faithful Chinese explanation of the tagline.
- `skills/autoresearch/SKILL.md`: use `ResearchHelm` as the visible heading and
  in the opening product sentence.
- `skills/autoresearch/agents/openai.yaml`: set `interface.display_name` to
  `ResearchHelm` and retain the existing functional prompt contract.
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: introduce
  `ResearchHelm` in human-readable descriptions while retaining their machine
  identifiers.

Use `ResearchHelm` when prose refers to the product. Use `autoresearch` only
when prose refers to the literal Skill ID, plugin ID, command, directory, mode
contract, or legacy compatibility surface.

`Research Cockpit` remains the component name. Historical specifications,
plans, experiment records, and frozen public artifacts are not rewritten.

## Compatibility Invariants

The rebrand must not change:

- GitHub repository owner or repository name: `zhangyiCristino/autoresearch-skill`;
- Skill ID and directory: `autoresearch` and `skills/autoresearch/`;
- plugin and marketplace IDs: `autoresearch` and `autoresearch-skill`;
- `/autoresearch` and every existing install, clone, copy, or `npx skills`
  command;
- modes `pi`, `scout`, and `optimize`;
- schemas, state directories, recommendation-card rules, human gates, privacy
  boundaries, or any executable behavior.

This guarantees that existing users receive a display-name update rather than
a migration.

## Verification

Verification will:

1. parse the edited JSON and YAML metadata;
2. assert that every compatibility identifier and documented install command
   remains unchanged;
3. check that current display surfaces use `ResearchHelm` consistently and do
   not retain the old display heading;
4. run the complete unit-test suite and state validation;
5. run the worktree, history, and archive release-security audit before any
   publication.

No repository rename, tag, release, or remote publication is part of the
display rebrand until the implementation is separately reviewed and approved.
