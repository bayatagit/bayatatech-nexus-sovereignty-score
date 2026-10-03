# Nexus Sovereignty Score (NSS)

Nexus Sovereignty Score is an open Python library and versioned scoring definition for measuring digital sovereignty across infrastructure stacks. It turns a structured assessment into a composite score, a letter grade and a list of findings that can be compared over time.

## Why it exists

SMEs, municipalities and data protection officers are often asked whether a system is "sovereign" without a shared yardstick. Marketing claims about EU regions or encryption leave gaps around operator jurisdiction, key custody, DNS leakage and contractual exit. NSS closes that measurement gap with a transparent questionnaire, published weights and reproducible calculation rules.

## Six dimensions

- **Data residency**: storage location, operator jurisdiction and secondary access paths
- **Vendor independence**: exportability, replaceability, exit terms and concentration
- **DNS and network integrity**: resolver operator, encrypted DNS, telemetry and egress control
- **Key management**: key custody, encryption coverage, rotation and plaintext access
- **AI inference**: inference location, retention for training and audit logging
- **Regulatory mapping**: documented links to GDPR, NIS2 and EU AI Act duties where applicable

## Quickstart

```bash
pip install -e ".[dev]"
python -m nss score examples/municipality-example.json --pretty
```

Python usage:

```python
import json
from pathlib import Path
from nss import score

assessment = json.loads(Path("examples/municipality-example.json").read_text(encoding="utf-8"))
result = score(assessment)
print(result["composite_score"], result["grade"])
```

## Project status

Early development. Scoring definition `0.1.0-draft`. First stable release planned for 2027.

## Documentation

- [Methodology](docs/methodology.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Origin

The scoring approach originates from sovereignty assessments carried out by bayata Technologies. This repository is an independent, clean open source implementation and contains no proprietary code.

## Licence

MIT
