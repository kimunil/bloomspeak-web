from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas

router = APIRouter(prefix="/reward", tags=["reward"])


@router.get("/ledger", response_model=schemas.RewardOut)
def ledger(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(models.RewardLedger).filter_by(user_id=user.id).order_by(models.RewardLedger.id.desc()).all()
    bal = rows[0].balance if rows else 0
    return schemas.RewardOut(balance=bal, entries=[{"delta": r.delta, "reason": r.reason, "balance": r.balance} for r in rows])
