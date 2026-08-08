# Rust formal and ownership assurance policy

This policy applies to Rust repositories in `declarative-migrations` that plan or execute schema changes, coordinate concurrent work, hold leases or locks, transform persistent state, or expose protocol state machines. Repository-local rules may be stricter.

The objective is not to label ordinary testing as a proof. The objective is to move invalid states out of runtime paths, model the remaining state space explicitly, and preserve exact evidence in the product and `declarative-migrations-test` organizations.

## Assurance order

Use the strongest inexpensive mechanism first:

1. **Types and ownership.** Represent identity, state, authorization, and lifecycle with newtypes, enums, typestates, lifetimes, and non-cloneable guards. Prefer a capability that owns or borrows the protected resource over a detached identifier that can be replayed.
2. **Pure transition model.** Express the relevant state machine as deterministic Rust over small values. State each safety invariant beside the model.
3. **Compile-time negative contracts.** Keep impossible uses executable with `compile_fail` doctests or `trybuild`, including validation bypass, double mutable borrowing, use after release, and protocol calls in the wrong phase.
4. **Bounded and property verification.** Exhaustively enumerate short traces and use property tests for longer generated traces. Loom or Kani may be added when thread interleavings or deeper bounded verification justify them.
5. **System witnesses.** Exercise the same contract against real PostgreSQL or CockroachDB instances, process boundaries, and protocol transports.
6. **Independent exact-head certification.** Pin the immutable product commit in a matching repository under `declarative-migrations-test`; do not certify a moving branch.

## Required migration invariants

Code that authorizes or applies migrations must make the following properties explicit and testable:

- a draft or unvalidated plan cannot be authorized or applied;
- a lease has at most one owner for the protected execution lane;
- authorization cannot outlive the guard or session that granted it;
- one lease cannot execute two mutable operations concurrently;
- release, apply, and abort are accepted only from valid phases and by the correct owner;
- applied and aborted states are terminal unless a separately modeled recovery transition exists;
- plan generation is deterministic for equivalent canonical inputs;
- successful application converges the target catalog to the declared source;
- statement failure, rollback, retry, and connection loss have documented atomicity semantics;
- destructive changes require an explicit policy decision rather than an implicit default.

A repository may add invariants, but it must not weaken these silently. When a database or distributed system prevents a property from being encoded in Rust alone, document the boundary and add a real-system witness.

## Rust design rules

- Use `#![forbid(unsafe_code)]` for assurance modules and test drivers unless a reviewed design note proves `unsafe` is required and states its local invariant.
- Do not derive `Clone` or `Copy` for a linear capability merely to make orchestration convenient.
- Prefer `&mut Guard` or ownership transfer for serialized execution. An `Arc<Mutex<_>>`, numeric lease ID, or string token is not equivalent evidence and requires a documented threat and lifecycle analysis.
- Keep transition functions pure where practical. Perform I/O at adapters that consume or borrow typed capabilities.
- Keep validation evidence immutable and bind audit receipts to stable plan or script fingerprints.
- Reject SQL or protocol input that can manipulate the guard responsible for authorizing that same execution unless that transition is modeled explicitly.
- New test drivers and repository validators for Rust systems should be written in Rust. A different language requires a concrete interoperability reason recorded in the pull request.

## Model discipline

A bounded model check proves only the model over the explored bound. Pull requests must state:

- the modeled state and transition alphabet;
- the invariants checked at every reachable state;
- the owner or actor set and exploration depth;
- abstractions that omit database, network, scheduler, or failure behavior;
- the system tests that witness those omitted boundaries.

Counterexamples must include the action trace. Rejecting an invalid transition is a successful safety result, not a reason to discard the generated case.

## Minimum Rust CI

Affected repositories should run, as applicable:

```sh
cargo fmt --all -- --check
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked --all-targets
cargo test --locked --doc
```

Add focused jobs for bounded models, elevated property-test case counts, database or process witnesses, and any compile-fail suite. Workflows must retain least-privilege permissions, full commit-SHA Action pins, timeouts, and `persist-credentials: false`.

Database-backed migration changes should cover supported PostgreSQL versions and CockroachDB where the repository claims compatibility. Lock or lease tests must include collision, execution, explicit release, reacquisition, and repeated lifecycle runs that expose leaked session state.

## Exact-head test-organization contract

A certification repository under `declarative-migrations-test` must:

1. record the full 40-character product SHA in its source pin and test plan;
2. checkout that SHA directly with read-only permissions;
3. run an assurance layer that is meaningfully independent of product CI;
4. retain scheduled execution without converting the pin back to a branch;
5. update its pull-request description with the product SHA, test-repository SHA, environments, and observed results.

The product pull request should link the certification pull request and record the same immutable SHA. Any product-head change invalidates prior exact-head evidence until the test repositories are repinned and rerun.

## Pull-request evidence

For stateful, concurrent, migration, or protocol changes, the pull request must name:

- safety properties and invariants;
- types or borrow relationships that enforce them;
- negative compile-time cases;
- model bounds and abstractions;
- product CI results at the exact head;
- independent `*-test` pins and results;
- compatibility, migration, rollback, and recovery behavior;
- remaining manual or external validation not actually performed.

Do not claim a proof of the deployed system when only a Rust model or unit test was checked. Precise scope is part of the assurance contract.
