from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas
from app.services.speech import score_attempt

router = APIRouter(prefix="/speaking", tags=["speaking"])


def _persist(db, user, lesson_id, result):
    att = models.SpeakAttempt(user_id=user.id, lesson_id=lesson_id,
                              transcript=result["transcript"], score=result["score"],
                              feedback=result["feedback"])
    db.add(att)
    if result["passed"]:
        last = (db.query(models.RewardLedger).filter_by(user_id=user.id)
                .order_by(models.RewardLedger.id.desc()).first())
        bal = (last.balance if last else 0) + 10
        db.add(models.RewardLedger(user_id=user.id, delta=10, reason="speaking_pass", balance=bal))
    db.commit()


@router.post("/score", response_model=schemas.SpeakOut)
def score_text(body: schemas.SpeakIn, user=Depends(current_user), db: Session = Depends(get_db)):
    """텍스트(transcript) 기반 — PoC/브라우저 STT 결과 전송용."""
    result = score_attempt(body.target_sentence, audio_bytes=None, provided_text=body.transcript)
    _persist(db, user, body.lesson_id, result)
    return schemas.SpeakOut(**result)


@router.post("/score-audio", response_model=schemas.SpeakOut)
async def score_audio(target_sentence: str = Form(...), lesson_id: int | None = Form(None),
                      audio: UploadFile = File(...), user=Depends(current_user), db: Session = Depends(get_db)):
    """오디오 업로드 기반 — 실제 STT(Whisper) 연동 경로. 키 없으면 빈 transcript로 폴백."""
    data = await audio.read()
    result = score_attempt(target_sentence, audio_bytes=data, provided_text=None,
                           mime=audio.content_type or "audio/m4a")
    _persist(db, user, lesson_id, result)
    return schemas.SpeakOut(**result)
