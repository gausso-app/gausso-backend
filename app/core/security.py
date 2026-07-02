# ============================================================
# Gausso Backend - Güvenlik Yardımcıları (Security Helpers)
# ============================================================
# Şifre hashleme/doğrulama ve JWT token üretimi bu dosyadadır.
# Tüm kriptografik işlemler buradan merkezi olarak yönetilir.
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# ============================================================
# Şifre Hashleme Bağlamı (Password Hashing Context)
# ============================================================
# bcrypt: Güçlü, tuzlu (salted) ve yavaş bir hash algoritması.
# "deprecated=auto" → eski şemalar otomatik yenilenir.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# Şifre İşlemleri
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Düz metin şifreyi, veritabanındaki hash ile karşılaştırır.

    Args:
        plain_password: Kullanıcının girdiği düz metin şifre
        hashed_password: Veritabanında saklanan bcrypt hash

    Returns:
        bool: Şifreler eşleşiyorsa True, aksi hâlde False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Düz metin şifreyi bcrypt ile hashler.

    Args:
        password: Hashlenecek düz metin şifre

    Returns:
        str: bcrypt ile hashlenmiş şifre
    """
    return pwd_context.hash(password)


# ============================================================
# JWT Token İşlemleri
# ============================================================

def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Süreli bir JWT erişim token'ı oluşturur.

    Token payload'ı:
        - sub  : Kullanıcı kimliği (user id veya username)
        - exp  : Token'ın sona erme zamanı (UTC)
        - iat  : Token'ın oluşturulma zamanı (UTC)
        - type : Token türü ("access")

    Args:
        subject   : Token'ın öznesini temsil eden değer (genellikle user.id)
        expires_delta : Özel süre; verilmezse settings'ten alınır.

    Returns:
        str: İmzalanmış JWT string'i
    """
    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),   # JWT standardı: subject string olmalı
        "exp": expire,
        "iat": now,
        "type": "access",
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
