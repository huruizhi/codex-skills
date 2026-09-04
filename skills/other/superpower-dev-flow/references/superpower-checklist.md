# Superpower Checklist

## A. Before Coding

- [ ] Problem statement and success criteria are explicit.
- [ ] Scope boundaries and non-goals are explicit.
- [ ] Design is approved and saved under `docs/designs/`.

## B. Plan Quality Gate

- [ ] Plan exists under `docs/plans/`.
- [ ] Tasks are bite-sized and ordered.
- [ ] Each task lists exact file paths.
- [ ] Each task lists test steps and expected outcomes.
- [ ] Each task lists runnable commands.

## C. TDD Gate (per task)

- [ ] RED: failing test added first.
- [ ] Failure confirmed with test output.
- [ ] GREEN: minimal code written.
- [ ] Passing result confirmed.
- [ ] REFACTOR completed with green tests.
- [ ] Small commit created.

## D. Review Gate

- [ ] Implementation matches approved design.
- [ ] Implementation matches task plan.
- [ ] Critical quality issues resolved before next tasks.

## E. Completion Gate

- [ ] Targeted tests pass.
- [ ] Relevant broader tests pass (or justified if skipped).
- [ ] Delivery summary includes file changes, evidence, risks, rollback.
- [ ] Branch disposition decision recorded (merge/PR/keep/discard).