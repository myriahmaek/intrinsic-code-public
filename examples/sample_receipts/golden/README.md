# Golden samples (test-keypair-signed)

These are **factory-golden samples**: synthetic builds ("TestApp", a
golden two-lane workspace) produced by Intrinsic Code's own regression
battery. They contain **zero customer content** and exist to show the
artifact structure and the verification flow.

Unlike the canary receipt one directory up (signed with the **production**
keypair), these are signed with the **test keypair**
(`algorithm: Ed25519-test`, `public_key_id: intrinsiccode-test-2026-Q2`,
published in `.well-known/signing-keys.json`) — published precisely so
they verify end-to-end. The verification mechanics are identical for both
grades; the signature block always tells you which keypair signed what.

| File | What it shows |
|---|---|
| `validation_receipt.sample.json` | A per-lane external Validation Receipt: enforcement summary, constitutional traces, external-standards evidence, release status, signature block. |
| `parity_attestation.sample.json` | The cross-lane parity attestation binding both lane receipts' signed hashes: category results, findings, signature block. |

Verify them with `verifier/verify_receipt.py` (see `/VERIFY.md`) or:

```
POST https://api.intrinsiccode.com/api/v1/verify
Content-Type: application/json

<paste the sample JSON>
```

Change any byte and verification fails — try it.
