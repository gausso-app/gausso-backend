# ============================================================
# Gausso Backend - Auth Şemaları (Auth Schemas)
# ============================================================
# Login endpoint'inin yanıt şeması burada tanımlanır.
# ============================================================

from pydantic import BaseModel, Field


# ============================================================
# Token Yanıt Şeması (Response)
# ============================================================
class Token(BaseModel):
    """
    POST /auth/login endpoint'inden döndürülecek JWT token verisi.
    OAuth2 standardı: access_token + token_type zorunlu alanlar.
    """

    access_token: str = Field(
        ...,
        description="İmzalanmış JWT erişim token'ı",
    )
    token_type: str = Field(
        default="bearer",
        description="Token türü (OAuth2 standardı gereği 'bearer')",
    )


# ============================================================
# Token Payload Şeması (İç Kullanım)
# ============================================================
class TokenData(BaseModel):
    """
    JWT token'ından çözülen veri.
    deps.py içinde get_current_user tarafından dahili olarak kullanılır.
    """

    user_id: int | None = None
