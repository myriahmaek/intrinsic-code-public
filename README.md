# Intrinsic Code — Public Verification Artifacts

**Everyone is generating code. We're generating proof.**

This repository contains the public verification surface for [Intrinsic Code](https://intrinsiccode.com) — the AI platform whose generated mobile applications ship with cryptographically-signed Validation Receipts.

The core generation engine, agent prompts, and orchestration logic remain private during active development. This repository contains the public artifacts needed to verify that an Intrinsic Code Validation Receipt was signed by Intrinsic Code and has not been tampered with.

The proof layer is public. The engine is private.

---

## What's here

```
intrinsic-code-public/
├── examples/sample_receipts/        Real signed Validation Receipts from canary builds
├── keys/prod/                       Public signing keys (Ed25519)
├── .well-known/signing-keys.json    Public key manifest
├── mappings/                        Constitution → external standards mapping
├── ledger/                          Live KPI ledger (RUN_LEDGER.csv)
├── verifier/                        Standalone verification script
├── VERIFY.md                        How to verify a Receipt yourself
└── LICENSE                          MIT
```

## What's NOT here

This repository deliberately does NOT contain:

- The Intrinsic Code generation engine
- Agent prompts (Sequoia, Scribe, Scaffolder, Coder, Receipt Aggregator, Auditor)
- The Security Constitution (cited by version in Receipts; full text is private)
- Architecture specifications
- Any private signing keys

The proof layer is public. The engine is private. That separation is intentional.

---

## How verification works

Every Intrinsic Code application generation produces a **Validation Receipt** — a JSON document enumerating enforcement gates fired during generation, mapped to internal constitutional controls and external standards references including OWASP MASVS, NIST SP 800-163, NIAP Protection Profiles, ISO/IEC 27034, Apple App Store Guidelines, and Google Play policies.

Receipts are cryptographically signed using **Ed25519** with **RFC 8785 (JCS)** canonicalization. Anyone with the published public signing key can verify that a Receipt was signed by Intrinsic Code and has not been modified after signing.

The first public cryptographically-signed Intrinsic Code Validation Receipt is in this repository at:

```
examples/sample_receipts/focusblock-android-canary.json
```

To verify it yourself, see [VERIFY.md](VERIFY.md).

---

## Security note on signing keys

Only public keys are published in this repository. Intrinsic Code private signing keys are never committed and are required to produce valid new Receipts. The cryptography (Ed25519) is mathematically designed so that the public key cannot be used to derive the private key — publishing the public key is safe by design, not by oversight.

---

## What a Receipt does NOT claim

Per the Validation Receipt v0.1.1 specification, a Receipt validates **enforcement gates fired during generation**. It does not certify:

- Runtime behavior of the application after deployment
- Third-party dependency security beyond declared provenance review
- Post-generation modifications to the code
- NIAP, FedRAMP, SOC 2, MASA, or other external compliance certifications (those are separate processes performed by accredited third parties)
- Vulnerability-free status

External standards mappings reflect Intrinsic Code's internal review of public control text and have not yet been third-party audited. Customers using these mappings in regulated procurement should validate independently.

---

## License

MIT for code in `verifier/`. The receipts, public keys, and mapping data are public artifacts.

---

*Intrinsic Code is a product of Be For Real Media LLC. Built in Olympia, Washington.*
