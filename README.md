# Nexus Sovereignty Score (NSS)

An open Python library and versioned schema for measuring digital sovereignty across infrastructure stacks.

## What it measures

NSS evaluates infrastructure across six dimensions:

- **Data residency**: where data physically sits and under which legal jurisdiction
- **Vendor independence**: how replaceable each critical service is
- **DNS and network integrity**: whether DNS resolution leaks to foreign resolvers
- **Cryptographic key management**: whether key material is managed locally or by a vendor
- **AI inference sovereignty**: whether AI processing stays on-premise
- **Regulatory compliance mapping**: how the overall picture maps to DSGVO, NIS2 and the EU AI Act

## Status

Active development. Initial release targeted Q2 2027.

This library is being extracted from the Nexus Suite (bayatatech.com), where the scoring engine has been running in production since August 2026.

## Licence

MIT
