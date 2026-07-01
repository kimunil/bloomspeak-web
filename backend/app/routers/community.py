from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/rooms")
def rooms(db: Session = Depends(get_db), user=Depends(current_user)):
    return [{"id": r.id, "host": r.host, "title": r.title, "type": r.type, "schedule": r.schedule}
            for r in db.query(models.StudyRoom).all()]


@router.get("/feed")
def feed(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(models.Post).order_by(models.Post.id.desc()).limit(30).all()
    return [{"id": p.id, "user_id": p.user_id, "body": p.body, "media_url": p.media_url,
             "is_completion": p.is_completion} for p in rows]


@router.post("/post")
def create_post(body: schemas.PostIn, db: Session = Depends(get_db), user=Depends(current_user)):
    p = models.Post(user_id=user.id, room_id=body.room_id, body=body.body,
                    media_url=body.media_url, is_completion=body.is_completion)
    db.add(p)
    # 완주 인증 시 블룸 리워드
    if body.is_completion:
        last = (db.query(models.RewardLedger).filter_by(user_id=user.id)
                .order_by(models.RewardLedger.id.desc()).first())
        bal = (last.balance if last else 0) + 20
        db.add(models.RewardLedger(user_id=user.id, delta=20, reason="completion_cert", balance=bal))
    db.commit()
    db.refresh(p)
    return {"id": p.id, "is_completion": p.is_completion}
