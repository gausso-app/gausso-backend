# ============================================================
# Gausso Backend - FastAPI Bağımlılıkları (Dependencies)
# ============================================================
# get_current_user: Gelen Bearer token'ı doğrular ve
# veritabanından ilgili kullanıcıyı döndürür.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

# ============================================================
# OAuth2 Bearer Token Şeması
# ============================================================
# tokenUrl: Swagger UI'ın "Authorize" butonunun yönleneceği adres.
# Bu adres, login endpoint'imizin tam yolu olmalıdır.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


# ============================================================
# get_current_user Bağımlılığı
# ============================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI bağımlılığı. Herhangi bir endpoint'e eklendiğinde:
    1. Authorization başlığından Bearer token'ı çeker.
    2. Token'ı imza ve süre açısından doğrular.
    3. Payload'daki 'sub' alanından user_id okur.
    4. Veritabanından kullanıcıyı çeker ve döndürür.

    Hata durumları:
        - 401 UNAUTHORIZED : Token yok, geçersiz veya süresi dolmuş.
        - 401 UNAUTHORIZED : Token'daki user_id veritabanında bulunamadı.
        - 403 FORBIDDEN     : Hesap aktif değil (is_active=False).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı. Lütfen tekrar giriş yapın.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # --- 1. Token'ı Çöz (Decode) ---
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if user_id_str is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # --- 2. Kullanıcıyı Veritabanından Çek ---
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # --- 3. Hesap Durumu Kontrolü ---
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu hesap devre dışı bırakılmış.",
        )

    return user


# ============================================================
# get_current_active_user (Takma Ad - Alias)
# ============================================================
# Daha okunabilir endpoint imzaları için kullanılabilir.
# Örnek: current_user: User = Depends(get_current_active_user)
get_current_active_user = get_current_user
