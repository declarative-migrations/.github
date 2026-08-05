# declarative-migrations organization handbook

> Shared operating defaults for repositories maintained under **declarative-migrations**. Repository-local policy may strengthen these rules but should not silently weaken them.

## Mission

declarative-migrations maintains deterministic, declarative schema and data-migration tooling. This `.github` repository is the canonical home for shared policy, reusable templates, community health files, and planning links.

## Repository contract

Each active repository must document purpose, ownership, maturity, supported engines and versions, development and test commands, authoritative manifest and state formats, release and rollback procedures, compatibility policy, and GitHub Project/Linear links. Migration components should also document planning semantics, dependency ordering, transactional behavior, locking, idempotency, drift detection, destructive-change safeguards, resumability, and audit output.

## Change workflow

1. Anchor work in an issue, Linear item, or documented maintenance objective.
2. Keep branches and pull requests focused.
3. Explain motivation, scope, data and compatibility risk, validation, migration, and rollback.
4. Test empty, existing, drifted, partially applied, concurrent, destructive, rollback, and cross-version paths as relevant.
5. Resolve conflicts semantically by reconstructing both sides' intent.
6. Prefer squash merges for focused work unless commit structure materially improves auditability.

## Evidence, security, and documentation

Pull requests should include reproducible commands, fixtures, generated plans, expected and observed state, negative-path coverage, documentation updates, and CI or local-equivalent evidence. Never commit credentials, production dumps, private schemas, or sensitive logs. Follow `SECURITY.md` for private reporting. Keep examples executable, compatibility matrices current, destructive behavior explicit, and important design and operational decisions recorded.

## Planning ownership

GitHub owns code, reviews, checks, releases, and delivery evidence. Linear owns priority, dependencies, sequencing, and cross-project planning. The organization GitHub Project is the cross-repository execution view; see `PROJECTS.md` for routing details.

## Organization health

- [ ] Profiles, descriptions, topics, and READMEs are current.
- [ ] Community health files and reusable issue/PR guidance are present.
- [ ] Ordering, locking, drift, idempotency, destructive safeguards, and rollback are documented.
- [ ] Required checks cover supported engines, versions, partial failure, and supply-chain risk.
- [ ] Stale repositories are archived or clearly marked.
- [ ] GitHub Project and Linear links resolve and reflect completed work.
