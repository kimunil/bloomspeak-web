from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(20), default="local")  # kakao/google/naver/local
    provider_user_id: Mapped[str] = mapped_column(String(120), default="", index=True)  # provider 고유 subject
    name: Mapped[str] = mapped_column(String(80), default="")
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    segment: Mapped[str] = mapped_column(String(10), default="2030")   # 5060 | 2030
    goal: Mapped[str] = mapped_column(String(20), default="travel")     # travel/grandkids/job/brain
    level: Mapped[int] = mapped_column(Integer, default=0)
    push_token: Mapped[str] = mapped_column(String(255), default="")
    user: Mapped["User"] = relationship(back_populates="profile")


class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[float] = mapped_column(Float, default=0)
    weakness: Mapped[str] = mapped_column(String(255), default="")
    taken_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    diagnosis_id: Mapped[int] = mapped_column(ForeignKey("diagnoses.id"))
    weeks: Mapped[int] = mapped_column(Integer, default=24)
    goal: Mapped[str] = mapped_column(String(20), default="travel")


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    segment: Mapped[str] = mapped_column(String(10), default="all")
    total_weeks: Mapped[int] = mapped_column(Integer, default=24)


class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    seq: Mapped[int] = mapped_column(Integer, default=1)
    type: Mapped[str] = mapped_column(String(20), default="method")  # method | expression | speaking
    title: Mapped[str] = mapped_column(String(160), default="")
    target_sentence: Mapped[str] = mapped_column(String(255), default="")  # for speaking
    content_ref: Mapped[str] = mapped_column(String(255), default="")


class Progress(Base):
    __tablename__ = "progress"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    status: Mapped[str] = mapped_column(String(20), default="started")  # started | done
    score: Mapped[float] = mapped_column(Float, default=0)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class SpeakAttempt(Base):
    __tablename__ = "speak_attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    transcript: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0)
    feedback: Mapped[str] = mapped_column(Text, default="")
    audio_url: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tier: Mapped[str] = mapped_column(String(20), default="basic")  # basic | completion | premium
    status: Mapped[str] = mapped_column(String(20), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(Integer, default=0)
    pg_tx_id: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(20), default="paid")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class CompletionRefund(Base):
    __tablename__ = "refunds"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    progress_pct: Mapped[float] = mapped_column(Float, default=0)
    eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    amount: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")


class RewardLedger(Base):
    __tablename__ = "reward_ledger"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    delta: Mapped[int] = mapped_column(Integer, default=0)   # 블룸 +/-
    reason: Mapped[str] = mapped_column(String(120), default="")
    balance: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


# ---------- v1: 스토리 게임 ----------
class Story(Base):
    __tablename__ = "stories"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    segment: Mapped[str] = mapped_column(String(10), default="all")
    character: Mapped[str] = mapped_column(String(40), default="Emma")


class Scene(Base):
    __tablename__ = "scenes"
    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    seq: Mapped[int] = mapped_column(Integer, default=1)
    prompt: Mapped[str] = mapped_column(String(255), default="")        # 상대 대사
    target_sentence: Mapped[str] = mapped_column(String(255), default="")  # 정답 발화
    hint: Mapped[str] = mapped_column(String(255), default="")


class AffinityState(Base):
    __tablename__ = "affinity_state"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    affinity: Mapped[int] = mapped_column(Integer, default=0)        # 0~100
    unlocked_scene: Mapped[int] = mapped_column(Integer, default=1)  # 해금된 장면 seq


# ---------- v1: 커뮤니티 ----------
class StudyRoom(Base):
    __tablename__ = "study_rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    host: Mapped[str] = mapped_column(String(40), default="스텔라")
    title: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(20), default="live")   # live | cert
    schedule: Mapped[str] = mapped_column(String(60), default="")


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("study_rooms.id"), nullable=True)
    body: Mapped[str] = mapped_column(Text, default="")
    media_url: Mapped[str] = mapped_column(String(255), default="")
    is_completion: Mapped[bool] = mapped_column(Boolean, default=False)  # 완주 인증 여부
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


# ---------- v1: 후기 · 추천 ----------
class Referral(Base):
    __tablename__ = "referrals"
    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    referee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="issued")  # issued | redeemed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer, default=5)
    body: Mapped[str] = mapped_column(Text, default="")
    referral_code: Mapped[str] = mapped_column(String(16), default="")  # 발급된 추천코드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class ContentAsset(Base):
    __tablename__ = "content_assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20), default="audio")  # audio | video | image
    url: Mapped[str] = mapped_column(String(255), default="")
    license: Mapped[str] = mapped_column(String(120), default="owned")


class Signup(Base):
    __tablename__ = "signups"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    lang: Mapped[str] = mapped_column(String(8), default="ko")
    source: Mapped[str] = mapped_column(String(40), default="landing")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Diary(Base):
    __tablename__ = "diaries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    content: Mapped[str] = mapped_column(String(280), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
