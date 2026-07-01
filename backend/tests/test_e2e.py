"""S0 PoC: 가입 -> 온보딩 -> 진단 -> 레슨완료 -> 발화채점 end-to-end (mock STT/LLM)."""
import os
import tempfile
from pathlib import Path

db_path = Path(tempfile.gettempdir()) / "bloom_e2e.db"
db_path.unlink(missing_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import run as seed  # noqa: E402

seed()
client = TestClient(app)


def _auth():
    r = client.post("/auth/login", json={"email": "demo@bloom.io"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_full_flow():
    h = _auth()
    assert client.post("/onboarding/profile", json={"segment": "5060", "goal": "travel"}, headers=h).status_code == 200
    rm = client.post("/diagnosis/submit", json={"answers": [1, 0, 1, 0]}, headers=h).json()
    assert rm["weeks"] in (16, 20, 24)
    # 발화 채점 PoC — 정답과 거의 같게 말하면 통과
    sp = client.post("/speaking/score", json={
        "target_sentence": "I am here to visit my friend",
        "transcript": "I am here to visit my friend"}, headers=h).json()
    assert sp["passed"] is True and sp["score"] >= 0.9
    # 틀리게 말하면 미통과 + 피드백
    sp2 = client.post("/speaking/score", json={
        "target_sentence": "I am here to visit my friend",
        "transcript": "uh hello"}, headers=h).json()
    assert sp2["passed"] is False
