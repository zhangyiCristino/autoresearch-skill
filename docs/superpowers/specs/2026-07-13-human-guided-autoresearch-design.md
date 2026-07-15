# Human-Governed Autoresearch v2 Design

Status: approved design sections for implementation planning
Date: 2026-07-13
Target repository: `zhangyiCristino/autoresearch-skill`

## 1. Product thesis

Autoresearch v2 is not another system that promises to replace a scientist or turn a topic into a paper without supervision. It is a lightweight, installable research-governance skill that helps a human principal investigator decide which idea deserves scarce resources, then supervises implementation and limits every claim to traceable evidence.

Public positioning:

> Not another autonomous AI scientist. Tell it what resources you have; it helps decide what is worth researching—and verifies that it was done correctly.

The memorable product loop is:

`resources -> defensible ideas -> human decisions -> bounded execution -> audited claims`

The existing `modify -> verify -> keep/discard -> repeat` protocol remains valuable, but becomes one bounded execution primitive rather than the whole definition of research.

## 2. Goals

1. Preserve the existing repository name, Claude Code plugin identity, installation commands, `/autoresearch` entry point, and mechanical optimization behavior.
2. Keep the canonical skill compliant with the open Agent Skills format, add Codex-standard metadata, and support capable coding agents without maintaining a second copy of the research protocol.
3. Make `pi` the default mode: the human owns scientific decisions while AI performs evidence gathering, implementation, verification, and post-processing inside approved boundaries.
4. Generate research ideas conditioned on real resources: accelerators, wall time, cost, data, licenses, code, expertise, and venue deadline.
5. Check idea overlap against public papers, code, and datasets and report bounded evidence rather than an unsupported novelty score.
6. Make every approval decision concise through decision-ready cards rather than generic checkpoint questions.
7. Separate implementation from verification and preserve reproducible provenance from idea to final claim.
8. Produce a zero-dependency static Research Cockpit that gives the project a distinctive, screenshot-friendly artifact.
9. Recommend complementary skills when a research stage has a concrete capability gap, while requiring human approval before every newly introduced skill is installed or used.
10. Make every named compatibility claim traceable to a client version, test date, commit, and evidence artifact.
11. Prevent Claude Code or Codex account data, API credentials, personal machine identifiers, private research content, and local-only artifacts from entering logs, Git history, CI artifacts, Cockpit exports, release archives, or public uploads.

## 3. Non-goals

- Do not build a hosted research platform, database, scheduler, or long-running web service.
- Do not promise fully autonomous scientific discovery or automatic publication.
- Do not treat a scalar benchmark improvement as sufficient evidence for a scientific claim.
- Do not execute clinical, wet-lab, physical, safety-critical, licensed, or externally consequential actions without domain-specific human authorization.
- Do not duplicate workflow rules across Claude Code, Codex, or other runtime adapters.
- Do not build a new package registry or a bespoke multi-agent installer for v2.
- Do not claim native support for a client merely because a third-party installer recognizes its install path.
- Do not automatically install or invoke a newly recommended skill.
- Do not read Claude Code, Codex, browser, Git, SSH, cloud, or operating-system credential stores; API credentials remain opaque and host-managed.
- Do not claim absolute security. Public claims describe the exact security checks and their limitations.

## 4. Compatibility architecture

Keep one canonical skill:

```text
skills/autoresearch/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- idea-diligence.md
|   |-- resource-triage.md
|   |-- experiment-design.md
|   |-- implementation-audit.md
|   |-- post-processing.md
|   |-- legacy-optimize.md
|   |-- skill-recommendations.md
|   |-- privacy-security.md
|   `-- schemas.md
|-- scripts/
|   |-- validate_state.py
|   |-- inspect_skill.py
|   |-- sanitize_export.py
|   |-- audit_release.py
|   |-- validate_compatibility.py
|   `-- render_cockpit.py
`-- assets/
    `-- templates/

evals/
|-- shared/
|-- claude/
|-- codex/
|-- portable/
`-- compatibility/
    `-- clients.json

.github/
|-- ISSUE_TEMPLATE/
|   `-- compatibility-report.yml
`-- workflows/
    |-- ci.yml
    `-- security.yml

