"""Parola hash'leme ve doğrulama (QR-01). Sorumlu: Mert.

Argon2id kullanılır; parola düz metin olarak saklanmaz veya loglanmaz.
"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

# argon2-cffi varsayılanları: Argon2id, RFC 9106 düşük bellek profili.
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Parolayı tuzlu Argon2id hash'ine çevirir; sonuç DB'deki password_hash alanına yazılır."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Parola hash ile eşleşirse True; yanlış parola veya bozuk hash'te False döner (hata fırlatmaz)."""
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False
