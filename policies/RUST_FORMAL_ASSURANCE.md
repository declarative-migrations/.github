# Rust formal and ownership assurance policy

This policy applies to Rust repositories in `declarative-migrations` that plan or execute schema changes, coordinate concurrent work, hold leases or locks, transform persistent state, or expose protocol state machines. Repository-local rules may be stricter.

The objective is not to label ordinary testing as a proof. The objective is to move invalid states out of runtime paths, model the remaining state space explicitly, and preserve exact evidence in the product and `declarative-migrations-test` organizations.

## Assurance order

Use the strongest inexpensive mechanism first:

1. **Types and ownership.** Represent identity, state, authorization, and lifecycle with newtypes, enums, typestates, lifetimes, and non-cloneable guards. Prefer a capability that owns or borrows the protected resource over a detached identifier that can be replayed.
2. **Typed-plan alias analysis.** Map each migration operation to explicit shared or exclusive borrows over hierarchical database resources. Reject or conservatively serialize operations whose dependencies cannot be proved independent.
3. **Pure transition model.** Express the relevant state machine as deterministic Rust over small values. State each safety invariant beside the model.
4. **Compile-time negative contracts.** Keep impossible uses executable with `compile_fail` doctests or `trybuild`, including validation bypass, double mutable borrowing, use after release, certificate bypass, and protocol calls in the wrong phase.
5. **Bounded and property verification.** Exhaustively enumerate short traces and use property tests for longer generated traces. Loom or Kani may be added when thread interleavings or deeper bounded verification justify them.
6. **System witnesses.** Exercise the same contract against real PostgreSQL or CockroachDB instances, process boundaries, and protocol transports.
7. **Independent exact-head certification.** Pin the immutable product commit in a matching repository under `declarative-migrations-test`; do not certify a moving branch.

## Required migration invariants

Code that plans, authorizes, or applies migrations must make the following properties explicit and testable:

- a draft, uncertified, or unvalidated plan cannot be authorized or applied through the hardened path;
- every typed change variant has explicit resource and dependency semantics, and adding a new variant fails compilation until those semantics are assigned;
- every certified execution wave is pairwise borrow-compatible and preserves the canonical plan order unless a separate dependency proof permits reordering;
- a certificate is bound to the exact typed plan and model version; structural validity alone cannot authorize certificate reuse for another plan;
- a lease has at most one owner for the protected execution lane;
- authorization cannot outlive the guard or session that granted it;
- one lease cannot execute two mutable operations concurrently;
- release, apply, and abort are accepted only from valid phases and by the correct owner;
- applied and aborted states are terminal unless a separately modeled recovery transition exists;
- plan generation is deterministic for equivalent canonical inputs;
- successful application converges the target catalog to the declared source;
- statement failure, rollback, retry, and connection loss have documented atomicity semantics;
- destructive and manual changes require explicit policy decisions rather than implicit defaults.

A repository may add invariants, but it must not weaken these silently. When a database or distributed system prevents a property from being encoded in Rust alone, document the boundary and add a real-system witness.

## Typed-plan resource and certificate discipline

When a migration planner or orchestrator claims that operations are independent or may share an execution wave:

- represent database, schema, relation, routine, type, sequence, index, policy, trigger, and other relevant object families with stable hierarchical resource paths;
- distinguish shared from exclusive access and exact-object from subtree access;
- make parent-subtree borrows conflict with incompatible descendant borrows;
- keep the operation-to-borrow mapping exhaustive over the typed change enum;
- resolve opaque SQL dependencies through a parsed dependency graph or a conservative barrier; never infer independence merely because two operations have different display names;
- group only operations proved pairwise compatible, and preserve input order unless dependency ordering is separately modeled and checked;
- keep the existing executor sequential unless the pull request explicitly changes execution semantics and adds database-backed evidence for the parallel path.

Plan certificates must include a model version, an exact-plan identity, ordered steps or waves, and the resource evidence needed for review. Consumers accepting a certificate from another process must recompute or otherwise authenticate its exact correspondence to the plan; checking certificate shape alone is insufficient. A stable checksum is an identity aid, not a cryptographic signature.

Changing resource, dependency, scheduling, or lifecycle semantics requires a model-version decision and invalidates exact-head certification until the product and matching `*-test` repositories are repinned and rerun.

MCP servers, CLIs, and orchestration layers must surface certificate, model-version, approval, and lease metadata rather than converting a successful tool call into an unqualified claim that a migration is safe. They must not reimplement a weaker parallel-safety heuristic outside the authoritative typed-plan model.

## Rust design rules

- Use `#![forbid(unsafe_code)]` for assurance modules and test drivers unless a reviewed design note proves `unsafe` is required and states its local invariant.
- Do not derive `Clone` or `Copy` for a linear capability merely to make orchestration convenient.
- Prefer `&mut Guard` or ownership transfer for serialized execution. An `Arc<Mutex<_>>`, numeric lease ID, or string token is not equivalent evidence and requires a documented threat and lifecycle analysis.
- Keep transition and alias-analysis functions pure where practical. Perform I/O at adapters that consume or borrow typed capabilities.
- Keep validation evidence immutable and bind audit receipts to stable plan or script fingerprints.
- Reject SQL or protocol input that can manipulate the guard responsible for authorizing that same execution unless that transition is modeled explicitly.
- New test drivers and repository validators for Rust systems should be written in Rust. A different language requires a concrete interoperability reason recorded in the pull request.

## Model discipline

A bounded model check proves only the model over the explored bound. Pull requests must state:

- the modeled state and transition alphabet;
- the resource hierarchy and alias rules when plan independence is claimed;
- the invariants checked at every reachable state;
- the owner or actor set and exploration depth;
- abstractions that omit database, network, scheduler, dependency-parser, or failure behavior;
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

Add focused jobs for bounded models, elevated property-test case counts, resource-alias and exact-certificate properties, database or process witnesses, and any compile-fail suite. Workflows must retain least-privilege permissions, full commit-SHA Action pins, timeouts, and `persist-credentials: false`.

Database-backed migration changes should cover supported PostgreSQL versions and CockroachDB where the repository claims compatibility. Lock or lease tests must include collision, execution, explicit release, reacquisition, and repeated lifecycle runs that expose leaked session state. Plan-safety tests must include alias symmetry, hierarchy overlap, certificate mismatch, deterministic scheduling, and generated typed plans.

## Exact-head test-organization contract

A certification repository under `declarative-migrations-test` must:

1. record the full 40-character product SHA in its source pin and test plan;
2. checkout that SHA directly with read-only permissions;
3. run an assurance layer that is meaningfully independent of product CI;
4. retain scheduled execution without converting the pin back to a branch;
5. update its pull-request description with the product SHA, test-repository SHA, environments, model version, and observed results.

The product pull request should link the certification pull request and record the same immutable SHA. Any product-head or formal-model change invalidates prior exact-head evidence until the test repositories are repinned and rerun.

## Pull-request evidence

For stateful, concurrent, migration, or protocol changes, the pull request must name:

- safety properties and invariants;
- types or borrow relationships that enforce them;
- resource paths, shared/exclusive aliases, opaque-dependency assumptions, and scheduling rules when plan independence is claimed;
- certificate/model version and exact-plan binding;
- negative compile-time cases;
- model bounds and abstractions;
- whether execution remains sequential or which separately checked proof permits parallel execution;
- product CI results at the exact head;
- independent `*-test` pins and results;
- compatibility, migration, rollback, and recovery behavior;
- remaining manual or external validation not actually performed.

Do not claim a proof of the deployed system when only a Rust model or unit test was checked. Precise scope is part of the assurance contract.
