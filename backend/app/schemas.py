from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    provider: str = "local"


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int


class OnboardingIn(BaseModel):
    segment: str = "2030"   # 5060 | 2030
    goal: str = "travel"     # travel | grandkids | job | brain


class ProfileOut(BaseModel):
    user_id: int
    segment: str
    goal: str
    level: int


class DiagnosisIn(BaseModel):
    answers: list[int] = []  # 문항 점수(0~1)


class RoadmapOut(BaseModel):
    diagnosis_id: int
    score: float
    weakness: str
    weeks: int
    goal: str


class SpeakIn(BaseModel):
    target_sentence: str
    transcript: str | None = None  # 클라가 보낸 텍스트(테스트용). 실제론 audio.
    lesson_id: int | None = None


class SpeakOut(BaseModel):
    transcript: str
    score: float
    feedback: str
    passed: bool


class SubscribeIn(BaseModel):
    tier: str = "completion"  # basic | completion | premium


class RefundCheckOut(BaseModel):
    course_id: int
    progress_pct: float
    eligible: bool
    amount: int
    note: str


# ---------- v1 ----------
class SceneOut(BaseModel):
    scene_id: int
    seq: int
    prompt: str
    target_sentence: str
    hint: str
    locked: bool


class GameSpeakIn(BaseModel):
    scene_id: int
    transcript: str | None = None


class GameSpeakOut(BaseModel):
    passed: bool
    score: float
    feedback: str
    affinity: int
    unlocked_scene: int


class PostIn(BaseModel):
    room_id: int | None = None
    body: str = ""
    media_url: str = ""
    is_completion: bool = False


class ReviewIn(BaseModel):
    rating: int = 5
    body: str = ""


class ReviewOut(BaseModel):
    review_id: int
    referral_code: str
    bloom_awarded: int


class RedeemIn(BaseModel):
    code: str


class RewardOut(BaseModel):
    balance: int
    entries: list[dict]


class SignupIn(BaseModel):
    email: EmailStr
    lang: str = "ko"
    source: str = "landing"


class DiaryIn(BaseModel):
    content: str
    day: str | None = None   # 미지정 시 오늘


class OAuthCodeIn(BaseModel):
    code: str
    redirect_uri: str | None = None
    code_verifier: str | None = None  # PKCE (선택)
