# BLOOM English API — 무료 배포 가이드 (Render)

목표: 백엔드를 Render 무료 플랜에 올려 **`https://api.bloomspeak.kr`** 로 접속되게 하고,
앱에서 **이메일 로그인(+소셜 데모)** 이 실제로 동작하게 만듭니다.

준비물: 대표님의 GitHub 계정(kimunil, 이미 로그인됨), Render 계정(무료·GitHub로 30초 가입), 가비아 DNS 접근.

---

## 1) 코드를 GitHub 리포에 올리기
이미 `render.yaml` 블루프린트가 포함돼 있어 리포만 있으면 원클릭 배포됩니다.
- 새 리포: **github.com/kimunil/bloomspeak-api** (Public)
- 이 폴더(`bloom-backend`) 내용 전체를 push
  (제가 브라우저로 리포 생성·업로드를 도와드릴 수 있습니다.)

## 2) Render에서 Blueprint 배포 (계정 로그인은 대표님이)
1. https://render.com 접속 → **Get Started** → **GitHub로 로그인**(대표님 계정)
2. 대시보드 → **New +** → **Blueprint**
3. `bloomspeak-api` 리포 선택 → Render가 `render.yaml`을 자동 인식
4. **Apply** 클릭 → 빌드(2~4분) → 상태가 **Live** 가 되면 완료
5. 발급된 주소 확인: 예) `https://bloomspeak-api.onrender.com`
   - 브라우저에서 `…/health` 열어 `{"status":"ok"}` 뜨면 서버 정상

> JWT_SECRET 은 Render가 자동 생성합니다. DB는 데모용 SQLite(재배포 시 초기화).
> 영구 저장이 필요하면 `render.yaml` 하단 주석의 무료 Postgres 블록을 켜세요.

## 3) 커스텀 도메인 연결 → api.bloomspeak.kr
앱은 이미 `api.bloomspeak.kr` 를 호출하도록 설정돼 있습니다. 도메인만 연결하면 됩니다.
1. Render → 서비스 → **Settings → Custom Domains → Add** → `api.bloomspeak.kr` 입력
2. Render가 안내하는 **CNAME 대상**(예: `bloomspeak-api.onrender.com`)을 복사
3. **가비아 DNS** → bloomspeak.kr → DNS 관리 → 레코드 추가
   - 타입 **CNAME** / 호스트 **api** / 값 **(2에서 복사한 onrender 주소)** / TTL 3600
4. 5~30분 후 Render의 도메인 상태가 **Verified**(자물쇠) 로 바뀜 → HTTPS 자동 발급

## 4) 로그인 실제 동작 확인
- **이메일 로그인**: 도메인 연결 즉시 동작(키 불필요).
- **소셜 로그인**: 키를 안 넣으면 데모(mock)로 로그인됩니다. 실제 계정 연동은 5)에서.

## 5) (선택) 소셜 로그인 실연동 — 키 입력 위치
민감키는 **코드/문서에 넣지 말고** Render 대시보드 환경변수에만 입력하세요.
Render → 서비스 → **Environment** → 아래 값 입력(콘솔에서 발급):
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`
- `KAKAO_REST_API_KEY` (필요시 `KAKAO_CLIENT_SECRET`)

각 콘솔의 **Redirect URI** 는 모두:
`https://api.bloomspeak.kr/auth/{provider}/callback`
(google/naver/kakao 로 치환) — 이미 콘솔에 등록해 두셨습니다.
앱쪽 `src/config/oauth.js` 의 google/naver `clientId` 도 채우면 소셜 버튼이 실제 동의창으로 연결됩니다.

---

## 요약 체크리스트
- [ ] GitHub `bloomspeak-api` 리포 생성 + 코드 push
- [ ] Render Blueprint 배포 → `/health` OK
- [ ] Custom Domain `api.bloomspeak.kr` 추가 + 가비아 CNAME
- [ ] 앱에서 이메일 로그인 성공 확인
- [ ] (선택) 소셜 키 입력 → 실연동

## 대표님이 직접 하셔야 하는 부분 (제가 대신 못 하는 것)
- Render 계정 로그인/가입, **Apply** 클릭 (계정 자격증명 필요)
- 가비아 DNS 레코드 저장 (계정 로그인 필요)
- 소셜 client_secret 입력 (민감키는 서버에만)

## 제가 지금 도와드릴 수 있는 부분
- GitHub `bloomspeak-api` 리포 생성 + 코드 업로드(브라우저)
- 배포 후 `/health`·`/auth/login` 원격 점검
