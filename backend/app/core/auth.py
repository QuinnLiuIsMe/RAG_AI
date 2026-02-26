from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from app.core.config import Settings


class AuthError(Exception):
    pass


@dataclass
class AuthPrincipal:
    subject: str
    issuer: str | None
    audience: str | None


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode((raw + padding).encode("utf-8"))


def _verify_hs256_signing_input(signing_input: bytes, signature: bytes, secret: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return hmac.compare_digest(expected, signature)


def decode_jwt(token: str, settings: Settings) -> AuthPrincipal:
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError("invalid JWT format")

    header_bytes = _b64url_decode(parts[0])
    payload_bytes = _b64url_decode(parts[1])
    signature = _b64url_decode(parts[2])
    signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")

    try:
        header = json.loads(header_bytes.decode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AuthError("invalid JWT payload") from exc

    alg = str(header.get("alg", "")).upper()
    if settings.auth_verify_signature:
        if alg != "HS256":
            raise AuthError("unsupported JWT algorithm")
        if not settings.auth_hs256_secret:
            raise AuthError("missing auth secret")
        if not _verify_hs256_signing_input(signing_input, signature, settings.auth_hs256_secret):
            raise AuthError("JWT signature verification failed")

    exp = payload.get("exp")
    if isinstance(exp, (int, float)) and time.time() >= float(exp):
        raise AuthError("JWT expired")

    issuer = payload.get("iss")
    audience = payload.get("aud")
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise AuthError("JWT missing subject")

    if settings.auth_issuer and issuer != settings.auth_issuer:
        raise AuthError("JWT issuer mismatch")
    if settings.auth_audience and audience != settings.auth_audience:
        raise AuthError("JWT audience mismatch")

    return AuthPrincipal(
        subject=subject,
        issuer=issuer if isinstance(issuer, str) else None,
        audience=audience if isinstance(audience, str) else None,
    )
