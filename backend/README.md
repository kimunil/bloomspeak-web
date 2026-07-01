# BLOOM English — Backend (MVP S0)

성인 영어회화 앱 **BLOOM English(스텔라영어)** 백엔드 스캐폴드.
FastAPI + SQLAlchemy. 키가 없으면 **SQLite + mock STT/LLM/PG** 로 오프라인 동작합니다.

## ☁️ 무료 배포 (Render 원클릭)
이 리포에는 `render.yaml` 블루프린트가 포함돼 있습니다.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/kimunil/bloomspeak-api)

1. 위 버튼 클릭 → Render에 GitHub로 로그인 → **Apply** (빌드 2~4분)
2. 발급된 `https://<이름>.onrender.com/health` 에서 `{"status":"ok"}` 확인
3. Render → Settings → **Custom Domains** 에 `api.bloomspeak.kr` 추가 → 안내된 CNAME을 가비아 DNS(호스트 `api`)에 등록
4. 앱은 이미 `api.bloomspeak.kr` 를 호출 → **이메일 로그인 즉시 동작**

자세한 단계는 [`DEPLOY_RENDER.md`](./DEPLOY_RENDER.md) 참고. JWT_SECRET은 자동생성, 소셜 키는 Render 환경변수에만 입력(빈 값이면 데모 로그인).

