# ============================================================
# Gausso Backend - Soru Şemaları (Question Schemas)
# ============================================================
# Pydantic v2 şemaları. Soru oluşturma (QuestionCreate) ve
# API yanıtı (QuestionResponse) için kullanılır.
# ============================================================

from pydantic import BaseModel, Field


# ============================================================
# Ortak / Temel Şema
# ============================================================
class QuestionBase(BaseModel):
    """
    Tüm soru şemalarının paylaştığı temel alanlar.
    """

    topic: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Olasılık"],
        description="Sorunun ait olduğu istatistik konusu",
    )
    difficulty_level: int = Field(
        ...,
        ge=1,
        le=5,
        examples=[3],
        description="Zorluk seviyesi (1=çok kolay, 5=çok zor)",
    )
    content: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        examples=["Bir paranın iki kez atılmasında en az bir tura gelme olasılığı nedir?"],
        description="Soru metni",
    )
    correct_answer: str = Field(
        ...,
        min_length=1,
        max_length=500,
        examples=["3/4"],
        description="Sorunun doğru cevabı",
    )
    points_awarded: int = Field(
        default=10,
        ge=1,
        le=1000,
        examples=[10],
        description="Bu soru doğru bilindiğinde verilecek puan",
    )


# ============================================================
# Oluşturma Şeması (Request)
# ============================================================
class QuestionCreate(QuestionBase):
    """
    POST /questions endpoint'ine gönderilecek veri.
    Tüm zorunlu alanlar QuestionBase'den miras alınır.
    """
    pass


# ============================================================
# Yanıt Şeması (Response)
# ============================================================
class QuestionResponse(QuestionBase):
    """
    API'den döndürülecek soru verisi.
    Veritabanından gelen id alanını da içerir.
    """

    id: int = Field(..., description="Veritabanı birincil anahtarı")

    # Pydantic v2'de ORM nesnelerini okumak için
    model_config = {"from_attributes": True}


# ============================================================
# Oyun Cevap Şeması (Request)
# ============================================================
class AnswerSubmit(BaseModel):
    """
    POST /game/answer endpoint'ine gönderilecek veri.

    Not: user_id artık JWT token'dan otomatik alınmaktadır.
    İsteği yapan kullanıcı, Authorization: Bearer <token> başlığıyla belirlenir.
    """

    question_id: int = Field(..., ge=1, description="Cevaplanacak sorunun ID'si")
    user_answer: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Kullanıcının verdiği cevap",
    )


# ============================================================
# Oyun Cevap Yanıt Şeması (Response)
# ============================================================
class AnswerResult(BaseModel):
    """
    POST /game/answer endpoint'inden döndürülecek sonuç.
    """

    is_correct: bool = Field(..., description="Cevap doğru mu?")
    message: str = Field(..., description="Kullanıcıya gösterilecek mesaj")
    correct_answer: str = Field(..., description="Sorunun doğru cevabı")
    points_earned: int = Field(default=0, description="Bu cevapta kazanılan puan")
    new_score: int = Field(..., description="Kullanıcının güncel toplam puanı")
