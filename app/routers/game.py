# ============================================================
# Gausso Backend - Oyun Router'ı (Game Router)
# ============================================================
# POST /game/answer  → Kullanıcının cevabını değerlendir ve puan ver
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.question import Question
from app.models.user import User
from app.schemas.question import AnswerResult, AnswerSubmit

router = APIRouter(
    prefix="/game",
    tags=["Oyun Motoru"],
)


# ============================================================
# POST /api/v1/game/answer  — Cevabı Değerlendir
# ============================================================
@router.post(
    "/answer",
    response_model=AnswerResult,
    summary="Cevabı değerlendir ve puan güncelle",
    description=(
        "Kullanıcının verdiği cevabı sorunun doğru cevabıyla karşılaştırır. "
        "Cevap doğruysa kullanıcının toplam puanı (score) sorunun "
        "points_awarded değeri kadar artırılır. "
        "Cevap büyük/küçük harf duyarsız karşılaştırılır."
    ),
)
async def submit_answer(
    answer_in: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerResult:
    """
    Oyunlaştırma döngüsünün çekirdeği.

    Akış:
    1. JWT token'dan gelen current_user kullanılır (user_id parametresi kaldırıldı)
    2. question_id → Soruyu veritabanından bul
    3. Cevabı karşılaştır (büyük/küçük harf duyarsız, boşluk kırpılır)
    4. Doğruysa kullanıcının score'unu artır ve kaydet
    5. Sonucu AnswerResult şemasıyla döndür
    """
    # --- 1. Kullanıcıyı token'dan al (kimlik doğrulaması Depends ile yapıldı) ---
    user = current_user

    # --- 2. Soruyu bul ---
    question_result = await db.execute(
        select(Question).where(Question.id == answer_in.question_id)
    )
    question = question_result.scalar_one_or_none()

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={answer_in.question_id} olan soru bulunamadı.",
        )

    # --- 3. Cevabı karşılaştır ---
    # Büyük/küçük harf ve baştaki/sondaki boşluklar yok sayılır
    is_correct = (
        answer_in.user_answer.strip().lower()
        == question.correct_answer.strip().lower()
    )

    points_earned = 0
    new_score = user.score

    # --- 4. Doğruysa puanı artır ---
    if is_correct:
        points_earned = question.points_awarded
        user.score += points_earned
        new_score = user.score
        # get_db bağımlılığı commit'i otomatik yapar (session.commit())
        await db.flush()
        message = (
            f"🎉 Tebrikler, doğru cevap! +{points_earned} puan kazandın. "
            f"Toplam puanın: {new_score}"
        )
    else:
        message = (
            f"❌ Yanlış cevap. Doğru cevap: '{question.correct_answer}'. "
            "Tekrar dene!"
        )

    # --- 5. Sonucu döndür ---
    return AnswerResult(
        is_correct=is_correct,
        message=message,
        correct_answer=question.correct_answer,
        points_earned=points_earned,
        new_score=new_score,
    )
