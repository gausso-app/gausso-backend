# ============================================================
# Gausso Backend - Kullanıcı Şemaları (User Schemas)
# ============================================================
# Pydantic v2 şemaları. Request body doğrulama ve response
# serializasyonu için kullanılır. ORM modelinden bağımsızdır.
# ============================================================

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================
# Ortak / Temel Şema
# ============================================================
class UserBase(BaseModel):
    """
    Tüm kullanıcı şemalarının paylaştığı temel alanlar.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["gausso_user"],
        description="Kullanıcı adı (3-50 karakter, harf/rakam/alt çizgi)",
    )
    email: EmailStr = Field(
        ...,
        examples=["user@gausso.com"],
        description="Geçerli bir e-posta adresi",
    )


# ============================================================
# Oluşturma Şeması (Request)
# ============================================================
class UserCreate(UserBase):
    """
    POST /users endpoint'ine gönderilecek veri.
    Şifre düz metin olarak alınır; servis katmanında hashlenir.
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["G@uss0_2025!"],
        description="Şifre (en az 8 karakter)",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Temel şifre gücü kontrolü.
        En az bir büyük harf, bir küçük harf ve bir rakam içermeli.
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Şifre en az bir büyük harf içermelidir.")
        if not any(c.islower() for c in v):
            raise ValueError("Şifre en az bir küçük harf içermelidir.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Şifre en az bir rakam içermelidir.")
        return v


# ============================================================
# Güncelleme Şeması (Request - Kısmi)
# ============================================================
class UserUpdate(BaseModel):
    """
    PATCH /users/{id} için isteğe bağlı güncelleme alanları.
    Yalnızca gönderilen alanlar güncellenir.
    """

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: EmailStr | None = None
    is_active: bool | None = None


# ============================================================
# Yanıt Şeması (Response)
# ============================================================
class UserResponse(UserBase):
    """
    API'den döndürülecek kullanıcı verisi.
    Hassas alanlar (hashed_password) gizlenir.
    """

    id: int = Field(..., description="Veritabanı birincil anahtarı")
    score: int = Field(
        default=0,
        ge=0,
        description="Toplam puan (istatistik çözdükçe artar)",
    )
    level: int = Field(
        default=1,
        ge=1,
        description="Mevcut seviye",
    )
    is_active: bool = Field(default=True, description="Hesap aktif mi?")

    # Pydantic v2'de ORM nesnelerini okumak için
    model_config = {"from_attributes": True}


# ============================================================
# Özet Şema (Listeler için hafif versiyon)
# ============================================================
class UserSummary(BaseModel):
    """
    Kullanıcı listesi endpoint'leri için kompakt yanıt.
    Yalnızca temel oyunlaştırma bilgilerini içerir.
    """

    id: int
    username: str
    score: int
    level: int
    is_active: bool

    model_config = {"from_attributes": True}
