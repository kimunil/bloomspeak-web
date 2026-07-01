"""콘텐츠 가안 시드: curriculum/story/trendy/together JSON 로드 → DB 반영.

content/ 의 JSON은 온라인 통용 표현을 참고한 오리지널 가안이며,
전가은(CCO)의 실제 커리큘럼·대본·음성으로 교체됩니다.
"""
import json
import os
from app.db.session import SessionLocal, Base, engine
from app import models

Base.metadata.create_all(bind=engine)
CDIR = os.path.join(os.path.dirname(__file__), "content")


def _load(name):
    p = os.path.join(CDIR, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def run():
    db = SessionLocal()

    # ---- 커리큘럼: Course + Lessons (method/expression/speaking) ----
    if db.query(models.Course).count() == 0:
        cur = _load("curriculum.json") or {"title": "여행 영어 스타터", "lessons": []}
        c = models.Course(title=cur.get("title", "BLOOM 24주 코스"), segment="all", total_weeks=24)
        db.add(c)
        db.commit()
        db.refresh(c)
        seq = 0
        for lz in cur.get("lessons", []):
            # 1) 메소드/상황 도입 레슨
            seq += 1
            db.add(models.Lesson(course_id=c.id, seq=seq, type="method",
                                 title=f"{lz['week']}주차 · {lz['title']}",
                                 target_sentence="", content_ref=lz.get("situation", "")))
            # 2) 핵심 문장들을 speaking 레슨으로
            for st in lz.get("sentences", []):
                seq += 1
                db.add(models.Lesson(course_id=c.id, seq=seq, type="speaking",
                                     title=lz["title"], target_sentence=st["en"],
                                     content_ref=st["ko"]))
        db.commit()

    # ---- 트렌디 표현: expression 레슨으로 별도 코스 ----
    if db.query(models.Course).filter(models.Course.title.like("%트렌디%")).count() == 0:
        tr = _load("trendy.json")
        if tr:
            tc = models.Course(title="트렌디 클립 (가안)", segment="2030", total_weeks=4)
            db.add(tc)
            db.commit()
            db.refresh(tc)
            for i, clip in enumerate(tr.get("clips", []), 1):
                db.add(models.Lesson(course_id=tc.id, seq=i, type="expression",
                                     title=clip["tag"], target_sentence=clip["en"],
                                     content_ref=clip["ko"]))
            db.commit()

    # ---- 스토리 게임: 여러 스토리 + Scenes (챕터 평탄화) ----
    if db.query(models.Story).count() == 0:
        for fname in ("story_nyc.json", "story_seoul.json", "story_campus.json"):
            stj = _load(fname)
            if not stj:
                continue
            s = models.Story(title=stj["title"], character=stj.get("character", "Emma"),
                             segment=stj.get("segment", "all"))
            db.add(s)
            db.commit()
            db.refresh(s)
            seq = 0
            for ch in stj.get("chapters", []):
                for sc in ch.get("scenes", []):
                    seq += 1
                    db.add(models.Scene(story_id=s.id, seq=seq, prompt=sc["line"],
                                        target_sentence=sc["target"], hint=sc["hint"]))
            db.commit()

    # ---- 스터디룸 ----
    if db.query(models.StudyRoom).count() == 0:
        db.add(models.StudyRoom(host="스텔라", title="아침 6시 미라클 영어", type="live", schedule="평일 06:00"))
        db.add(models.StudyRoom(host="커뮤니티", title="5060 여행영어 완주방", type="live", schedule="화/목 20:00"))
        db.add(models.StudyRoom(host="커뮤니티", title="#블룸영어챌린지 인증방", type="cert", schedule="상시"))
        ch = _load("challenges.json")
        if ch:
            for item in ch.get("items", []):
                db.add(models.StudyRoom(host="챌린지", title=item["name"], type="challenge", schedule=item["duration"]))
        db.commit()

    db.close()
    print("seeded (content gaan)")


if __name__ == "__main__":
    run()
