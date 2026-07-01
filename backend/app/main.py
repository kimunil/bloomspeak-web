from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import Base, engine
from app import models  # noqa: F401
from app.routers import (auth, onboarding, diagnosis, learning, speaking, billing,
                         story, community, social, reward, meta, signup)

app = FastAPI(title="BLOOM English API", version="0.2.0 (MVP+v1)")
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(bind=engine)
for r in (auth, onboarding, diagnosis, learning, speaking, billing, story, community, social, reward, meta, signup):
    app.include_router(r.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "service": "bloom-english", "version": "0.2.0"}
