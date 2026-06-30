# ============================================================
# Gausso Backend - Uygulama Ayarları (Settings)
# ============================================================
# Bu dosya, tüm ortam değişkenlerini (environment variables)
# merkezi bir yerden yönetir. Değerler .env dosyasından okunur.
# ============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Uygulama genelinde kullanılan tüm ayarlar.
    Pydantic BaseSettings sayesinde .env dosyasından otomatik okunur.
    """

    # --- Uygulama Bilgileri ---
    APP_NAME: str = "Gausso API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Oyunlaştırılmış istatistik öğrenme platformunun backend API'si."
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # --- API Ayarları ---
    API_V1_PREFIX: str = "/api/v1"

    # --- Veritabanı (Database) ---
    # Geliştirme: SQLite | Üretim: PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./gausso_dev.db"

    # --- Güvenlik (Security) ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_A_STRONG_RANDOM_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS Ayarları ---
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # Frontend (React/Next.js geliştirme)
        "http://localhost:5173",  # Frontend (Vite geliştirme)
    ]

    # Pydantic v2: .env dosyasını oku
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Ayarları singleton olarak döndür.
    lru_cache sayesinde ayarlar yalnızca bir kez yüklenir,
    her request'te dosya okuma maliyeti oluşmaz.
    """
    return Settings()


# Kolayca import edilebilmesi için global instance
settings = get_settings()
