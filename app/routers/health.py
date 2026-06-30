# ============================================================
# Gausso Backend - Sağlık Kontrolü Router'ı (Health Check)
# ============================================================
# Bu router, sistemin ayakta olup olmadığını kontrol etmek
# için kullanılan endpoint'leri içerir.
# ============================================================

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(
    prefix="/health",
    tags=["Sistem Durumu"],
)


@router.get(
    "",
    summary="Sağlık Kontrolü",
    description="Sunucunun çalışıp çalışmadığını ve temel sistem bilgilerini döndürür.",
)
async def health_check():
    """
    Sistemin sağlık durumunu kontrol eder.
    Monitoring araçları (örn. Kubernetes liveness probe) tarafından kullanılır.
    """
    return {
        "status": "healthy",
        "message": "Gausso API calisıyor!",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
