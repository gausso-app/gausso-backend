# ============================================================
# Gausso Backend - Veritabanı Modelleri (Tüm import'lar)
# ============================================================
# Alembic migration'larının modelleri otomatik keşfedebilmesi
# için tüm model modülleri buraya import edilmelidir.
# ============================================================

from app.db.session import Base  # noqa: F401

# Tüm modeller buraya import edilmelidir (Alembic keşfi + create_all için)
from app.models.user import User          # noqa: F401
# from app.models.lesson import Lesson    # noqa: F401  ← ileride eklenecek
# from app.models.quiz import Quiz        # noqa: F401  ← ileride eklenecek
