# How to Verify a Validation Receipt

This document walks you through verifying that a Validation Receipt was genuinely signed by Intrinsic Code and has not been tampered with.

You will need:

- Python 3.9 or higher
- The `cryptography` and `rfc8785` packages
- A Validation Receipt JSON file
- The Intrinsic Code production public key (in this repo)

---

## Quick start

From the root of this repository:

```bash
pip install cryptography rfc8785
python verifier/verify_receipt.py examples/sample_receipts/focusblock-android-canary.json
```

You should see:

```
✓ Verified
  algorithm:        Ed25519
  public_key_id:    intrinsiccode-prod-2026-Q2
  signed_payload_hash: sha256:ec5928e1b8e996729b75c5ae3f6f41310fbe2269981f72585a623cf26fb50c2a
```

If you see anything else, the Receipt is either tampered with, signed by a different key, or malformed.

---

## What the verifier does

The `verifier/verify_receipt.py` script implements the inverse of the signing process specified in Validation Receipt v0.1.1 §5.4:

1. **Reads the Receipt JSON** and extracts the `signature` block.
2. **Looks up the public key** for the Receipt's `signature.public_key_id` in the `.well-known/signing-keys.json` manifest.
3. **Sets the signature field to null** in a working copy of the Receipt.
4. **Canonicalizes the working copy** using RFC 8785 (JCS) — produces deterministic byte-exact output regardless of key order or whitespace in the original JSON.
5. **Computes the SHA-256 hash** of the canonical bytes.
6. **Compares the recomputed hash** against the `signed_payload_hash` embedded in the Receipt's signature block. Mismatch means the Receipt was modified after signing.
7. **Verifies the Ed25519 signature** against the recomputed hash using the public key. Mismatch means the signature is invalid (wrong key, or signature was tampered with).

If both checks pass, the Receipt matches the signed payload hash and was signed by the published Intrinsic Code key.

---

## Verifying a Receipt you obtained elsewhere

If you have a Receipt JSON file from somewhere other than this repository (for example, attached to a generated application you are evaluating), you can verify it the same way.

```bash
python verifier/verify_receipt.py path/to/your/receipt.json
```

The verifier resolves the public key from the manifest in this repository, so as long as the Receipt was signed by an Intrinsic Code identity that is published in `.well-known/signing-keys.json`, verification will work.

---

## Possible verification failures

| Output | Meaning |
|--------|---------|
| `✗ Hash mismatch` | The Receipt data changed after signing. Formatting-only changes such as whitespace or key order should not trigger this because Receipts are canonicalized with RFC 8785 before hashing. |
| `✗ Signature does not verify` | The hash matched but the cryptographic signature is invalid. Likely tampering or a wrong public key. |
| `✗ public_key_id not found in manifest` | The Receipt was signed by a key Intrinsic Code does not publish. Either the key was rotated and is not yet in the manifest, or the Receipt is not from Intrinsic Code at all. |
| `✗ Receipt was emitted in 'unsigned' mode` | The Receipt is a placeholder from a pre-Phase-5-Commit-3 build. These exist in early development repositories but should not appear on production deliverables. |
| `✗ Unsupported signature algorithm` | The Receipt declares an algorithm the verifier does not implement. Currently only Ed25519 is supported. |

---

## Verification by alternative means

The standalone Python script is the simplest way to verify a Receipt, but the cryptography is open and standard. You can verify a Receipt with:

- Any Ed25519-compatible signing library (Go, Rust, Node.js, etc.)
- Any RFC 8785 (JCS) canonicalization library
- A SHA-256 hash function (every standard library has one)

The required steps are documented in Validation Receipt v0.1.1 §5.4. The reference implementation in this repository is one valid implementation; you are encouraged to write your own if you want defense-in-depth verification.

---

## Reporting verification failures

If you obtain a Receipt that claims to be from Intrinsic Code and it fails verification, that is information worth knowing — for you and for us.

Open an issue in this repository describing what you observed (do not include the suspect Receipt content if it might contain sensitive data; a description of the failure mode is sufficient).

---

*Validation Receipt design specification: v0.1.1. Constitution version cited in receipts: v0.4.*
