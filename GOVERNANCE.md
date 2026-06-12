# Shared Developer Agent Governance & Guidelines

This document serves as the master authority for LLM Developer Agent behaviors (Claude Code, Antigravity/Gemini CLI, and Codex CLI). These rules enforce discipline, surgical precision, and token efficiency.

---

## 1. Core Principles (Andrej Karpathy Rules)

Use these four heuristics to ensure surgical, high-quality development:

1. **Think Before Coding**: 
   * Always state assumptions, identify tradeoffs, and clarify scope before making edits.
   * If a request is ambiguous and could lead to multiple valid interpretations, ask for clarification.
2. **Simplicity First**:
   * Write the minimum amount of code necessary to solve the problem.
   * Reject speculative abstractions, unused configuration parameters, or complex helper classes unless explicitly required by the active task.
3. **Surgical Changes**:
   * Keep diffs as small and focused as possible.
   * Do not touch, format, or refactor adjacent or unrelated code unless the edit directly demands it.
4. **Goal-Driven Execution**:
   * Turn tasks into explicit success checks.
   * Write verification tests, check output logs, and confirm execution before claiming completion.

---

## 2. Process Governance (Codex Workflow)

### Required Flow For Code Tasks
* **Read Project Plan**: If the repository contains `PROJECT_PLAN.md`, read it before starting substantial coding.
* **Read Task Plan**: If the task has a directory in `plans/` (e.g. `plans/<task>/plan.md` and `pdca.md`), read the active handoff and plans before starting edits.
* **Triage Logging**: Before starting code changes, record or state the task triage:
  * `mode` (TDD, Debug, Feature)
  * `level` (Simple, Complex)
  * `must_test` / `optional_test`
  * `change_boundary` (files to edit)
  * `risks_and_assumptions`

### Complex Task Management
A task is **Complex** if it spans:
* More than 2 dependent steps.
* More than 1 file changed.
* Multi-iteration debugging.
* Multi-session resumption.

For Complex tasks, always maintain:
* `PROJECT_PLAN.md`
* `plans/<task>/plan.md` (Design & Execution Plan)
* `plans/<task>/pdca.md` (PDCA Loop Log)
* `plans/<task>/handoff.md` (Task Handoff state)

### Task Loop Closure
Before claiming completion:
1. Update the active `plan.md` and write verification evidence into `plan.md` or `pdca.md`.
2. Refresh `handoff.md` with the exact next step or final state.
3. Update `PROJECT_PLAN.md` if the phase or active task status changed.
4. If a touched directory has a `README.md` and its interface/responsibility changed, update the documentation.

---

## 3. Token Savings & Command Execution (RTK & Brevity)

* **RTK Command Interception**:
  * All shell commands are automatically proxied via `rtk` (e.g. `git status` -> `rtk git status`).
  * If executing manual commands in a tool without automatic hook configuration, always prefix shell commands with `rtk`.
* **Brevity Controls**:
  * Always be brief, clear, and direct. Avoid conversational filler or long preambles.
  * Use **Caveman Mode** (via `/caveman` or custom prompt instructions) if token conservation is critical.

---

## 4. Failure Escalation & PUA Rules

`pua` is an escalation layer, not the baseline.
Invoke `pua` and switch to a stronger, high-agency debugging loop when:
1. The same command or test path fails twice.
2. You are making small, repetitive tweaks without changing the underlying hypothesis.
3. You are tempted to report "done" or "cannot solve" without fresh test evidence.
4. The user explicitly requests a stronger effort level.

Under PUA escalation:
* Inspect error signals and logs directly (avoid summaries).
* Audit assumptions about state, imports, and variables.
* Implement a materially different debugging strategy (e.g., logging states, reading library internals).
