from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas

router = APIRouter(prefix="/signup", tags=["signup"])


@router.post("")
def signup(body: schemas.SignupIn, db: Session = Depends(get_db)):
    """사전신청 이메일 수집 (공개 · 인증 불필요). 중복 이메일은 멱등 처리."""
    existing = db.query(models.Signup).filter_by(email=body.email).first()
    if existing:
        return {"ok": True, "duplicate": True}
    db.add(models.Signup(email=body.email, lang=body.lang, source=body.source))
    db.commit()
    return {"ok": True, "duplicate": False}


@router.get("/count")
def count(db: Session = Depends(get_db)):
    return {"count": db.query(models.Signup).count()}


@router.get("/list")
def list_signups(db: Session = Depends(get_db), user=Depends(current_user)):
    """관리자용 — 토큰 필요."""
    rows = db.query(models.Signup).order_by(models.Signup.id.desc()).limit(500).all()
    return [{"email": s.email, "lang": s.lang, "source": s.source, "at": s.created_at.isoformat()} for s in rows]
