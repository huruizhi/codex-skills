---
name: review-software-design
description: Review or shape software modules and architectures for complexity, deep interfaces, locality, testability, and AI-assisted-development risks. Use for design proposals, design docs, module interfaces, refactors, and architecture tradeoffs; use ordinary code review for line-level correctness findings.
---

# Review Software Design

Aim for the smallest design that concentrates knowledge, limits change impact, and makes intent easy to verify.

## Vocabulary

- **Module**: anything with an interface and an implementation, at any scale.
- **Interface**: everything a caller must know, including invariants, ordering, errors, configuration, and performance characteristics.
- **Depth**: useful behavior per unit of interface knowledge. A deep module gives callers high leverage through a small interface.
- **Seam**: the place where an interface allows behavior to vary.
- **Locality**: related knowledge, changes, bugs, and verification stay together.

## Review

1. Read the design or code plus the nearest callers and tests. Identify the module, its interface, its implementation, and the knowledge crossing its seam. When artifacts are incomplete, label assumptions. A review request produces findings; edit only when the user also requests implementation.
2. Evaluate the material design risks:
   - **Complexity**: change amplification, cognitive load, and unknown impact.
   - **Depth**: apply the deletion test. If deleting the module spreads its complexity across callers, it earns its place; if complexity disappears, it is probably a pass-through.
   - **Locality**: keep each design decision and its verification in one place rather than repeating it across callers.
   - **Seams**: place seams at demonstrated variation or volatile external dependencies. Prefer a direct implementation when variation is only hypothetical.
   - **Errors**: expose distinctions that change caller behavior, while keeping real failures explicit and observable.
   - **AI-era verification**: isolate nondeterminism and provider details; express intent with types, schemas, contract or acceptance tests, and useful observability. Keep generated changes small enough to review and reverse.
   - **Documentation**: record purpose, invariants, and non-obvious reasoning. Put enforceable facts in executable constraints rather than comments alone.
3. Prioritize the few issues that materially affect understanding or change cost. Treat short methods, microservices, patterns, TDD, and comments as means, not goals.

The review is complete when every conclusion points to evidence in an artifact or to an explicitly labeled assumption.

## Improve or Design

When the user wants a new or improved design:

1. Propose the smallest **deepening move**: simplify the interface, move scattered knowledge behind it, remove a pass-through, or relocate the seam.
2. **Design it twice** for consequential choices. Sketch two meaningfully different interfaces or seam placements; compare depth, locality, testability, reversibility, and operational risk; recommend one.
3. Use tests as executable intent at the module interface. Let the design determine test units, rather than allowing a sequence of tiny tests to determine the architecture.
4. Preserve the user's scope. A better design need not become a larger framework.

The design is complete when the recommended interface, hidden knowledge, main tradeoff, and verification approach are all explicit.

## Response Shape

Lead with one of: **Keep**, **Deepen**, or **Redesign**. Then give only the sections the request needs:

- **Evidence**: concrete complexity or depth observations.
- **Recommended design**: interface sketch and seam placement.
- **Alternative**: the second design and why it loses, when the choice is consequential.
- **Verification**: tests, evaluations, and observability at the interface.
- **Tradeoff**: the main cost or capability sacrificed.

Keep simple reviews short. Expand only when the system or decision is genuinely complex.
