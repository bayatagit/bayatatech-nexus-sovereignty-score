# Nexus Sovereignty Score methodology

Version: scoring definition `0.1.0-draft`

This document explains how the Nexus Sovereignty Score (NSS) is defined and calculated. It is written for technical staff, data protection officers, and public-sector IT leads who need a reproducible way to compare digital sovereignty posture across systems and over time.

NSS does not replace a legal opinion, a risk assessment, or a certification. It turns a structured questionnaire into a numeric result so that gaps are visible and comparable.

## Purpose

Digital sovereignty is often discussed in qualitative language: "EU cloud", "self-hosted", "sovereign by design". Those labels are hard to compare. Two organisations can both claim "EU hosting" while one places keys with a non-EU parent company and the other holds keys in its own hardware security module. Without a shared measurement, procurement and oversight remain anecdotal.

NSS exists to make digital sovereignty:

- **Measurable**: answers map to scores on a 0 to 100 scale.
- **Reproducible**: the same input and the same scoring definition always produce the same composite score and grade.
- **Comparable**: results that use the same major version of the scoring definition can be compared across teams, vendors, and assessment dates.

The primary audience is small and medium enterprises, municipalities, and data protection officers who need a practical baseline rather than a consultancy-only model.

## Why six dimensions

Sovereignty is not a single property of a data centre. It is a set of control questions across storage, contracts, networks, cryptography, AI processing, and regulatory documentation. Collapsing everything into one yes/no question hides the usual failure modes: EU servers under non-EU jurisdiction, open formats without an exit plan, encrypted disks with provider-held keys, or AI inference that leaves the EU without audit logs.

NSS therefore uses six dimensions:

| Dimension | Weight | Role |
|-----------|--------|------|
| Data residency | 0.20 | Where data sits and which law can compel access |
| Vendor independence | 0.20 | Whether lock-in blocks exit |
| DNS and network integrity | 0.15 | Whether resolution and egress leak control |
| Key management | 0.20 | Who can decrypt |
| AI inference | 0.10 | Where models run and what is retained |
| Regulatory mapping | 0.15 | Whether GDPR, NIS2 and EU AI Act duties are documented |

Weights are a first proposal for public debate. Data residency, vendor independence and key management each receive 0.20 because each can nullify the others: EU storage with provider-held keys, or strong cryptography inside an irreplaceable proprietary stack, still fails a sovereignty test. DNS and network integrity and regulatory mapping receive 0.15 because they are essential but usually secondary to custody and jurisdiction. AI inference is weighted 0.10 because many organisations have little or no AI today; the dimension can be marked not applicable and its weight redistributed.

Weights sum to 1.0. Criterion weights inside each dimension also sum to 1.0.

## Data residency

This dimension measures physical location and legal reach. Server location alone is not residency.

### Why DR2 exists and is critical

An EU-located server operated by a company under non-EU jurisdiction can still be subject to foreign access laws. The US CLOUD Act is the best-known example: it can create obligations for providers organised under United States law even when the relevant systems sit in the EU. Other jurisdictions have similar extraterritorial tools. That is why **DR2 (operator legal jurisdiction)** is critical and weighted 0.40. Storage in the EU does not settle the question if the operator can be compelled under foreign law.

### Criteria

**DR1: Primary data storage location** (weight 0.35, critical)

- `eu_eea` = 100: primary data stored in the EU or EEA.
- `adequacy_country` = 60: stored in a country with an EU adequacy decision.
- `other` = 0: stored elsewhere.

**DR2: Operator legal jurisdiction** (weight 0.40, critical)

- `eu_entity` = 100: operator is organised under EU/EEA law without a controlling non-EU parent that can compel disclosure.
- `eu_subsidiary_of_non_eu_parent` = 40: EU subsidiary of a non-EU parent; foreign-law pressure remains plausible.
- `non_eu_entity` = 0: operator is a non-EU entity.

**DR3: Backups, replicas and support access** (weight 0.25)

- `all_eu` = 100
- `partly_outside` = 50
- `outside` = 0

Backups and remote support often undermine carefully chosen primary regions. DR3 captures that secondary exposure.

## Vendor independence

Sovereignty without an exit path is temporary. This dimension asks whether data and services can leave a vendor relationship without unacceptable loss.

**VI1: Data export in open, documented formats** (weight 0.30)

- `full` = 100, `partial` = 50, `none` = 0

**VI2: Self-hostable or replaceable by another provider** (weight 0.30)

- `yes` = 100, `with_significant_effort` = 50, `no` = 0

**VI3: Contractual exit terms** (weight 0.20)

Termination, data return and deletion must be documented (`documented` = 100, `partial` = 50, `none` = 0). Informal promises are not enough.

**VI4: Single-vendor concentration** (weight 0.20)

Numeric input from 0.0 to 1.0: share of critical services with the same single vendor. Score = `round(100 * (1 - share))`. A share of 0.0 scores 100; a share of 1.0 scores 0. Concentration is scored this way because lock-in is often a portfolio effect, not a property of one contract.

## DNS and network integrity

Name resolution and outbound traffic decide who sees metadata and where telemetry flows, even when application data stays put.

**DN1: DNS resolver operator** (weight 0.35, critical)

- `self_operated` = 100
- `eu_operator` = 80
- `non_eu_public_resolver` = 0

Public resolvers outside the EU are treated as a fundamental failure for this dimension because recursive resolution reveals destination patterns at scale.

**DN2: Encrypted DNS in use** (weight 0.20): `yes` = 100, `no` = 0.

