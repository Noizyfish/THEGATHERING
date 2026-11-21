"""Human Voice Sovereignty (HVS) consent records.

A speaker's voice never enters NOIZYVOX without a signed consent record that names the scope.
Records are JSON, signed with the speaker's Ed25519 key (generated on first use, kept in the session's
`keys/` dir or the speaker's own device). Every exported clip carries the consent id; the dataset
builder refuses clips whose consent is missing, expired, revoked, or out of scope.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

SCOPES = ("record", "transcribe", "train", "synthesize", "commercial", "share")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Consent:
    speaker_id: str                    # track id or stable pseudonym (never the legal name in clear)
    display_name: str
    scopes: list[str]
    session_id: str
    granted_at: str = field(default_factory=now)
    expires_at: str | None = None
    revoked_at: str | None = None
    name_hash: str | None = None       # sha256(legal name + salt) so identity can be proven, not read
    salt: str = field(default_factory=lambda: secrets.token_hex(8))
    terms_version: str = "HVS-1.0"
    consent_id: str = field(default_factory=lambda: "cns_" + secrets.token_hex(8))
    public_key: str | None = None      # hex, Ed25519
    signature: str | None = None       # hex over canonical payload

    def payload(self) -> bytes:
        d = asdict(self)
        d.pop("signature", None)
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode()

    def active(self, at: str | None = None) -> bool:
        at = at or now()
        if self.revoked_at and self.revoked_at <= at:
            return False
        if self.expires_at and self.expires_at <= at:
            return False
        return True

    def allows(self, *scopes: str) -> bool:
        return self.active() and all(s in self.scopes for s in scopes)


def set_legal_name(c: Consent, legal_name: str) -> None:
    c.name_hash = hashlib.sha256((legal_name.strip().lower() + c.salt).encode()).hexdigest()


def new_key(path: Path) -> Ed25519PrivateKey:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = Ed25519PrivateKey.generate()
    path.write_bytes(key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()))
    path.chmod(0o600)
    return key


def load_key(path: Path) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(path.read_bytes()) if path.exists() else new_key(path)


def sign(c: Consent, key: Ed25519PrivateKey) -> Consent:
    c.public_key = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
    c.signature = key.sign(c.payload()).hex()
    return c


def verify(c: Consent) -> bool:
    if not (c.public_key and c.signature):
        return False
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(c.public_key)).verify(bytes.fromhex(c.signature), c.payload())
        return True
    except Exception:
        return False


def save(c: Consent, dir_: Path) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    p = dir_ / f"{c.consent_id}.json"
    p.write_text(json.dumps(asdict(c), indent=2))
    return p


def load_all(dir_: Path) -> dict[str, Consent]:
    out: dict[str, Consent] = {}
    if not dir_.exists():
        return out
    for p in sorted(dir_.glob("cns_*.json")):
        c = Consent(**json.loads(p.read_text()))
        if verify(c):
            out[c.speaker_id] = c       # latest file per speaker wins (sorted by id → use granted_at below)
    return out


def latest_for(consents: dict[str, Consent], speaker_id: str) -> Consent | None:
    return consents.get(speaker_id)


def revoke(c: Consent, key: Ed25519PrivateKey) -> Consent:
    c.revoked_at = now()
    return sign(c, key)
