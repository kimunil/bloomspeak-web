import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas


router = APIRouter(prefix="/social", tags=["referral-review"])


def _award(db, user_id, delta, reason):
    last = (db.query(models.RewardLedger).filter_by(user_id=user_id)
            .order_by(models.RewardLedger.id.desc()).first())
    bal = (last.balance if last else 0) + delta
    db.add(models.RewardLedger(user_id=user_id, delta=delta, reason=reason, balance=bal))


@router.post("/review", response_model=schemas.ReviewOut)
def review(body: schemas.ReviewIn, db: Session = Depends(get_db), user=Depends(current_user)):
    """후기 작성 → 추천코드 발급 + 블룸 적립 (후기→추천 그로스 루프)."""
    code = "BLOOM" + secrets.token_hex(3).upper()
    db.add(models.Referral(referrer_id=user.id, code=code, status="issued"))
    db.add(models.Review(user_id=user.id, rating=body.rating, body=body.body, referral_code=code))
    _award(db, user.id, 50, "review_written")
    db.commit()
    return schemas.ReviewOut(review_id=0, referral_code=code, bloom_awarded=50)


@router.post("/redeem")
def redeem(body: schemas.RedeemIn, db: Session = Depends(get_db), user=Depends(current_user)):
    ref = db.query(models.Referral).filter_by(code=body.code).first()
    if not ref:
        raise HTTPException(404, "invalid code")
    if ref.status == "redeemed":
        raise HTTPException(409, "already redeemed")
    if ref.referrer_id == user.id:
        raise HTTPException(400, "cannot redeem own code")
    ref.referee_id = user.id
    ref.status = "redeemed"
    _award(db, ref.referrer_id, 100, "referral_success")  # 추천인 보상
    _award(db, user.id, 30, "referred_join")              # 피추천인 보상
    db.commit()
    return {"code": body.code, "status": "redeemed"}
