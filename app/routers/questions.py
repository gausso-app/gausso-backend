# ============================================================
# Gausso Backend - Sorular Router'ı (Questions Router)
# ============================================================
# POST /questions/        → Yeni soru ekle (admin/geliştirici)
# GET  /questions/random  → Rastgele bir soru getir
# ============================================================

import random

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionResponse

router = APIRouter(
    prefix="/questions",
    tags=["Sorular"],
)


# ============================================================
# POST /api/v1/questions  — Yeni Soru Ekle
# ============================================================
@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni istatistik sorusu ekle",
    description=(
        "Veritabanına yeni bir istatistik sorusu ekler. "
        "difficulty_level 1 (çok kolay) ile 5 (çok zor) arasında olmalıdır. "
        "points_awarded soruyu doğru bilen kullanıcıya verilecek puandır."
    ),
)
async def create_question(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
) -> QuestionResponse:
    """
    Yeni soru oluşturma endpoint'i.

    - Zorunlu alanlar: topic, difficulty_level, content, correct_answer
    - İsteğe bağlı: points_awarded (varsayılan: 10)
    - Başarılıysa oluşturulan soruyu 201 ile döndürür
    """
    new_question = Question(
        topic=question_in.topic,
        difficulty_level=question_in.difficulty_level,
        content=question_in.content,
        correct_answer=question_in.correct_answer,
        points_awarded=question_in.points_awarded,
    )

    db.add(new_question)
    await db.flush()
    await db.refresh(new_question)

    return QuestionResponse.model_validate(new_question)


# ============================================================
# GET /api/v1/questions/random  — Rastgele Soru Getir
# ============================================================
@router.get(
    "/random",
    response_model=QuestionResponse,
    summary="Rastgele bir istatistik sorusu getir",
    description=(
        "Veritabanından rastgele bir soru döndürür. "
        "İsteğe bağlı olarak topic veya difficulty_level parametreleriyle "
        "belirli bir konudan ya da zorluk seviyesinden soru filtrelenebilir."
    ),
)
async def get_random_question(
    db: AsyncSession = Depends(get_db),
    topic: str | None = Query(
        default=None,
        description="Belirli bir konuya göre filtrele (örn: 'Olasılık')",
    ),
    difficulty_level: int | None = Query(
        default=None,
        ge=1,
        le=5,
        description="Belirli bir zorluk seviyesine göre filtrele (1-5)",
    ),
) -> QuestionResponse:
    """
    Rastgele soru endpoint'i.

    - Opsiyonel topic ve difficulty_level filtreleri desteklenir
    - Hiç soru bulunamazsa 404 döndürür
    - Kayıt sayısını çekerek Python tarafında rastgele seçim yapar
      (SQLite için func.random() desteği kısıtlı olduğundan)
    """
    stmt = select(Question)

    if topic:
        stmt = stmt.where(Question.topic == topic)
    if difficulty_level:
        stmt = stmt.where(Question.difficulty_level == difficulty_level)

    result = await db.execute(stmt)
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belirtilen kriterlere uygun soru bulunamadı.",
        )

    # Python tarafında rastgele seçim (SQLite ile uyumlu)
    chosen = random.choice(questions)
    return QuestionResponse.model_validate(chosen)
