"""Authentication routes for email login and social OAuth login."""

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.core.security import create_token
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

PROVIDERS = {
    "google": {
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
    },
    "kakao": {
        "token_url": "https://kauth.kakao.com/oauth/token",
        "userinfo_url": "https://kapi.kakao.com/v2/user/me",
    },
    "naver": {
        "token_url": "https://nid.naver.com/oauth2.0/token",
        "userinfo_url": "https://openapi.naver.com/v1/nid/me",
    },
}


def _client(provider: str) -> tuple[str, str]:
    if provider == "google":
        return settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET
    if provider == "naver":
        return settings.NAVER_CLIENT_ID, settings.NAVER_CLIENT_SECRET
    if provider == "kakao":
        return settings.KAKAO_REST_API_KEY, settings.KAKAO_CLIENT_SECRET
    return "", ""


def _provider_error(provider: str, stage: str, exc: httpx.HTTPStatusError) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "provider": provider,
            "stage": stage,
            "status_code": exc.response.status_code,
            "response": exc.response.text,
        },
    )


def _exchange_and_fetch(provider: str, code: str, redirect_uri: str) -> tuple[str, str, str]:
    cfg = PROVIDERS[provider]
    cid, secret = _client(provider)
    data = {
        "grant_type": "authorization_code",
        "client_id": cid,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    if secret:
        data["client_secret"] = secret

    with httpx.Client(timeout=10) as client:
        token_response = client.post(
            cfg["token_url"],
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            token_response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise _provider_error(provider, "token_exchange", exc) from exc

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise HTTPException(400, "token exchange failed")

        userinfo_response = client.get(
            cfg["userinfo_url"],
            headers={"Authorization": f"Bearer {access_token}"},
        )
        try:
            userinfo_response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise _provider_error(provider, "userinfo", exc) from exc
        userinfo = userinfo_response.json()

    if provider == "google":
        return userinfo.get("email", ""), str(userinfo.get("sub", "")), userinfo.get("name", "")
    if provider == "kakao":
        account = userinfo.get("kakao_account", {}) or {}
        profile = account.get("profile", {}) or {}
        return account.get("email", ""), str(userinfo.get("id", "")), profile.get("nickname", "")
    if provider == "naver":
        response = userinfo.get("response", {}) or {}
        return response.get("email", ""), str(response.get("id", "")), response.get("name", "")
    return "", "", ""


def _upsert(db: Session, provider: str, email: str, provider_user_id: str, name: str) -> models.User:
    user = None
    if provider_user_id:
        user = db.query(models.User).filter_by(
            provider=provider,
            provider_user_id=provider_user_id,
        ).first()
    if not user and email:
        user = db.query(models.User).filter_by(email=email).first()

    if not user:
        user = models.User(
            email=email or f"{provider}_{provider_user_id}@bloomspeak.kr",
            provider=provider,
            provider_user_id=provider_user_id,
            name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    changed = False
    if not user.provider_user_id and provider_user_id:
        user.provider_user_id = provider_user_id
        changed = True
    if user.provider == "local":
        user.provider = provider
        changed = True
    if changed:
        db.commit()
        db.refresh(user)
    return user


@router.post("/login", response_model=schemas.TokenOut)
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=body.email).first()
    if not user:
        user = models.User(email=body.email, provider=getattr(body, "provider", "local") or "local")
        db.add(user)
        db.commit()
        db.refresh(user)
    return schemas.TokenOut(access_token=create_token(user.id), user_id=user.id)


@router.post("/oauth/{provider}", response_model=schemas.TokenOut)
def oauth_login(provider: str, body: schemas.OAuthCodeIn, db: Session = Depends(get_db)):
    if provider not in PROVIDERS:
        raise HTTPException(404, "unsupported provider")

    client_id, client_secret = _client(provider)
    redirect_uri = body.redirect_uri or f"{settings.OAUTH_REDIRECT_BASE}/auth/{provider}/callback"

    if client_id and (client_secret or provider == "kakao"):
        email, provider_user_id, name = _exchange_and_fetch(provider, body.code, redirect_uri)
    else:
        provider_user_id = "demo_" + body.code[-6:] if body.code else "demo"
        email = f"{provider}.{provider_user_id}@bloomspeak.kr"
        name = f"{provider} demo user"

    user = _upsert(db, provider, email, provider_user_id, name)
    return schemas.TokenOut(access_token=create_token(user.id), user_id=user.id)


@router.get("/{provider}/callback")
def oauth_callback(provider: str, code: str = "", state: str = ""):
    scheme = settings.APP_DEEP_LINK_SCHEME
    return RedirectResponse(f"{scheme}://oauth?provider={provider}&code={code}&state={state}")