SECURITY.md
.security-allowlist.json
```

`SKILL.md` contains only the common frontmatter subset (`name` and `description`), mode routing, the state machine, human authority, escalation rules, and links to references. `.claude-plugin` retains its current names and paths. `agents/openai.yaml` supplies Codex UI metadata generated from the canonical skill. Runtime-specific eval adapters may differ, but the expected decisions are shared.

The supported execution boundary is a coding agent that can read local files, execute commands, and use Git. A client missing any of those three capabilities is unsupported and must say so rather than attempting the workflow. Network access is conditional: an offline client may run an approved local optimization or analyze user-provided sources, but it may not claim that it searched public literature, code, or datasets.

### Distribution layers

1. **Native Agent Skills:** compatible clients discover the canonical `skills/autoresearch/SKILL.md` and its relative resources.
2. **Runtime-specific entry points:** the existing Claude Code plugin and Codex `agents/openai.yaml` remain thin adapters to the same canonical skill.
3. **Community installer:** the README offers `npx skills add zhangyiCristino/autoresearch-skill --skill autoresearch` and clearly identifies the Vercel Skills CLI as a third-party community installer.
4. **Use without installation:** the README offers `npx skills use zhangyiCristino/autoresearch-skill@autoresearch` for clients supported by that tool.
5. **Portable fallback:** a user may download the complete release or clone the repository and instruct a capable coding agent to read `skills/autoresearch/SKILL.md`, resolve relative references from the skill root, check its capabilities, default to `pi`, and stop at every human gate.

The existing Claude Code commands remain exactly:

```text
/plugin marketplace add zhangyiCristino/autoresearch-skill
/plugin install autoresearch@autoresearch-skill
```

The portable bootstrap is:

```text
Read <download-path>/skills/autoresearch/SKILL.md completely.
Resolve every relative reference from that skill directory.
Check that you can read files, execute commands, and use Git.
Use pi mode unless I explicitly request scout or optimize.
Do not cross a human decision gate without my approval.
```

The portable instructions live in the English and Chinese READMEs rather than in a second protocol file. A release archive must include the complete skill folder; downloading only `SKILL.md` is not a supported installation because references, scripts, and assets are part of the contract. Documentation distinguishes the `pi` research mode from the Pi agent client.

### Compatibility evidence and claims

`evals/compatibility/clients.json` is the source of truth for the public compatibility matrix. Each entry records the client and version, operating system, install command, test date, tested commit, evidence path, limitations, and one or more of these labels:

- `Standard-validated`: the canonical folder passes the Agent Skills format validator; this is a repository-level format claim, not a native-client claim.
- `Install-path verified`: the pinned community installer discovers the skill and writes or links it to the selected client path.
- `Native-tested`: a real client completes installation, discovery, activation, a human-gate refusal, and a safe exit scenario.
- `Portable-tested`: a client without native skill installation follows the portable bootstrap and passes the shared behavior scenario.
- `Community-reported`: a report includes the required version, operating system, command, commit, and raw evidence but has not been independently reproduced by the maintainer.

Installer support counts never become autoresearch support counts. Named clients receive a green native claim only after a real-client test, and every public row shows its version and test date. Stale rows become `needs revalidation`. The README says `portable fallback for capable coding agents`, never `works with every AI agent` or `tested on 70+ agents` without matching evidence.

## 5. Modes and routing

### `pi` — default

Runs the complete human-governed lifecycle. The human approves the idea, preregistered plan and budget, escalation from pilot to full execution, and final claims.

### `scout`

Runs resource intake, landscape search, overlap analysis, and idea ranking. Stops after the idea decision card. It does not write experiment code.

### `optimize`

Preserves the current single-metric autonomous optimization use case. It is selected only when the user explicitly asks for bounded mechanical optimization, such as an overnight benchmark run. It retains branch isolation, a frozen evaluator, atomic changes, commit-before-verify, truthful crash rows, and keep/discard behavior.

Mode resolution rules:

1. Honor an explicitly named mode.
2. Use `scout` when the user asks only for ideas, novelty diligence, or resource feasibility.
3. Use `optimize` only for an explicit scalar objective with an agreed evaluator, scope, and budget.
4. Use `pi` for scientific ideation, implementation, interpretation, or any ambiguous request.
5. Never infer permission for a more autonomous mode from silence or previous approval.

## 6. Lifecycle and human gates

```text
RESOURCE_INTAKE
  -> IDEA_SCOUT
  -> GATE_1_IDEA
  -> PREREGISTRATION
  -> GATE_2_PLAN_AND_BUDGET
  -> BUILD
  -> VERIFY
  -> PILOT
  -> GATE_3_FULL_RUN
  -> BOUNDED_EXECUTION
  -> ANALYZE_AND_AUDIT
  -> GATE_4_CLAIMS
  -> PACKAGE
