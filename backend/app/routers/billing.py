from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas
from app.services.billing import charge, confirm_payment

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/subscribe")
def subscribe(body: schemas.SubscribeIn, user=Depends(current_user), db: Session = Depends(get_db)):
    pay = charge(body.tier)
    db.add(models.Payment(user_id=user.id, amount=pay["amount"], pg_tx_id=pay["pg_tx_id"], status=pay["status"]))
    sub = db.query(models.Subscription).filter_by(user_id=user.id).first() or models.Subscription(user_id=user.id)
    sub.tier = body.tier
    sub.status = "active"
    db.add(sub)
    db.commit()
    return {"tier": body.tier, "amount": pay["amount"], "tx": pay["pg_tx_id"], "status": "active"}


@router.post("/confirm")
def confirm(payment_key: str, order_id: str, amount: int, tier: str = "completion",
            user=Depends(current_user), db: Session = Depends(get_db)):
    """결제위젯 승인 콜백 → 서버 확정(Toss confirm)."""
    pay = confirm_payment(payment_key, order_id, amount)
    db.add(models.Payment(user_id=user.id, amount=pay["amount"], pg_tx_id=pay["pg_tx_id"], status=pay["status"]))
    sub = db.query(models.Subscription).filter_by(user_id=user.id).first() or models.Subscription(user_id=user.id)
    sub.tier = tier
    sub.status = "active"
    db.add(sub)
    db.commit()
    return {"status": pay["status"], "tx": pay["pg_tx_id"], "amount": pay["amount"]}


@router.get("/refund/check", response_model=schemas.RefundCheckOut)
def refund_check(course_id: int = 1, db: Session = Depends(get_db), user=Depends(current_user)):
    total = db.query(models.Lesson).filter_by(course_id=course_id).count() or 1
    done = db.query(models.Progress).filter_by(user_id=user.id, status="done").count()
    pct = round(done / total * 100, 1)
    eligible = pct >= 100.0
    paid = db.query(models.Payment).filter_by(user_id=user.id).first()
    amount = paid.amount if (eligible and paid) else 0
    note = "완주(100%) 시 환급 대상 · 주5회+인증 조건 별도 검증" if not eligible else "환급 대상"
    return schemas.RefundCheckOut(course_id=course_id, progress_pct=pct, eligible=eligible, amount=amount, note=note)
