# ============================================================
# Gausso Backend - Ana Uygulama Giriş Noktası (main.py)
# ============================================================
# Bu dosya FastAPI uygulamasını başlatır, middleware'leri,
# router'ları ve yaşam döngüsü olaylarını yapılandırır.
# ============================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.db import base  # noqa: F401 — modelleri kaydet (User vb.)
from app.db.session import Base, engine
from app.routers import auth, game, health, questions, users
from app.admin import create_admin


# ============================================================
# Yaşam Döngüsü (Lifespan) - Startup & Shutdown
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama başlarken ve kapanırken çalışacak işlemler.
    FastAPI'nin modern 'lifespan' yaklaşımı (eski @on_event yerine).

    Startup: Veritabanı bağlantısını aç, önbellekleri başlat, vb.
    Shutdown: Bağlantıları kapat, kaynakları serbest bırak.
    """
    # --- STARTUP ---
    print("[STARTUP] Gausso API baslatiliyor...")
    print(f"   Ortam    : {settings.ENVIRONMENT}")
    print(f"   Versiyon : {settings.APP_VERSION}")
    print(f"   Debug    : {settings.DEBUG}")

    # Veritabanı tablolarını oluştur (yoksa).
    # Alembic migration'larına geçince bu satır kaldırılacak.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[STARTUP] Veritabani tablolari hazir.")

    print("[STARTUP] Gausso API hazir!\n")

    yield  # Uygulama bu noktada çalışır

    # --- SHUTDOWN ---
    print("\n[SHUTDOWN] Gausso API kapatiliyor...")
    # await engine.dispose()
    print("[SHUTDOWN] Gorusuruz!")


# ============================================================
# FastAPI Uygulama Örneği (Application Instance)
# ============================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    # Swagger UI ve ReDoc adresleri
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ============================================================
# Admin Paneli (/admin)
# ============================================================
# sqladmin entegrasyonu - /admin rotasında yönetim arayüzü
create_admin(app)


# ============================================================
# Middleware'ler
# ============================================================

# CORS: Frontend'in API'ye erişebilmesi için gerekli.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],   # Authorization, Content-Type, vb.
)


# ============================================================
# Router'ların Kayıt Edilmesi (Route Registration)
# ============================================================

# Sağlık kontrolü router'ı - /api/v1/health
app.include_router(health.router, prefix=settings.API_V1_PREFIX)

# Kullanıcı router'ı - /api/v1/users
app.include_router(users.router, prefix=settings.API_V1_PREFIX)

# Soru router'ı - /api/v1/questions
app.include_router(questions.router, prefix=settings.API_V1_PREFIX)

# Kimlik doğrulama router'ı - /api/v1/auth
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

# Oyun motoru router'ı - /api/v1/game
app.include_router(game.router, prefix=settings.API_V1_PREFIX)

# İleride eklenecek router'lar:
# app.include_router(lessons.router,  prefix=settings.API_V1_PREFIX)
# app.include_router(progress.router, prefix=settings.API_V1_PREFIX)


# ============================================================
# Kök Endpoint (Root Endpoint)
# ============================================================
@app.get(
    "/",
    tags=["Genel"],
    summary="Gausso API'ye Hoş Geldiniz",
    description="Uygulamanın temel bilgilerini ve API bağlantılarını döndürür.",
)
async def root() -> JSONResponse:
    """
    Gausso API'nin ana karşılama endpoint'i.
    Sunucu adresine istek atıldığında çalışır.
    """
    return JSONResponse(
        content={
            "status": "success",
            "message": "Gausso API'ye Hos Geldiniz! Istatigiyi ogrenmenin en eglenceli yolu.",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json",
            },
            "endpoints": {
                "health_check": f"{settings.API_V1_PREFIX}/health",
                "auth":         f"{settings.API_V1_PREFIX}/auth/login",
                "users":        f"{settings.API_V1_PREFIX}/users",
                "questions":    f"{settings.API_V1_PREFIX}/questions",
                "game":         f"{settings.API_V1_PREFIX}/game",
            },
        }
    )
