---
name: codex-deepseek-open-spec
description: Use when coordinating Codex as planner/reviewer with Claude Code or DeepSeek as an implementation agent through repo-local Open Spec files such as plans/codex-deepseek-collaboration/next_action.md, including writing specs, reviewing reports, enforcing scope, and preparing follow-up actions.
---

# Codex DeepSeek Open Spec

Use this skill to run a local file-based collaboration loop where Codex writes the task spec and reviews the implementation, while Claude Code / DeepSeek implements only the active spec.

## Core Contract

- Codex owns planning, Open Spec writing, review, verification, git submission, and follow-up specs.
- Claude Code / DeepSeek owns implementation inside the active Open Spec only.
- The active task file is normally `plans/codex-deepseek-collaboration/next_action.md`.
- The stable protocol is normally `plans/codex-deepseek-collaboration/协议.md`.
- Claude Code / DeepSeek writes only inside the `CLAUDE_REPORT` block unless the active spec explicitly says otherwise.
- Keep `live_order_allowed: false` and `git_submit_allowed_for_claude: false` unless the user explicitly authorizes a narrower exception.

## Start A Collaboration Round

1. Read repo instructions and check `git status --short --untracked-files=all`.
2. Read the stable protocol if it exists:
   - `plans/codex-deepseek-collaboration/协议.md`
3. Read current tracking context when present:
   - `PROJECT_PLAN.md`
   - relevant `plans/<task>/plan.md`, `pdca.md`, and `handoff.md`
4. Inspect the target code or docs before writing a spec.
5. Replace or create `plans/codex-deepseek-collaboration/next_action.md` with one narrow Open Spec.
6. Update the collaboration `plan.md`, `pdca.md`, and `handoff.md` enough for the next session to know what is active.
7. Run `git diff --check -- plans/codex-deepseek-collaboration`.

## Open Spec Checklist

Every `next_action.md` should include:

- YAML-like metadata: `action_id`, `state`, `owner`, `reviewer`, `repo_root`, `branch`, `base_commit`, `created_at`, `live_order_allowed`, `git_submit_allowed_for_claude`.
- `User Intent`: technical translation of the user's request.
- `Context`: repo facts and current evidence.
- `Objective`: one implementation target.
- `Allowed Changes`: exact file or directory boundaries.
- `Forbidden Changes`: files, behaviors, and commands that are out of scope.
- `Non-Goals`: tempting work that must not be done this round.
- `Implementation Notes`: preferred approach and known pitfalls.
- `Acceptance Criteria`: reviewable outcomes.
- `must_test`: exact commands DeepSeek must run.
- `optional_test`: useful but non-blocking commands.
- `Stop Conditions`: conditions that require reporting instead of improvising.
- `CLAUDE_REPORT`: the only report block for Claude Code / DeepSeek.

Use this report block:

```markdown
<!-- CLAUDE_REPORT_START -->
## Claude Report

- state:
- summary:
- changed_files:
- tests_run:
- tests_not_run:
- blockers:
- scope_changes_requested:
- review_notes:

<!-- CLAUDE_REPORT_END -->
```

## Review A Completed Report

1. Read `next_action.md`, especially `CLAUDE_REPORT`.
2. Check `git status --short --untracked-files=all`.
3. Inspect the actual changed files, not just the report.
4. Compare changes against every `Allowed Changes`, `Forbidden Changes`, and `Acceptance Criteria` item.
5. Rerun `must_test` when feasible; at minimum rerun the highest-signal focused tests and `git diff --check`.
6. Check for live-order, credential, dependency-install, and broad-architecture violations.
7. Add a `Codex Review` section to `next_action.md` with:
   - `state`: `accepted`, `rework_requested`, or `blocked`
   - summary
   - verification
   - findings or rework items
   - decision
8. Update collaboration `plan.md`, `pdca.md`, and `handoff.md`.

## Acceptance Rules

Accept only when:

- the diff stays within the Open Spec;
- `must_test` passes or any failure is proven unrelated and recorded;
- no forbidden live, credential, git, dependency, or broad runtime action occurred;
- the implementation is supported by code inspection, not just test counts;
- the next action is obvious from local files.

Request rework when:

- tests are conditional or weak and do not prove the intended behavior;
- a plan claims unimplemented phases as complete;
- DeepSeek changed files outside `Allowed Changes`;
- the work requires new scope, live access, network access, or credentials.

## Skill Design Note

Keep this skill process-only. Do not bake project-specific implementation details into it; put those details in each round's `next_action.md`.
