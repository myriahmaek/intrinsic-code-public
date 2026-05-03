#!/usr/bin/env python3
"""Standalone Validation Receipt verifier for Intrinsic Code.

This is a minimal reference implementation. It performs only signature
verification — no aggregation, no agent logic, no telemetry. Anyone can
audit this script in full to confirm the verification process is honest.

Usage:
    python verify_receipt.py <path/to/receipt.json>

Requirements:
    pip install cryptography rfc8785

Validation Receipt specification: v0.1.1 §5.4.
"""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import rfc8785
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


SIGNING_KEYS_MANIFEST = Path(__file__).resolve().parent.parent / ".well-known" / "signing-keys.json"


def verify_receipt(receipt: dict) -> tuple[bool, str]:
    """Returns (valid, diagnostic). Never raises on bad input."""

    sig_block = receipt.get("signature")
    if not isinstance(sig_block, dict):
        return False, "Receipt is missing a signature block."

    algo = sig_block.get("algorithm", "")
    if algo == "Ed25519-unsigned":
        return False, "Receipt was emitted in 'unsigned' mode (placeholder, not signed)."
    if algo != "Ed25519":
        return False, f"Unsupported signature algorithm: {algo!r}. This verifier supports Ed25519 only."

    key_id = sig_block.get("public_key_id", "")
    embedded_hash = sig_block.get("signed_payload_hash", "")
    embedded_sig_b64 = sig_block.get("signature", "")

    # Look up the public key in the manifest
    try:
        manifest = json.loads(SIGNING_KEYS_MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, f"Signing-keys manifest not found at {SIGNING_KEYS_MANIFEST}."
    except json.JSONDecodeError as e:
        return False, f"Signing-keys manifest is malformed: {e}."

    pub_key_pem = None
    for entry in manifest.get("keys", []):
        if entry.get("public_key_id") == key_id:
            pub_key_pem = entry.get("pem_format", "")
            break
    if pub_key_pem is None:
        return False, f"public_key_id {key_id!r} not found in manifest."

    # Recompute the canonical bytes and hash
    receipt_for_hash = json.loads(json.dumps(receipt))  # deep copy
    receipt_for_hash["signature"] = None
    canonical = rfc8785.dumps(receipt_for_hash)
    recomputed_hash = "sha256:" + hashlib.sha256(canonical).hexdigest()

    if recomputed_hash != embedded_hash:
        return False, f"Hash mismatch: receipt was modified after signing.\n  embedded:    {embedded_hash}\n  recomputed:  {recomputed_hash}"

    # Verify the Ed25519 signature
    try:
        import base64
        sig_bytes = base64.b64decode(embedded_sig_b64)
        pub_key = serialization.load_pem_public_key(pub_key_pem.encode("utf-8"))
        if not isinstance(pub_key, Ed25519PublicKey):
            return False, "Public key in manifest is not an Ed25519 key."
        pub_key.verify(sig_bytes, hashlib.sha256(canonical).digest())
    except InvalidSignature:
        return False, "Signature does not verify against the public key. Receipt may be forged."
    except Exception as e:
        return False, f"Verification failed with an unexpected error: {e}"

    return True, (
        f"Verified.\n"
        f"  algorithm:           {algo}\n"
        f"  public_key_id:       {key_id}\n"
        f"  signed_payload_hash: {embedded_hash}"
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python verify_receipt.py <path/to/receipt.json>", file=sys.stderr)
        return 2

    receipt_path = Path(sys.argv[1])
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"✗ Receipt file not found: {receipt_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"✗ Receipt JSON is malformed: {e}", file=sys.stderr)
        return 1

    valid, diagnostic = verify_receipt(receipt)
    print(("✓ " if valid else "✗ ") + diagnostic)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
