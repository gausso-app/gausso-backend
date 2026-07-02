# ============================================================
# Gausso Backend - Auth Router (Kimlik Doğrulama)
# ============================================================
# POST /auth/login  → Kullanıcı adı/e-posta + şifre ile giriş,
#                     başarılıysa JWT access token döndürür.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter(
    prefix="/auth",
    tags=["Kimlik Doğrulama"],
)


# ============================================================
# POST /api/v1/auth/login  — Kullanıcı Girişi
# ============================================================
@router.post(
    "/login",
    response_model=Token,
    summary="Kullanıcı girişi (JWT token al)",
    description=(
        "Kullanıcı adı (veya e-posta) ve şifre ile kimlik doğrulaması yapar. "
        "Başarılı girişte, korumalı endpoint'lere erişmek için kullanılacak "
        "JWT Bearer token döndürür. "
        "Swagger UI'da 'Authorize' butonunu kullanarak bu token'ı otomatik ekleyebilirsiniz."
    ),
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    OAuth2 PasswordFlow ile giriş endpoint'i.

    OAuth2PasswordRequestForm alanları:
        - username : Kullanıcı adı VEYA e-posta adresi
        - password : Düz metin şifre

    Akış:
    1. username ile kullanıcıyı bul (önce username, sonra email dene)
    2. Şifreyi bcrypt ile doğrula
    3. Hesap aktiflik kontrolü
    4. JWT access token oluştur ve döndür
    """
    # --- 1. Kullanıcıyı Bul (username veya email) ---
    # Önce username'e göre ara
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    # Bulunamazsa email'e göre ara
    if user is None:
        result = await db.execute(
            select(User).where(User.email == form_data.username)
        )
        user = result.scalar_one_or_none()

    # --- 2. Kimlik Doğrulaması ---
    # Kullanıcı bulunamadı veya şifre yanlış → aynı hata (güvenlik gereği)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı/e-posta veya şifre hatalı.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- 3. Hesap Aktiflik Kontrolü ---
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu hesap devre dışı bırakılmış. Lütfen yönetici ile iletişime geçin.",
        )

    # --- 4. JWT Token Oluştur ---
    access_token = create_access_token(subject=user.id)

    return Token(access_token=access_token, token_type="bearer")
