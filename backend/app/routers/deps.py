from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app import models


def current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> models.User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    try:
        uid = decode_token(authorization.split(" ", 1)[1])
    except Exception:
        raise HTTPException(401, "invalid token")
    user = db.get(models.User, uid)
    if not user:
        raise HTTPException(401, "user not found")
    return user
