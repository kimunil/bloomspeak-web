from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/profile", response_model=schemas.ProfileOut)
def set_profile(body: schemas.OnboardingIn, user=Depends(current_user), db: Session = Depends(get_db)):
    prof = db.query(models.Profile).filter_by(user_id=user.id).first()
    if not prof:
        prof = models.Profile(user_id=user.id)
        db.add(prof)
    prof.segment = body.segment
    prof.goal = body.goal
    db.commit()
    db.refresh(prof)
    return schemas.ProfileOut(user_id=user.id, segment=prof.segment, goal=prof.goal, level=prof.level)
