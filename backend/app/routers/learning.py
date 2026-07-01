from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as _date
from datetime import datetime, timezone
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/lessons")
def lessons(course_id: int = 1, db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(models.Lesson).filter_by(course_id=course_id).order_by(models.Lesson.seq).all()
    return [
        {
            "id": lesson.id,
            "seq": lesson.seq,
            "type": lesson.type,
            "title": lesson.title,
            "target_sentence": lesson.target_sentence,
        }
        for lesson in rows
    ]


@router.post("/lessons/{lesson_id}/complete")
def complete(lesson_id: int, score: float = 1.0, db: Session = Depends(get_db), user=Depends(current_user)):
    if not db.get(models.Lesson, lesson_id):
        raise HTTPException(404, "lesson not found")
    p = db.query(models.Progress).filter_by(user_id=user.id, lesson_id=lesson_id).first()
    if not p:
        p = models.Progress(user_id=user.id, lesson_id=lesson_id)
        db.add(p)
    p.status = "done"
    p.score = score
    p.completed_at = datetime.now(timezone.utc)
    db.commit()
    return {"lesson_id": lesson_id, "status": "done", "score": score}


@router.get("/progress")
def progress(course_id: int = 1, db: Session = Depends(get_db), user=Depends(current_user)):
    total = db.query(models.Lesson).filter_by(course_id=course_id).count() or 1
    done = db.query(models.Progress).filter_by(user_id=user.id, status="done").count()
    return {"course_id": course_id, "total": total, "done": done, "pct": round(done / total * 100, 1)}

@router.post("/diary")
def write_diary(body: schemas.DiaryIn, db: Session = Depends(get_db), user=Depends(current_user)):
    """오늘 배운 표현으로 한 줄 일기 (학습 홈)."""
    day = body.day or _date.today().isoformat()
    d = db.query(models.Diary).filter_by(user_id=user.id, day=day).first()
    if d:
        d.content = body.content
    else:
        d = models.Diary(user_id=user.id, day=day, content=body.content)
        db.add(d)
    # 첫 작성 시 블룸 +5
    if not db.query(models.RewardLedger).filter_by(user_id=user.id, reason="diary").first():
        last = db.query(models.RewardLedger).filter_by(user_id=user.id).order_by(models.RewardLedger.id.desc()).first()
        bal = (last.balance if last else 0) + 5
        db.add(models.RewardLedger(user_id=user.id, delta=5, reason="diary", balance=bal))
    db.commit()
    return {"day": day, "content": body.content}

@router.get("/diary")
def list_diary(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(models.Diary).filter_by(user_id=user.id).order_by(models.Diary.day.desc()).limit(30).all()
    return [{"day": r.day, "content": r.content} for r in rows]
