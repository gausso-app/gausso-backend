# ============================================================
# Gausso Backend - Kullanıcı Modeli (User Model)
# ============================================================
# SQLAlchemy ORM modeli. Veritabanındaki 'users' tablosunu temsil eder.
# Oyunlaştırma alanları: score (puan) ve level (seviye).
# ============================================================

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    """
    Gausso kullanıcı tablosu.

    Temel kimlik bilgilerinin yanı sıra oyunlaştırma
    mekanizması için score ve level alanlarını barındırır.
    """

    __tablename__ = "users"

    # --- Kimlik ---
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Otomatik artan birincil anahtar",
    )

    # --- Kimlik Bilgileri ---
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Kullanıcı adı (benzersiz)",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="E-posta adresi (benzersiz)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt ile hashlenmiş şifre",
    )

    # --- Oyunlaştırma (Gamification) ---
    score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="Kullanıcının toplam puanı (istatistik çözdükçe artar)",
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
        comment="Kullanıcının mevcut seviyesi (1'den başlar)",
    )

    # --- Durum ---
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
        comment="Hesap aktif mi? (soft delete için kullanılabilir)",
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username='{self.username}' "
            f"level={self.level} score={self.score}>"
        )
