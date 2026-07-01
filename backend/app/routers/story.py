from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.deps import current_user
from app import models, schemas
from app.services.speech import score_attempt

router = APIRouter(prefix="/story", tags=["story-game"])


def _state(db, user_id, story_id):
    st = db.query(models.AffinityState).filter_by(user_id=user_id, story_id=story_id).first()
    if not st:
        st = models.AffinityState(user_id=user_id, story_id=story_id, affinity=0, unlocked_scene=1)
        db.add(st)
        db.commit()
        db.refresh(st)
    return st


@router.get("/list")
def stories(db: Session = Depends(get_db), user=Depends(current_user)):
    return [{"id": s.id, "title": s.title, "character": s.character, "segment": s.segment}
            for s in db.query(models.Story).all()]


@router.get("/{story_id}/scenes", response_model=list[schemas.SceneOut])
def scenes(story_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    st = _state(db, user.id, story_id)
    rows = db.query(models.Scene).filter_by(story_id=story_id).order_by(models.Scene.seq).all()
    return [schemas.SceneOut(scene_id=s.id, seq=s.seq, prompt=s.prompt, target_sentence=s.target_sentence,
                             hint=s.hint, locked=s.seq > st.unlocked_scene) for s in rows]


@router.post("/speak", response_model=schemas.GameSpeakOut)
def speak(body: schemas.GameSpeakIn, db: Session = Depends(get_db), user=Depends(current_user)):
    scene = db.get(models.Scene, body.scene_id)
    if not scene:
        raise HTTPException(404, "scene not found")
    st = _state(db, user.id, scene.story_id)
    if scene.seq > st.unlocked_scene:
        raise HTTPException(403, "scene locked")
    r = score_attempt(scene.target_sentence, audio_bytes=None, provided_text=body.transcript)
    db.add(models.SpeakAttempt(user_id=user.id, transcript=r["transcript"], score=r["score"], feedback=r["feedback"]))
    if r["passed"]:
        st.affinity = min(100, st.affinity + 8)
        if scene.seq == st.unlocked_scene:
            st.unlocked_scene = scene.seq + 1
    db.commit()
    return schemas.GameSpeakOut(passed=r["passed"], score=r["score"], feedback=r["feedback"],
                                affinity=st.affinity, unlocked_scene=st.unlocked_scene)
