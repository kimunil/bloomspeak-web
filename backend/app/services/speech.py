"""발화 채점 — STT -> (정답 비교 + LLM 피드백).
키가 없거나 provider=mock 이면 자동으로 오프라인 mock 동작.
실서비스: .env 의 STT_PROVIDER / LLM_PROVIDER 를 openai|google|anthropic 로 변경하고 키 설정."""
import difflib
import re
import httpx
from app.core.config import settings


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


# ---------- STT ----------
def transcribe(audio_bytes: bytes | None, provided_text: str | None, mime: str = "audio/m4a") -> str:
    """오디오 -> 텍스트. audio 없으면 provided_text 사용(PoC/테스트)."""
    if not audio_bytes:
        return provided_text or ""
    provider = settings.STT_PROVIDER
    try:
        if provider == "openai" and settings.OPENAI_API_KEY:
            return _stt_openai(audio_bytes, mime)
        if provider == "google":
            return _stt_google(audio_bytes)  # TODO: Google Speech-to-Text
    except Exception as e:  # 폴백: 절대 죽지 않게
        print(f"[STT fallback] {e}")
    return provided_text or ""


def _stt_openai(audio_bytes: bytes, mime: str) -> str:
    r = httpx.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        files={"file": ("audio", audio_bytes, mime)},
        data={"model": "whisper-1"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json().get("text", "")


def _stt_google(audio_bytes: bytes) -> str:
    raise NotImplementedError("Google STT 연동 TODO")


# ---------- LLM 피드백 ----------
def llm_feedback(target: str, said: str, score: float) -> str:
    provider = settings.LLM_PROVIDER
    try:
        if provider == "openai" and settings.OPENAI_API_KEY:
            return _llm_openai(target, said)
        if provider == "anthropic" and settings.OPENAI_API_KEY:
            return _llm_anthropic(target, said)
    except Exception as e:
        print(f"[LLM fallback] {e}")
    # mock
    if score >= 0.85:
        return "아주 좋아요! 자연스럽게 말했어요. 👍"
    if score >= 0.6:
        return f"거의 맞았어요. 또박또박 다시: \"{target}\""
    return f"천천히 따라 말해요: \"{target}\""


_PROMPT = (
    "You are a warm Korean-speaking English tutor for adult learners. "
    "Compare the learner's spoken sentence with the target. In 1-2 short Korean sentences, "
    "praise what's good and give one concrete fix. Be encouraging, never harsh.\n"
    "Target: {t}\nLearner said: {s}\nFeedback (Korean):"
)


def _llm_openai(target: str, said: str) -> str:
    r = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "max_tokens": 120,
              "messages": [{"role": "user", "content": _PROMPT.format(t=target, s=said)}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _llm_anthropic(target: str, said: str) -> str:
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": settings.OPENAI_API_KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": "claude-3-5-haiku-latest", "max_tokens": 120,
              "messages": [{"role": "user", "content": _PROMPT.format(t=target, s=said)}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"].strip()


# ---------- 통합 ----------
def score_attempt(target: str, audio_bytes: bytes | None, provided_text: str | None, mime: str = "audio/m4a"):
    transcript = transcribe(audio_bytes, provided_text, mime)
    score = round(_similarity(target, transcript), 3)
    feedback = llm_feedback(target, transcript, score)
    return {"transcript": transcript, "score": score, "feedback": feedback, "passed": score >= 0.6}
