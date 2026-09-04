---
name: superpower-dev-flow
description: Enforce a Superpowers-style software delivery workflow for coding tasks. Use when implementing features, fixing bugs, or refactoring code where you need explicit design sign-off, bite-sized implementation planning, strict TDD (RED-GREEN-REFACTOR), review gates, and evidence-based completion.
---

# Superpower Dev Flow

## Overview

Use a strict, auditable development flow: align on design first, produce an executable task plan, implement with TDD, run review gates, and finish with verification and delivery choices.

## Workflow

### 1) Clarify and lock design before coding

- Ask focused questions until scope, constraints, and success criteria are concrete.
- Present design in small sections and get explicit approval before writing production code.
- Record the approved design in `docs/designs/YYYY-MM-DD-<topic>.md`.

### 2) Write a bite-sized implementation plan

- Convert approved design into tasks that each take ~2-10 minutes.
- For every task, specify:
  - Exact files to create/modify
  - Exact test files and test cases
  - Concrete commands to run
  - Expected pass/fail outcomes
- Save plan in `docs/plans/YYYY-MM-DD-<topic>.md`.

### 3) Implement with strict TDD

For each task, execute RED-GREEN-REFACTOR in order:

1. Write or update a failing test (RED).
2. Run test and confirm failure for the expected reason.
3. Write minimal code to pass (GREEN).
4. Run tests and confirm pass.
5. Refactor while keeping tests green.
6. Commit a small, single-purpose change.

If code is written before tests, delete or rewrite it to restore TDD order.

### 4) Run review gates between task groups

- Validate against the approved design and plan first.
- Check code quality second: readability, coupling, error handling, logging, compatibility.
- Block forward progress on critical issues.

### 5) Verify and close the branch

Before completion:

- Run targeted tests, then relevant broader test suites.
- Summarize evidence (commands + key outputs).
- Provide closeout options: merge, open PR, keep branch, or discard branch.

## Output Contract

When reporting progress or completion, always include:

1. Design status (approved/pending + doc path)
2. Plan status (doc path + current task)
3. File-level changes
4. Test evidence actually run
5. Risks, follow-ups, and rollback suggestion

## Reference

- Use `references/superpower-checklist.md` as the execution checklist.