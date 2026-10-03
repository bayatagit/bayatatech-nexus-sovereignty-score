# Roadmap

## Milestones

### M1 Scoring definition and open methodology

Status: in progress

Publish the six-dimension scoring definition, rules (critical cap, not applicable redistribution, grades, findings) and the human methodology document.

### M2 Core library with full test coverage

Status: in progress (initial version)

Ship a standard-library Python package that loads the bundled definition, validates input, scores assessments and exposes a stable result shape covered by automated tests.

### M3 Command line tool and linked data output (JSON-LD)

Status: CLI started, linked data planned

Provide `nss score` and `nss version`. Add JSON-LD output aligned with a published vocabulary in a later increment.

### M4 Integration examples for container, orchestrated and bare metal deployments

Status: planned

Document how to run assessments beside common deployment patterns without prescribing a single vendor stack.

### M5 Full documentation, package index publication, public versioned schema registry

Status: planned

Publish packaged releases, expand operator docs and host versioned input/output schemas for machine consumers.

### M6 Community feedback round and stable v1.0 release

Status: planned

Collect challenges to weights and interpretations, freeze a stable major version after review.

## Later

- Additional frameworks (German federal IT baseline protection, EU cloud certification scheme)
- Independent security review
- Governance for schema changes