## 빠른 실행
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 그대로 두면 SQLite + mock
python -m app.seed            # 데모 코스/레슨 시드
uvicorn app.main:app --reload # http://localhost:8000/docs
pytest -q                     # end-to-end PoC 테스트
```
Docker: `docker compose up --build` (Postgres 포함)

## 구현 상태 (스프린트 매핑)
- **S0 ✅** 프로젝트·DB(ERD)·CI·**발화채점 PoC**(녹음텍스트→STT(mock)→정답비교+LLM(mock) 피드백→점수→블룸 적립)
- **S1 ✅(골격)** `/auth/login`(소셜 upsert) · `/onboarding/profile`(세그먼트 분기)
- **S2 ✅(골격)** `/diagnosis/submit` → 24주 로드맵 생성
- **S3 ✅(골격)** `/learning/lessons` · `/complete` · `/progress`
- **S4 ✅(PoC)** `/speaking/score` (실제 audio STT 연동은 TODO)
- **S5 ✅(골격)** `/billing/subscribe` (3티어, mock PG)
- **S6 ✅(골격)** `/billing/refund/check` (완주율·환급 대상 판정) + 리워드 원장
- **S7/S8** QA·스토어 심사 — 실제 빌드 누적 후 진행(체크리스트는 스프린트 백로그 문서 참고)

## 핵심 흐름 (S4)
`/speaking/score` 에 목표문장+발화(텍스트)를 보내면 유사도 채점 + 피드백 반환, 통과 시 블룸 10 적립.
실제 운영 전환: `app/services/speech.py` 의 `transcribe()`(STT)·`llm_feedback()`(LLM)에
Whisper/Google·GPT/Claude 연동 추가, `.env` 의 `STT_PROVIDER`/`LLM_PROVIDER` 를 mock→실제로 변경.

## 다음 작업(TODO)
- 실제 STT/LLM/PG 연동, audio 업로드(Storage), 소셜토큰 검증
- Story/Scene/Affinity(호감도 게임), 커뮤니티/리뷰/추천 라우트 — v1
- Alembic 마이그레이션, 권한·레이트리밋, 개인정보 암호화

> 가격·환급 조건·자동결제·저작권은 집행 전 법무/전문가 검토 필요.

## 프론트엔드
- `web/` — 빌드 없는 HTML/JS 데모(로그인→온보딩→진단→발화채점→구독/환급). `python -m http.server 5500`.
- `mobile/` — Expo(React Native) 스타터 `App.js`. `npx create-expo-app` 후 교체.

## 실제 STT/LLM 연동 (키 넣으면 동작)
`.env` 에서:
```
STT_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```
- 텍스트 채점: `POST /speaking/score` (브라우저 Web Speech 결과 등)
- 오디오 채점: `POST /speaking/score-audio` (multipart: target_sentence, audio) → Whisper STT → GPT 피드백
- Anthropic 사용 시 `LLM_PROVIDER=anthropic` + 키 설정(`_llm_anthropic`).
- 어떤 경우든 실패하면 자동 mock 폴백(서비스 중단 없음).

## v1 구현 추가 (개발 문서 전체 반영)
스토리게임·커뮤니티·후기→추천·리워드까지 ERD 전 엔티티 + 엔드포인트 구현. 테스트 5건 통과.

| Method | Path | 설명 |
|---|---|---|
| GET | /story/list · /story/{id}/scenes | 스토리·장면(해금 상태) |
| POST | /story/speak | 장면 발화 채점 → 호감도↑·다음 장면 해금 |
| GET | /community/rooms · /community/feed | 스터디룸·피드 |
| POST | /community/post | 게시/완주 인증(+블룸 20) |
| POST | /social/review | 후기 작성 → 추천코드 발급(+블룸 50) |
| POST | /social/redeem | 추천코드 사용(추천인 +100·피추천인 +30) |
| GET | /reward/ledger | 블룸 잔액·내역 |

전체 모델: User·Profile·Diagnosis·Roadmap·Course·Lesson·Progress·SpeakAttempt·Subscription·Payment·CompletionRefund·RewardLedger·Story·Scene·AffinityState·StudyRoom·Post·Referral·Review·ContentAsset (20종).

## 마이그레이션 (Alembic)
```
python -m alembic upgrade head      # 스키마 생성/업데이트
python -m alembic revision --autogenerate -m "change"   # 모델 변경 후 새 마이그레이션
```
초기 마이그레이션(20개 테이블)이 `migrations/versions/`에 포함되어 있습니다. Docker는 `entrypoint.sh`가 `alembic upgrade head → seed → uvicorn` 순으로 실행합니다.

## 외부 연동 상태 점검
```
python scripts/verify_providers.py   # STT/LLM/PG 키 유무 + LLM dry-run
GET /meta/providers                  # 런타임 프로바이더 상태(JSON)
```
결제: `POST /billing/confirm`(Toss 결제위젯 승인 콜백 확정). `PG_PROVIDER=toss`+`PG_SECRET_KEY` 설정 시 실제 Toss confirm API 호출, 아니면 mock 승인.

## 사전신청 수집 (공개 API)
- `POST /signup` {email, lang, source} — 중복 멱등. `GET /signup/count` 공개, `GET /signup/list` 토큰 필요.
- 정적 사이트(bloomspeak.kr)에서 쓰려면 백엔드를 배포(공개 URL+CORS)한 뒤 `web` 또는 `bloomspeak-web/index.html` 의 `BACKEND` 에 API 주소를 넣으세요. 백엔드 미배포 시엔 Formspree/Tally 로도 연동 가능.

## 실키 검증 빠른 절차
```
# .env 편집
OPENAI_API_KEY=sk-...
STT_PROVIDER=openai
LLM_PROVIDER=openai
PG_PROVIDER=toss
PG_SECRET_KEY=test_sk_...
# 1) 프로바이더/LLM 점검
python scripts/verify_providers.py
# 2) 실제 오디오 발화 채점 (multipart)  — target_sentence 와 audio 파일
curl -X POST http://localhost:8000/speaking/score-audio \
  -H "Authorization: Bearer <토큰>" \
  -F "target_sentence=Can I get a flat white" \
  -F "audio=@sample.m4a"
# 3) 결제 확정 (Toss 결제위젯 승인 후 paymentKey/orderId/amount 로)
curl -X POST "http://localhost:8000/billing/confirm?payment_key=...&order_id=...&amount=49000" -H "Authorization: Bearer <토큰>"
```
