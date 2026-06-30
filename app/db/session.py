# ============================================================
# Gausso Backend - Veritabanı Bağlantısı (Database Connection)
# ============================================================
# SQLAlchemy 2.0 async motorunu ve session yönetimini içerir.
# Her API isteği için bağımsız bir session açılıp kapanır.
# ============================================================

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# --- Async Engine ---
# Veritabanına bağlanan motor nesnesini oluştur.
# pool_pre_ping=True: bozuk bağlantıları otomatik yeniler.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,   # DEBUG modda SQL sorgularını logla
    future=True,
    pool_pre_ping=True,
)

# --- Session Factory ---
# Her request için kullanılacak session fabrikası.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # commit sonrası objeleri bellekten silme
)


# --- Base Model ---
# Tüm SQLAlchemy modelleri bu sınıftan türeyecek.
class Base(DeclarativeBase):
    pass


# --- Dependency (FastAPI'de Kullanım) ---
async def get_db() -> AsyncSession:
    """
    FastAPI dependency injection ile her endpoint'e
    temiz bir veritabanı session'ı sağlar.

    Kullanım:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
