from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas
from app.services.diagnosis import build_roadmap

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])


@router.post("/submit", response_model=schemas.RoadmapOut)
def submit(body: schemas.DiagnosisIn, user=Depends(current_user), db: Session = Depends(get_db)):
    r = build_roadmap(body.answers)
    diag = models.Diagnosis(user_id=user.id, score=r["score"], weakness=r["weakness"])
    db.add(diag)
    db.commit()
    db.refresh(diag)
    goal = (db.query(models.Profile).filter_by(user_id=user.id).first() or models.Profile(goal="travel")).goal
    rm = models.Roadmap(user_id=user.id, diagnosis_id=diag.id, weeks=r["weeks"], goal=goal)
    db.add(rm)
    db.commit()
    return schemas.RoadmapOut(diagnosis_id=diag.id, score=r["score"], weakness=r["weakness"], weeks=r["weeks"], goal=goal)