```

Skill recommendation is a sidecar decision loop rather than a lifecycle stage:

```text
ANY_STAGE
  -> CAPABILITY_GAP
  -> SKILL_RECOMMENDATION_CARD
  -> HUMAN_DECISION
  -> RETURN_TO_SAME_STAGE
```

Recommending or approving a skill never advances a research gate, changes the approved question, or expands the budget or editable scope.

Each gate produces a Decision Card containing a recommendation, alternatives, evidence, uncertainty, resource consequences, failure modes, and the exact decision requested. Valid human decisions are `approve`, `revise`, `reject`, or `defer`. An approval record includes the stage input hash, actor, timestamp, rationale, and constraints. Silence, an old approval, or approval of a different hash is not valid.

Gate responsibilities:

- Gate 1: decide whether an idea deserves investment.
- Gate 2: approve whether the experiment can test the hypothesis and whether its budget and risks are acceptable.
- Gate 3: decide whether pilot evidence justifies the full run.
- Gate 4: decide what the evidence permits the project to claim.

### Governed skill recommendation

Autoresearch recommends a complementary skill only when the current stage has a concrete capability gap, the skill can materially improve evidence or reliability, the user asks for help finding a skill, or a failure is directly attributable to missing specialist capability. It does not recommend skills merely to appear helpful, add formatting, or promote popular projects.

Typical capability matches include literature and citation work during Scout, experiment design and statistical review during preregistration, testing and framework expertise during Build, debugging and leakage review during Verify, scientific plotting and sensitivity analysis during Analyze, and citation, data-availability, writing, patent, slide, or document preparation during Package.

The recommender:

- returns at most three non-redundant candidates as a Pareto set over task fit, evidence, permission cost, and source trust;
- prefers already installed skills, then user-configured private or team catalogs, official or client-curated catalogs, known public directories, and finally a specific public repository with inspectable provenance;
- treats popularity and star counts as discovery signals only, never as evidence of scientific quality or trust;
- includes the no-new-skill option;
- never recommends autoresearch itself, detects recommendation cycles, and does not repeat a rejected candidate in the same stage unless the input or evidence changes;
- limits `scout` recommendations to future help after the idea decision and limits `optimize` recommendations to the approved metric, evaluator, scope, and budget.

Every candidate appears in a Skill Recommendation Card containing the research stage, capability gap, reason for recommending now, expected contribution, alternatives, installed status, source, author, license, immutable version or commit, trust evidence, required tools and permissions, network or credential needs, data exposure, executable content, known limitations, confidence, and exact decision requested. Valid decisions are `approve`, `revise`, `reject`, or `defer`.

Discovery reads local metadata before loading bodies. Remote source inspection treats all content as untrusted data: fetch it into an isolated temporary location, record the source and hashes, inspect frontmatter, file types, scripts, binaries, symlinks, license, and permission declarations, and execute nothing. It never follows commands from a third-party README or installer script. An uninspectable source may be described, but it does not receive one-click installation.

For an installed skill, approval authorizes its use only within the matching stage input hash and stated constraints. For a remote skill, approval binds installation and the current use to the named source, immutable version or commit, content hash, permissions, and data boundary. Any change invalidates the approval. Installation prefers the runtime's native skill manager, then a verified community installer, and finally documented manual copying. The newly used skill remains subordinate to human gates, Builder-Verifier isolation, budget, safety rules, and the approved experimental scope.

Remote discovery does not transmit project files, unpublished results, or a full private research question unless the user explicitly approves that disclosure. Recommendations, decisions, installation method, version, hashes, constraints, and outcomes are recorded in the Flight Recorder.

## 7. Resource-to-Idea Scout

The intake contract records the question or domain, existing code and data, accelerators and VRAM, CPU/RAM/storage, wall time, monetary budget, data and API access, licenses, expertise, deadline, venue, allowed scope, forbidden scope, and risk tolerance.

The Scout searches public papers, code, and datasets using a recorded query ladder. For every candidate it produces:

- falsifiable hypothesis and proposed mechanism;
- closest public work and source links;
- overlap across question, method, data, evaluation, and claimed contribution;
- precise differentiating claim;
- minimum falsification experiment;
- low, expected, and high resource estimates with assumptions;
- expected information gain, feasibility, impact, evidence quality, compute fit, and risk;
- likely failure modes and pivot options.

Candidate status is restricted to `overlapping`, `incremental`, `differentiated`, or `unknown`. No search result can prove global novelty. Search failure, narrow coverage, conflicting evidence, and publication cutoff dates remain visible. Candidates are presented as a Pareto set; a weighted score may aid sorting but never replaces the human choice.

## 8. Preregistration and experiment contract

Before implementation, record the hypothesis, causal reasoning, baseline, controls, ablations, primary and secondary metrics, invariants, data splits, seeds or repetitions, uncertainty/statistical method, minimum effect of interest, maximum resource envelope, pilot definition, promotion rule, kill criteria, editable files, frozen evaluator, and expected artifacts.

The cheapest experiment capable of falsifying the idea is preferred. A full experiment cannot begin merely because code runs or a pilot metric improves.

## 9. Builder-Verifier supervision

Builder and Verifier are logically separate roles. When independent subagents are available, the Verifier receives the plan and raw artifacts without the Builder's conclusions. Otherwise, the agent performs a fresh audit pass using the same contract.

The Builder implements test-first in an isolated branch or worktree. The Verifier checks:

- the diff implements the approved hypothesis rather than an easier proxy;
- the evaluator and hidden data remain untouched;
- tests, static checks, shapes, units, splits, seeds, and environment are valid;
- the implementation did not change multiple causal factors without declaring them;
- there is no data leakage, metric gaming, benchmark fitting, or cherry-picking;
- a clean smoke run and the approved pilot reproduce;
- code, configuration, data, environment, and artifact hashes are recorded.

Open critical findings block Gate 3 even when the headline metric looks favorable.

## 10. Bounded execution and legacy optimization

Within an approved block, AI may autonomously run atomic experiments using the original git-backed loop. It must escalate before changing the question, data, baseline, evaluator, editable scope, resource ceiling, risk profile, or experimental design. It also escalates on anomalously large gains, non-reproducibility, unstable statistics, leakage indicators, environment drift, or the need for a more expensive stage.

Every run records its commit and hashes, metrics and uncertainty, runtime, peak memory, cost, status, decision, and artifact paths. Crashes use a non-numeric missing value and preserve their real cost. Resume verifies state, branch, code, data, configuration, and environment before continuing.

## 11. Post-processing and claim control

Raw results and their manifest are frozen before tables, figures, or prose are generated. Report applicable effect sizes, uncertainty, ablations, sensitivity analysis, alternative explanations, failure cases, and negative results. Figure and table values must be derived from registered artifacts rather than manually typed.

Every proposed conclusion appears in a claim-evidence matrix with status `supported`, `qualified`, or `unsupported`, plus linked runs, code, data, figures, citations, caveats, and counter-evidence. Unsupported claims are removed or explicitly downgraded. The skill may prepare a reproducibility bundle and manuscript-ready material, but publication remains a separate human action.

## 12. Research Flight Recorder and Cockpit

Each run uses `.autoresearch/<run-id>/`:

```text
research-brief.json
evidence.jsonl
idea-candidates.json
decision-log.jsonl
skill-recommendations.jsonl
experiment-ledger.jsonl
artifact-manifest.json
claim-evidence.json
research-cockpit.html
```

The JSON/JSONL files are the portable source of truth. `render_cockpit.py` uses only the Python standard library and embeds all data, CSS, and JavaScript into a static HTML file. It renders the resource envelope, novelty-feasibility-cost idea map, nearest-work overlap matrix, decision timeline, experiment cost/performance Pareto view, and claim-to-artifact evidence graph. No server or external asset is required.

The skill does not silently edit `.gitignore`. The run contract states which lightweight provenance files are committed and which raw or large artifacts remain local.

## 13. Credential, privacy, and publication security

Security rules are global invariants. They apply before mode routing and remain in force inside `pi`, `scout`, `optimize`, approved autonomous blocks, recommended skills, portable-agent execution, CI, and release automation. A human research approval cannot waive a credential-protection rule.

### Workspace and credential boundary

The skill accesses only the project workspace and paths the user explicitly places in scope. It does not inspect parent directories or enumerate the process environment. It must not read Claude Code or Codex account/configuration directories, browser profiles or cookies, Git credential helpers, SSH or GPG private keys, cloud credential files, operating-system credential stores, or session databases. Recommended skills inherit the same boundary and cannot use their approval to expand it.

API authentication remains opaque and host-managed. A command may inherit a credential through the runtime's environment or credential manager, but the skill records only the provider and whether authentication was available. It never prints, echoes, serializes, hashes, copies, or places the credential in a command argument, URL, Git remote, prompt, error report, or debug trace. Commands that dump all environment variables are forbidden. Private research content may be sent to a research service only after the user approves that specific data disclosure; credentials themselves are never disclosed.

### State classification and safe recording

Every state field is classified as `public` or `project-private`; `secret` is a forbidden storage class rather than a valid value. Before any text enters the Flight Recorder, persistent log, compatibility evidence, or Cockpit, the recorder checks for authorization headers, cookies, private keys, provider tokens, account/session data, credential-bearing URLs, Claude/Codex configuration paths, emails, operating-system usernames, home directories, hostnames, local IP or MAC addresses, device identifiers, and absolute local paths. High-confidence credential matches reject the write. The system never stores a secret's plaintext, ciphertext, reversible encoding, or hash.

Recorded commands use sanitized templates and replace sensitive arguments with `<redacted:credential>`. A finding contains only a rule ID, normalized repository-relative file, line or record location, severity, and remediation; it never echoes the matched value. Raw tool output that cannot be proven clean remains local and untracked.

`sanitize_export.py` converts validated local state into a separate public-export tree. It removes project-private fields, converts allowed artifact references to repository-relative identifiers, and emits a content-free sanitization report. `render_cockpit.py` produces a local private Cockpit by default. A public Cockpit can be rendered only from the sanitized public-export tree, and rendering fails on an unclassified field or security finding. No local Cockpit is added to Git automatically.

### Repository and release audit

`audit_release.py` is a Python-standard-library maintainer tool with three blocking scopes:

1. Scan staged changes and every tracked worktree file, including filenames and decoded strings from binary files.
2. Scan every Git object and author identity reachable from the release branch, without printing matched values.
3. Build the exact candidate with `git archive`, extract it in a temporary directory, and rescan the archive contents before upload.

CI repeats the repository scan with read-only permissions and no repository or publication secrets, and adds a pinned, checksum-verified Gitleaks scan for independent credential-pattern coverage. CI does not upload raw scanner output, failing files, research state, generated Cockpits, downloaded skills, or environment dumps. Git author email must be a GitHub noreply address or an address the user explicitly approved for public exposure. The release gate also rejects credential filenames such as `.env`, `auth.json`, cookie/session stores, private-key files, and Claude/Codex account configuration even when their content does not match a token pattern.

High-confidence credential, account, session, private-key, and credential-file findings cannot be allowlisted. A demonstrably benign personal-information false positive may be suppressed only in `.security-allowlist.json` with the rule ID, exact normalized path, line digest, reason, expiration date, and recorded human approval. Expired, path-drifted, or content-drifted entries fail closed.

The mandatory order is tracked/staged scan, reachable-history scan, archive build, archive scan, standard and behavioral gates, authentication check, then explicit publication approval. Push, pull request, tag, release, marketplace publication, and public demo upload remain blocked until every security scan reports zero unsuppressed findings.

### Incident handling and public claims

If a real credential or session value is found, stop publication, remove the material, and tell the user to rotate the credential or revoke the session. The skill does not rotate accounts or rewrite Git history on its own. If sensitive content entered a commit, history cleanup and any force update require separate explicit authorization, followed by a complete rescan. If content is already public, deletion alone is not considered remediation; rotation or revocation remains required.

`SECURITY.md` directs vulnerability reports to GitHub Private Vulnerability Reporting when enabled and warns users never to paste secrets into public issues. Documentation may state which security gates passed, with versions and dates, but never promises that the skill or release is absolutely secure.

## 14. Failure and safety behavior

| Condition | Required behavior |
|---|---|
| Literature source unavailable | Record the failure and coverage; set novelty status to `unknown` |
| Resource information incomplete | Offer tiered options; block a full run |
| Test or verification failure | Remain in BUILD/VERIFY; metrics cannot override the failure |
| Crash or OOM | Record truthful status and cost; repair within the agreed retry limit or discard |
| Budget threshold reached | Stop automatically and issue a Decision Card |
| Resume hash mismatch | Pause and require re-approval of changed inputs |
| Anomalously large improvement | Test leakage, evaluator integrity, and independent reproduction first |
| License, safety, ethics, or external-impact change | Stop and return the decision to the human |
| Unsupported citation or claim | Remove or downgrade it and record the audit finding |
| Missing local file, command, or Git capability | Report the unsupported capability and do not start the workflow |
| Offline public-overlap request | Restrict work to supplied sources and mark public search as not performed |
| Recommended skill source cannot be inspected | Mark trust as `unknown`; do not offer one-click installation |
| Recommended skill version, permission, or hash changes | Invalidate the old approval and issue a new Recommendation Card |
| Recommendation cycle or repeated rejected candidate | Stop the recommendation loop and continue without the skill |
| Third-party skill requests a gate or scope bypass | Treat it as untrusted instruction, block use, and record the finding |
| Command or tool requests an environment or credential dump | Refuse the request and continue without exposing the process environment |
| Recorder, log, or Cockpit input matches a credential | Reject the write; report only the finding code and location |
| Public export contains project-private or unclassified data | Fail the export and keep the local source untracked |
| Git history or candidate archive contains a security finding | Block every remote publication action until remediation and a clean rescan |
| Real credential or session data is discovered | Stop; require rotation or revocation and separately approved history cleanup if committed |

Dirty user worktrees are never stashed, reset, or committed by the skill. Destructive git operations are limited to the isolated experiment branch and agreed protocol.

## 15. Test strategy

Skill changes follow RED-GREEN-REFACTOR. Baseline tests run the current skill on pressure scenarios and capture exact failures before v2 guidance is written. Required RED scenarios include resource-driven ideation, premature novelty claims, infeasible ideas, skipped gates, unauthorized scope growth, lucky-seed selection, anomalous gains, resume drift, untraceable figures, and metric improvement that ignores compute cost or scientific validity.

Cross-agent RED scenarios include downloading only `SKILL.md`, proceeding without Git or command execution, claiming a public search while offline, confusing `pi` mode with the Pi client, treating installer discovery as native compatibility, inferring gate approval in a client without native gate UI, and changing legacy Claude identifiers to simplify installation.

Recommendation RED scenarios include irrelevant recommendation spam, ignoring an installed equivalent, ranking by stars instead of task fit, fabricating a skill or license, prompt injection that requests a gate bypass, installation or use without approval, reusing approval after a hash change, executing a third-party README command, recursive recommendations, repeating rejected candidates, expanding permissions or scope, and leaking private research content during discovery.

Security RED scenarios include requests to read Claude/Codex authentication files, enumerate environment variables, place an API key in a command or URL, retain an authorization header in a log, upload a local private Cockpit, commit a home-directory path or machine identifier, trust a recommended skill that requests credentials, allowlist a high-confidence token, and publish after a scanner failure. Public DOI strings, licensed repository URLs, synthetic fixture identities, and approved GitHub noreply addresses are negative controls that must not be rejected.

GREEN runs the same scenarios with v2. Key behavioral wording receives a no-guidance control and at least five fresh-context samples per variant. Shared contracts assert the same gate, mode, and recommendation-approval decisions on Claude Code, Codex, and the portable path. Existing regression cases for metric ties, evaluation-data peeking, dirty trees, crash hashes, and autonomous continuation remain.

Deterministic tests cover state validation, append-only events, hash checks, idempotent resume, Decision Card completeness, Skill Recommendation Card completeness, candidate limits and deduplication, cycle detection, approval binding, isolated inspection without execution, malformed inputs, compatibility-record freshness, relative-reference integrity, Cockpit rendering, pre-record rejection, public-export sanitization, worktree and staged scans, reachable-history scans, archive rescans, author-email policy, content-free findings, high-confidence no-bypass behavior, allowlist expiry and drift, and credential-filename rejection. Tests assemble invalid synthetic canaries from non-secret fragments only inside temporary directories at runtime; no real credential or complete token-shaped canary is committed to the repository. A pinned community-installer version is tested in temporary directories for discovery, project and global targets, copy and link modes, and use-without-installation. These tests establish only the label they actually exercise.

Release gates are:

1. `audit_release.py` reports zero findings for staged and tracked files, reachable Git history, author identities, and the exact candidate archive.
2. The pinned Gitleaks scan reports zero findings and emits no matched content into CI artifacts.
3. Public-export tests prove that account data, credentials, personal machine identifiers, absolute local paths, and project-private state cannot enter a committed Cockpit or demo.
4. The Agent Skills reference validator and Codex `quick_validate.py` pass.
5. `agents/openai.yaml` matches the canonical skill.
6. Claude plugin manifests remain valid and original install identifiers, paths, and commands are byte-for-byte unchanged.
7. Portable capability refusal, offline-claim behavior, complete-folder loading, and human-gate behavior pass their controls and forward tests.
8. The pinned installer discovers and installs the local skill in isolated temporary targets; this result is reported only as install-path verification.
9. No recommendation path installs or invokes a new skill without a matching approval record, and malicious skill content cannot alter gates, scope, or credential boundaries.
10. Shared, Claude, Codex, portable, recommendation, security, script, and compatibility tests pass without warnings.
11. Independent forward tests find no credential access, environment dump, unsafe persistence, gate bypass, unsupported claim promotion, private-data disclosure, or inflated compatibility claim.

## 16. Star-oriented release

Release v2.0.0 with a README that leads with the product thesis and a real, reproducible public demo: a researcher supplies one consumer GPU, a fixed GPU-hour budget, a public codebase/data source, and a research domain; the skill rejects overlaps, produces a Pareto shortlist, records the human choice, runs a pilot, audits the implementation, and renders the Cockpit.

The README includes the Cockpit screenshot or short reproducible animation; the universal install and try-without-installing commands; the original Claude Code commands; Codex metadata support; the portable bootstrap; a dated evidence-linked compatibility matrix; a compatibility note for existing `optimize` users; a concise comparison with end-to-end autonomous scientist platforms; the bilingual documentation already provided; and a direct link to `SECURITY.md`. Release notes explain migration without adding changelog files inside the skill.

The first-screen message is human-governed autoresearch for capable coding agents, not a client-count claim. It leads with resource-to-idea scouting, human scientific authority, Builder-Verifier supervision, bounded experiments, claim-to-artifact auditing, and the offline Cockpit. The public compatibility summary uses the form `Native-tested`, `Install-path verified`, and `Portable fallback`, filled only from the evidence registry. A compatibility-report issue template invites community evidence without presenting community reports as maintainer verification.

The public demo is generated only through the sanitized public-export path. Its source records, HTML, screenshot, compatibility logs, and release archive must contain no account data, credential material, personal machine identifiers, absolute local paths, or project-private research content. The README may list the dated security gates that passed, but it must not display an “absolutely secure”, “zero risk”, or equivalent badge.

GitHub topics may include `agent-skills`, `autoresearch`, `research-agent`, `claude-code`, `codex`, and `reproducible-research`. A named client is emphasized in topics or launch copy only after the corresponding evidence exists. The repository may prepare share-ready release text and demo assets, but posting to external communities or social platforms requires separate user authorization.

## 17. Acceptance criteria

- Existing Claude Code installation commands and plugin identifiers continue to work.
- The canonical folder passes the open Agent Skills validator and remains the only copy of the research protocol.
- Codex discovers the skill with valid `agents/openai.yaml` metadata.
- The community installer discovers the skill using the documented command, and the README identifies it as third-party.
- A capable non-native coding agent can follow the portable bootstrap from a complete release archive, while a client missing files, command execution, or Git stops with a precise capability report.
- Offline operation never becomes a claim that public literature, code, or datasets were searched.
- Every named compatibility status is tied to a client version, date, commit, evidence path, and exact tested capability.
- Ambiguous scientific requests enter `pi`; only explicit bounded scalar optimization enters `optimize`.
- A user can start from resources rather than a preselected idea.
- Every idea assessment exposes nearest public work, search coverage, resource assumptions, and falsification cost.
- No gate can be passed without a matching human approval record.
- No expensive full run begins before a successful verified pilot and Gate 3 approval.
- Every retained experiment and every final claim is traceable to code, configuration, data, environment, and artifacts.
- A capability gap may produce at most three evidence-backed Skill Recommendation Cards, with an installed-skill preference and an explicit no-new-skill option.
- No newly introduced skill is installed or used without a matching human approval bound to its source, immutable version or commit, content hash, permissions, and stage constraints.
- Remote skill inspection executes no third-party code, cannot bypass a human gate, and does not disclose private research content without explicit approval.
- The Cockpit renders offline from validated state with no third-party dependency.
- The old mechanical optimization safety regressions remain green.
- The skill never reads Claude Code, Codex, browser, Git, SSH, cloud, or operating-system credential stores and never enumerates the complete process environment.
- API credentials remain host-managed and no plaintext, ciphertext, reversible encoding, hash, command argument, URL, prompt, log, state record, or error report contains their values.
- Flight Recorder persistence rejects high-confidence credential content before writing and reports findings without echoing matched values.
- A local private Cockpit is untracked by default; a committed Cockpit or demo can be generated only from a validated sanitized public-export tree.
- Recommended skills cannot expand the workspace, account, credential, network-disclosure, or data-boundary rules.
- Staged files, tracked files, reachable Git history, commit author identities, and the exact release archive pass both the standard-library audit and pinned independent credential scan.
- Claude/Codex configuration, session stores, credential files, personal machine identifiers, absolute local paths, and unapproved author emails are absent from the public revision and release archive.
- High-confidence credential, account, session, private-key, and credential-file findings cannot be allowlisted; benign personal-information suppressions are exact, approved, expiring, and drift-sensitive.
- Any discovered real credential blocks publication until removal and user-performed rotation or revocation; committed history is rewritten only with separate explicit authorization.
- Public security wording names the checks that passed and does not promise absolute security.
