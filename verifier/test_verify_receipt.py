"""Isolated verifier regressions, not real or publishable Receipt examples.

Fixtures use an ephemeral in-memory signing key and a temporary public-key
manifest. They exercise cryptography and key-role policy without any factory
run, production key, network access, or modification of repository samples.

Run from the repository root with existing verifier dependencies installed:
    python -m unittest discover -s verifier -p test_verify_receipt.py
"""

import base64
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import rfc8785
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import verify_receipt as verifier


class ProductionKeyAcceptanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="receipt-verifier-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest_path = self.root / "signing-keys.json"
        self.private_key = Ed25519PrivateKey.generate()
        self.public_pem = (
            self.private_key.public_key()
            .public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("ascii")
        )
        manifest_patch = patch.object(
            verifier, "SIGNING_KEYS_MANIFEST", self.manifest_path
        )
        manifest_patch.start()
        self.addCleanup(manifest_patch.stop)

    def write_manifest(self, role):
        entry = {
            "public_key_id": "synthetic-fixture-key",
            "pem_format": self.public_pem,
        }
        if role is not None:
            entry["role"] = role
        self.manifest_path.write_text(json.dumps({"keys": [entry]}), encoding="utf-8")

    def signed_fixture(self, label="Ed25519"):
        receipt = {"fixture": "Synthetic verifier regression only", "signature": None}
        digest = hashlib.sha256(rfc8785.dumps(receipt)).digest()
        receipt["signature"] = {
            "algorithm": label,
            "public_key_id": "synthetic-fixture-key",
            "signed_payload_hash": "sha256:" + digest.hex(),
            "signature": base64.b64encode(self.private_key.sign(digest)).decode(
                "ascii"
            ),
        }
        return receipt

    def test_role_controls_production_acceptance_for_both_labels(self):
        for role in ("production", "test", None, "staging", "Production"):
            self.write_manifest(role)
            for label in ("Ed25519", "Ed25519-test"):
                with self.subTest(role=role, label=label):
                    accepted, diagnostic = verifier.verify_receipt(
                        self.signed_fixture(label)
                    )
                    self.assertEqual(accepted, role == "production")
                    if role == "production":
                        self.assertTrue(diagnostic.startswith("Verified."))
                    else:
                        self.assertIn("Signature valid", diagnostic)
                        self.assertIn("not a production Receipt", diagnostic)
                        self.assertFalse(diagnostic.startswith("Verified."))

    def test_tampering_never_claims_a_valid_signature(self):
        for role in ("production", "test"):
            self.write_manifest(role)
            for field in ("payload", "hash", "signature"):
                with self.subTest(role=role, tampered=field):
                    receipt = self.signed_fixture()
                    if field == "payload":
                        receipt["fixture"] = "Changed after signing"
                    elif field == "hash":
                        receipt["signature"]["signed_payload_hash"] = (
                            "sha256:" + "00" * 32
                        )
                    else:
                        signature = bytearray(
                            base64.b64decode(receipt["signature"]["signature"])
                        )
                        signature[0] ^= 1
                        receipt["signature"]["signature"] = base64.b64encode(
                            signature
                        ).decode("ascii")
                    accepted, diagnostic = verifier.verify_receipt(receipt)
                    self.assertFalse(accepted)
                    self.assertNotIn("Signature valid", diagnostic)
                    self.assertIn(
                        "Signature does not verify"
                        if field == "signature"
                        else "Hash mismatch",
                        diagnostic,
                    )

    def test_other_algorithm_and_unsigned_labels_remain_refused(self):
        self.write_manifest("production")
        for label in ("RSA", "Ed25519-unsigned", [], {}):
            with self.subTest(label=label):
                accepted, diagnostic = verifier.verify_receipt(
                    self.signed_fixture(label)
                )
                self.assertFalse(accepted)
                self.assertNotIn("Signature valid", diagnostic)

    def test_malformed_key_manifests_are_cleanly_refused(self):
        self.write_manifest("production")
        valid_entry = json.loads(self.manifest_path.read_text(encoding="utf-8"))[
            "keys"
        ][0]
        malformed = ["{"]
        malformed.extend(json.dumps(value) for value in (None, [], "keys", 1, True))
        malformed.extend(
            json.dumps({"keys": value}) for value in (None, {}, "keys", 1, True)
        )
        for entry in (None, [], "key", 1, True):
            malformed.append(json.dumps({"keys": [entry, valid_entry]}))
            malformed.append(json.dumps({"keys": [valid_entry, entry]}))
        receipt = self.signed_fixture()
        for contents in malformed:
            with self.subTest(manifest=contents):
                self.manifest_path.write_text(contents, encoding="utf-8")
                accepted, diagnostic = verifier.verify_receipt(receipt)
                self.assertFalse(accepted)
                self.assertTrue(
                    diagnostic.startswith("Signing-keys manifest is malformed:")
                )
        self.manifest_path.write_bytes(b"\xff")
        accepted, diagnostic = verifier.verify_receipt(receipt)
        self.assertFalse(accepted)
        self.assertTrue(diagnostic.startswith("Signing-keys manifest is malformed:"))

    def test_cli_exit_status_tracks_production_acceptance(self):
        path = self.root / "synthetic-fixture.json"
        path.write_text(json.dumps(self.signed_fixture()), encoding="utf-8")
        for role, expected in (("production", 0), ("test", 1)):
            self.write_manifest(role)
            with (
                self.subTest(role=role),
                patch.object(verifier.sys, "argv", ["verify_receipt.py", str(path)]),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(verifier.main(), expected)


if __name__ == "__main__":
    unittest.main()
