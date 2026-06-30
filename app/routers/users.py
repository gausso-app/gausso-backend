# ============================================================
# Gausso Backend - Kullanıcı Router'ı (Users Router)
# ============================================================
# POST /users  → Yeni kullanıcı oluştur
# GET  /users  → Kullanıcıları listele
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserSummary

router = APIRouter(
    prefix="/users",
    tags=["Kullanıcılar"],
)


# ============================================================
# Yardımcı: Basit Parola Hash (Geçici - passlib ile değiştirilecek)
# ============================================================
def _fake_hash(password: str) -> str:
    """
    Geliştirme aşamasında geçici hash fonksiyonu.
    Üretimde passlib/bcrypt kullanılacak:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"])
        pwd_context.hash(password)
    """
    return f"fakehashed_{password}"


# ============================================================
# POST /api/v1/users  — Yeni Kullanıcı Oluştur
# ============================================================
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı oluştur",
    description=(
        "Yeni bir Gausso kullanıcısı kaydeder. "
        "Kullanıcı adı ve e-posta benzersiz olmalıdır. "
        "Başlangıç puanı 0, seviyesi 1'dir."
    ),
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Yeni kullanıcı oluşturma endpoint'i.

    - Şifreyi hashler (şu an fake, ileride bcrypt)
    - username/email çakışmasında 409 döndürür
    - Başarılıysa oluşturulan kullanıcıyı 201 ile döndürür
    """
    hashed_pw = _fake_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        # score=0 ve level=1 model default'larından gelir
    )

    db.add(new_user)

    try:
        await db.flush()   # DB'ye gönder, henüz commit etme
        await db.refresh(new_user)  # id gibi sunucu taraflı değerleri al
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu kullanıcı adı veya e-posta adresi zaten kullanımda.",
        )

    return UserResponse.model_validate(new_user)


# ============================================================
# GET /api/v1/users  — Kullanıcı Listesi
# ============================================================
@router.get(
    "",
    response_model=list[UserSummary],
    summary="Kullanıcıları listele",
    description=(
        "Kayıtlı tüm kullanıcıları (veya aktif olanları) puanlarına göre sıralar. "
        "Hassas bilgiler (parola, e-posta) gizlenir."
    ),
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(default=20, ge=1, le=100, description="Döndürülecek maksimum kayıt"),
    only_active: bool = Query(default=True, description="Sadece aktif kullanıcıları göster"),
) -> list[UserSummary]:
    """
    Kullanıcı listeleme endpoint'i.

    - Puanlara göre azalan sırayla sıralama (liderlik tablosu mantığı)
    - Sayfalama: skip & limit parametreleri
    - only_active=True (varsayılan) ile sadece aktif kullanıcılar listelenir
    """
    stmt = select(User).order_by(User.score.desc()).offset(skip).limit(limit)

    if only_active:
        stmt = stmt.where(User.is_active.is_(True))

    result = await db.execute(stmt)
    users = result.scalars().all()

    return [UserSummary.model_validate(u) for u in users]
