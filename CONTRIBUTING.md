# Contributing

Thank you for helping improve the Nexus Sovereignty Score. This project stays small and reviewable: scoring changes need clear reasoning, tests and a version bump.

## Propose a new criterion

1. Open an issue describing the gap, the proposed criterion id, question, levels and weight impact.
2. Explain which dimension it belongs to and how existing criterion weights would be adjusted so they still sum to 1.0.
3. After discussion, open a pull request that updates `src/nss/data/nss-scoring-v0.1.json` (or a new versioned file), `docs/methodology.md`, schemas if needed, tests and `CHANGELOG.md`.
4. Bump the scoring definition version according to semantic versioning.

## Challenge an interpretation

Open an issue with legal or technical reasoning. Cite the criterion id, the current levels, and why the interpretive choice should change. Challenges that rely only on marketing claims are unlikely to be accepted. References to laws and regulations (GDPR, NIS2, EU AI Act, US CLOUD Act and similar) are welcome.

## Propose weight changes

Weight changes are sensitive because they affect comparability. Open an issue first with:

- the current and proposed weights
- why the relative importance changes
- whether the change is major-version breaking

Any merged weight change must update the scoring definition version and the changelog.

## Run tests locally

```bash
pip install -e ".[dev]"
pytest
```

Before opening a pull request, confirm that tests pass on your machine.

## Commit and pull request conventions

- Prefer small, focused commits with imperative messages.
- Do not introduce em dashes or en dashes in any file.
- In prose, do not name third-party companies, products or brands; describe technology generically. Laws and regulations may be named.
- Keep the implementation independent: do not copy code from other private projects.
- Pull requests should describe the motivation, the scoring impact and the test coverage.

## Scoring definition changes

Changes to the scoring definition require:

1. A version bump in the definition file
2. A changelog entry under Unreleased or a release section
3. Updated methodology text when interpretation changes
4. Tests that lock the new behaviour
