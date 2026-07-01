# BLOOM Web Client (데모)
백엔드(S0~S6)에 붙는 순수 HTML/JS 데모. 빌드 불필요.

## 실행
1) 백엔드 먼저: `uvicorn app.main:app --reload`
2) 이 폴더에서: `python -m http.server 5500` → http://localhost:5500
3) 상단 API 칸이 http://localhost:8000 인지 확인 후 ①→⑥ 순서로 클릭.

흐름: 로그인 → 온보딩(세그먼트/목적) → 진단 → 레슨 선택 → 🎙️말하기(크롬 Web Speech) 또는 직접입력 → 채점/피드백/블룸 적립 → 구독/환급확인.
실제 제품 웹은 Next.js 권장(이 데모의 fetch 로직을 컴포넌트로 이전).
