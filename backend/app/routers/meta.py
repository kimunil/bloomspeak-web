from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/providers")
def providers():
    """외부 연동 상태 점검 — 키가 없으면 mock 으로 동작."""
    has_openai = bool(settings.OPENAI_API_KEY)
    has_pg = bool(settings.PG_SECRET_KEY)
    def mode(p, key):
        return p if (p != "mock" and key) else "mock"
    return {
        "stt": {"provider": mode(settings.STT_PROVIDER, has_openai), "configured": has_openai},
        "llm": {"provider": mode(settings.LLM_PROVIDER, has_openai), "configured": has_openai},
        "pg":  {"provider": mode(settings.PG_PROVIDER, has_pg), "configured": has_pg},
        "note": "configured=false 면 해당 영역은 mock 으로 동작합니다. .env 에 키를 넣고 PROVIDER 를 변경하세요.",
    }
