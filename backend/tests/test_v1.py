"""v1: 스토리게임(호감도) · 커뮤니티(완주인증) · 후기→추천코드 → 리워드."""
import os
import tempfile
from pathlib import Path

db_path = Path(tempfile.gettempdir()) / "bloom_v1.db"
db_path.unlink(missing_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import run as seed  # noqa: E402
seed()
c = TestClient(app)


def auth(email):
    r = c.post("/auth/login", json={"email": email})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_story_game_affinity():
    h = auth("gamer@bloom.io")
    scenes = c.get("/story/1/scenes", headers=h).json()
    assert scenes[0]["locked"] is False and scenes[1]["locked"] is True
    # 정답 발화 → 통과, 호감도↑, 다음 장면 해금
    r = c.post("/story/speak", json={"scene_id": scenes[0]["scene_id"],
              "transcript": scenes[0]["target_sentence"]}, headers=h).json()
    assert r["passed"] and r["affinity"] >= 8 and r["unlocked_scene"] == 2
    # 잠긴 장면 발화는 거부
    locked = c.post("/story/speak", json={"scene_id": scenes[2]["scene_id"], "transcript": "x"}, headers=h)
    assert locked.status_code == 403


def test_community_completion_reward():
    h = auth("cert@bloom.io")
    rooms = c.get("/community/rooms", headers=h).json()
    assert len(rooms) >= 2
    c.post("/community/post", json={"body": "Day 30 완주!", "is_completion": True}, headers=h)
    bal = c.get("/reward/ledger", headers=h).json()["balance"]
    assert bal >= 20  # 완주 인증 +20


def test_review_referral_loop():
    a = auth("ref_a@bloom.io")
    b = auth("ref_b@bloom.io")
    out = c.post("/social/review", json={"rating": 5, "body": "트였어요!"}, headers=a).json()
    code = out["referral_code"]
    assert code.startswith("BLOOM") and out["bloom_awarded"] == 50
    red = c.post("/social/redeem", json={"code": code}, headers=b)
    assert red.status_code == 200
    # 추천인 +100(후기50+추천100=150), 피추천인 +30
    assert c.get("/reward/ledger", headers=a).json()["balance"] == 150
    assert c.get("/reward/ledger", headers=b).json()["balance"] == 30


def test_signup_public():
    r = c.post("/signup", json={"email": "early@bloom.io", "lang": "ko"})
    assert r.status_code == 200 and r.json()["ok"] is True
    dup = c.post("/signup", json={"email": "early@bloom.io"})
    assert dup.json()["duplicate"] is True
    assert c.get("/signup/count").json()["count"] >= 1


def test_diary_oneline():
    h = auth("diary@bloom.io")
    r = c.post("/learning/diary", json={"content": "I made a new friend today."}, headers=h)
    assert r.status_code == 200
    lst = c.get("/learning/diary", headers=h).json()
    assert lst and lst[0]["content"].startswith("I made")
    assert c.get("/reward/ledger", headers=h).json()["balance"] >= 5
