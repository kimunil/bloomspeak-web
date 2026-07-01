"""결제(PG). mock 기본. PG_PROVIDER=toss 이면 Toss Payments confirm API 사용."""
import uuid
import base64
import httpx
from app.core.config import settings

PRICE = {"basic": 19900, "completion": 49000, "premium": 129000}


def charge(tier: str) -> dict:
    """구독 시작(데모/mock). 실결제는 confirm_payment 로."""
    amount = PRICE.get(tier, PRICE["completion"])
    return {"amount": amount, "pg_tx_id": f"mock_{uuid.uuid4().hex[:12]}", "status": "paid"}


def confirm_payment(payment_key: str, order_id: str, amount: int) -> dict:
    """클라이언트 결제위젯 승인 후 서버 확정. PG_PROVIDER=toss + 키 있으면 실제 호출."""
    if settings.PG_PROVIDER == "toss" and settings.PG_SECRET_KEY:
        auth = base64.b64encode(f"{settings.PG_SECRET_KEY}:".encode()).decode()
        r = httpx.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
            json={"paymentKey": payment_key, "orderId": order_id, "amount": amount},
            timeout=20,
        )
        r.raise_for_status()
        d = r.json()
        return {"amount": d.get("totalAmount", amount), "pg_tx_id": d.get("paymentKey", payment_key), "status": d.get("status", "DONE")}
    # mock 승인
    return {"amount": amount, "pg_tx_id": payment_key or f"mock_{uuid.uuid4().hex[:8]}", "status": "DONE"}