**DN3: Outbound telemetry to non-EU endpoints** (weight 0.30): `none` = 100, `limited` = 50, `extensive` = 0.

**DN4: Documented egress control** (weight 0.15): `yes` = 100, `partial` = 50, `no` = 0.

## Key management

If the provider can decrypt, residency claims are weaker than they appear. Key custody is therefore a major dimension with a critical criterion.

**KM1: Who holds the encryption keys** (weight 0.40, critical)

- `customer_hardware_module` = 100: keys in customer-controlled hardware security modules.
- `customer_software` = 70: customer-controlled software key stores.
- `provider_with_customer_control` = 30: provider infrastructure with customer-managed keys under limited conditions.
- `provider` = 0: provider holds keys without meaningful customer exclusivity.

**KM2: Encryption at rest and in transit** (weight 0.20): `both` = 100, `one` = 50, `none` = 0.

**KM3: Key rotation and revocation** (weight 0.15): `documented_and_tested` = 100, `documented` = 50, `none` = 0.

**KM4: Provider technically able to access plaintext** (weight 0.25): `no` = 100, `under_conditions` = 30, `yes` = 0.

KM4 is separate from KM1 because "customer keys" marketing language sometimes coexists with support channels that still expose plaintext.

## AI inference

This dimension may be marked not applicable when the organisation does not use AI systems. When it applies, location, retention and auditability matter.

**AI1: Where inference runs** (weight 0.45, critical)

- `on_premise` = 100
- `eu_operator` = 70
- `eu_region_non_eu_operator` = 30
- `non_eu` = 0

An EU region operated by a non-EU provider scores poorly for the same jurisdiction reasons as DR2.

**AI2: Prompts or outputs retained or used for training** (weight 0.35): `no` = 100, `opt_out` = 40, `yes` = 0.

**AI3: Audit logging of inference events** (weight 0.20): `yes` = 100, `partial` = 50, `no` = 0.

## Regulatory mapping

NSS maps operational facts to documentation that GDPR, NIS2 and the EU AI Act typically require. It does not certify compliance.

**RM1: Legal basis for every transfer outside the EU/EEA** (weight 0.30)

- `all` = 100, `some` = 50, `none` = 0, `no_transfers` = 100

This relates to GDPR Chapter V transfer rules. `no_transfers` scores full marks because the obligation does not arise.

**RM2: Records of processing and processor agreements** (weight 0.25)

- `complete` = 100, `partial` = 50, `missing` = 0

This relates to GDPR records of processing and Article 28 processor arrangements.

**RM3: NIS2 risk management measures** (weight 0.25)

- `in_place` = 100, `partial` = 50, `missing` = 0, `not_in_scope` = null (excluded)

Only organisations in scope of NIS2 are scored. Others mark `not_in_scope` so the criterion is excluded and its weight redistributed.

**RM4: EU AI Act risk classification** (weight 0.20)

- `done` = 100, `partial` = 50, `not_done` = 0, `no_ai_systems` = null (excluded)

NSS supports preparatory work for a legal assessment. It does not replace counsel, supervisory authority guidance, or a formal conformity assessment.

## Scoring rules

### Dimension score

For each applicable criterion, the answer selects a level score from 0 to 100 (or a formula for VI4). Criterion weights among applicable criteria are renormalised to sum to 1.0. The dimension score is the weighted average of those criterion scores.

### Critical cap

If any critical criterion in a dimension scores 0, that dimension score is capped at 40, even if other criteria score 100. The rule exists because one fundamental failure (for example provider-held keys, or a non-EU public DNS resolver as the only path) should prevent a high dimension grade. Cosmetic strengths must not hide a structural defect.

### Not applicable handling

A whole dimension may set `"not_applicable": true`. A criterion with a null level (RM3 `not_in_scope`, RM4 `no_ai_systems`) is also treated as not applicable. Excluded weights are redistributed proportionally across remaining dimensions or criteria so that applied weights always sum to 1.0 among what remains.

### Rounding and grades

Dimension scores round to one decimal place. The composite score is the weighted sum of applicable dimension scores, then rounded to an integer.

Grades:

- **A** 85 to 100: high sovereignty
- **B** 70 to 84: substantial sovereignty
- **C** 50 to 69: moderate sovereignty
- **D** 30 to 49: limited sovereignty
- **E** 0 to 29: low sovereignty

### Findings

Every applicable criterion scoring below 50 produces a finding with dimension, criterion, score and a short message. Findings are the actionable list for remediation planning.

## Versioning policy

The scoring definition uses semantic versioning. The package and every output record the `scoring_version` used for the calculation. Results are only comparable within the same major version. A major bump may change weights, criteria, levels or rules in ways that break trend comparisons. Minor and draft increments may add clarifying questions or fix inconsistencies; consumers should still record the exact version string.

## Limitations and open questions

1. **Self-reported answers.** NSS trusts the assessor. There is no automated discovery of storage regions, DNS paths or key custody in this version.
2. **No evidence attachment yet.** Future versions may link answers to documents or configuration extracts.
3. **Weights are a first proposal.** Public challenge is expected, especially the relative weight of AI inference and regulatory mapping.
4. **Organisation-level aggregation.** Multi-system landscapes require a clear system boundary before scoring; NSS does not yet define portfolio aggregation rules.
5. **Legal nuance.** Jurisdiction and transfer tools change. The scoring levels are interpretive, not a substitute for case-specific legal analysis.

## How to challenge or propose changes

Open an issue describing the criterion, the current interpretation, and a legal or technical argument for change. Weight changes and new criteria require a version bump and a changelog entry. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the process, local test expectations, and pull request conventions.
