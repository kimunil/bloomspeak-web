from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

ALGO = "HS256"


def create_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MIN)
    return jwt.encode({"sub": str(user_id), "exp": exp}, settings.JWT_SECRET, algorithm=ALGO)


def decode_token(token: str) -> int:
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])
    return int(data["sub"])
