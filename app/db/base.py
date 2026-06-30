# ============================================================
# Gausso Backend - Veritabanı Modelleri (Tüm import'lar)
# ============================================================
# Alembic migration'larının modelleri otomatik keşfedebilmesi
# için tüm model modülleri buraya import edilmelidir.
# ============================================================

from app.db.session import Base  # noqa: F401

# İleride modeller eklendikçe buraya import eklenecek:
# from app.models.user import User          # noqa: F401
# from app.models.lesson import Lesson      # noqa: F401
# from app.models.quiz import Quiz          # noqa: F401
