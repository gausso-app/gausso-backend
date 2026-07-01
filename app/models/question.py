# ============================================================
# Gausso Backend - Soru Modeli (Question Model)
# ============================================================
# SQLAlchemy ORM modeli. Veritabanındaki 'questions' tablosunu
# temsil eder. İstatistik soruları ve puan mekanizmasını içerir.
# ============================================================

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Question(Base):
    """
    Gausso istatistik soruları tablosu.

    Her soru bir konuya (topic) ve zorluk seviyesine (difficulty_level)
    sahiptir. Doğru cevaplanması durumunda kullanıcıya points_awarded
    kadar puan verilir.
    """

    __tablename__ = "questions"

    # --- Birincil Anahtar ---
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Otomatik artan birincil anahtar",
    )

    # --- Konu ---
    topic: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Sorunun ait olduğu istatistik konusu (örn: 'Olasılık', 'Dağılımlar')",
    )

    # --- Zorluk Seviyesi ---
    difficulty_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Zorluk seviyesi (1=çok kolay, 5=çok zor)",
    )

    # --- Soru Metni ---
    content: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
        comment="Soru metni",
    )

    # --- Doğru Cevap ---
    correct_answer: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Sorunun doğru cevabı",
    )

    # --- Puan ---
    points_awarded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
        server_default="10",
        comment="Bu soru doğru bilindiğinde verilecek puan",
    )

    def __repr__(self) -> str:
        return (
            f"<Question id={self.id} topic='{self.topic}' "
            f"difficulty={self.difficulty_level} points={self.points_awarded}>"
        )
