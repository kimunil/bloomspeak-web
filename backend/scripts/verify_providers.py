"""외부 연동 점검: 키 유무 표시 + 키 있으면 LLM 소형 호출 시도.
사용: python scripts/verify_providers.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings
from app.services.speech import llm_feedback

print("== BLOOM provider check ==")
print("STT_PROVIDER:", settings.STT_PROVIDER, "| OPENAI key:", "set" if settings.OPENAI_API_KEY else "MISSING")
print("LLM_PROVIDER:", settings.LLM_PROVIDER, "| PG_PROVIDER:", settings.PG_PROVIDER,
      "| PG key:", "set" if settings.PG_SECRET_KEY else "MISSING")
print("\n[LLM dry-run]")
fb = llm_feedback("Can I get a flat white", "Can I get a flat white", 0.95)
print("feedback:", fb)
print("\n키가 없으면 위 피드백은 mock 입니다. .env 설정 후 PROVIDER 를 openai/anthropic/toss 로 변경하세요.")
