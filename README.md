# bloomspeak-web — BLOOM English 공개 사이트 (bloomspeak.kr)

이중언어(한/영) 랜딩 + 사전신청 페이지. 빌드 불필요한 정적 사이트라 GitHub Pages·Vercel·Netlify 어디든 바로 배포됩니다.

## 로컬 미리보기
```
python -m http.server 5500   # http://localhost:5500
```

## 사전신청 폼 연동 (1분)
`index.html`의 `action="https://formspree.io/f/your-id"` 를 실제 폼 endpoint로 교체하세요.
- 무료 추천: Formspree(formspree.io) 또는 Google Form, Tally. 가입 후 받은 endpoint URL을 붙여넣으면 이메일이 수집됩니다.
- 교체 전에는 데모(로컬 알림)로 동작합니다.

---

## A. GitHub 레포 만들고 올리기
```bash
cd bloomspeak-web
git init
git add .
git commit -m "BLOOM English public site (bloomspeak.kr)"
# GitHub에서 빈 레포 'bloomspeak-web' 생성 후:
git remote add origin https://github.com/<계정>/bloomspeak-web.git
git branch -M main
git push -u origin main
```

## B. 배포 — 택1

### ① GitHub Pages (무료, 이 레포에 워크플로 포함)
1. 레포 → Settings → Pages → Source: **GitHub Actions** 선택.
2. push하면 `.github/workflows/deploy-pages.yml`가 자동 배포.
3. Settings → Pages → Custom domain에 **bloomspeak.kr** 입력 → 저장(레포의 `CNAME` 파일이 이미 있음).
4. "Enforce HTTPS" 체크(인증서 자동 발급까지 몇 분~수십 분).

### ② Vercel (가장 간단)
- vercel.com에서 레포 Import → Deploy → Domains에 bloomspeak.kr 추가.

### ③ Netlify
- netlify.com에서 레포 연결 → Deploy → Domain settings에 bloomspeak.kr 추가.

---

## C. 가비아(Gabia) DNS 설정 — bloomspeak.kr 연결

가비아 → My가비아 → 도메인 → bloomspeak.kr → **DNS 관리(DNS 정보)** 에서 아래 레코드를 추가/수정하세요.

### GitHub Pages 사용 시 (apex 도메인)
| 타입 | 호스트/이름 | 값/레코드 | TTL |
|---|---|---|---|
| A | @ | 185.199.108.153 | 3600 |
| A | @ | 185.199.109.153 | 3600 |
| A | @ | 185.199.110.153 | 3600 |
| A | @ | 185.199.111.153 | 3600 |
| CNAME | www | <계정>.github.io. | 3600 |

(IPv6도 쓰려면 AAAA로 2606:50c0:8000::153 / ::8001::153 / ::8002::153 / ::8003::153 추가)

### Vercel 사용 시
| 타입 | 호스트 | 값 |
|---|---|---|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com. |

### Netlify 사용 시
| 타입 | 호스트 | 값 |
|---|---|---|
| A | @ | 75.2.60.5 |
| CNAME | www | <사이트>.netlify.app. |

> DNS 전파는 보통 수 분~수 시간. 적용 후 https://bloomspeak.kr 접속 확인.

## D. 업무 이메일 (hello@bloomspeak.kr) — 선택
구글 워크스페이스/네이버웍스 가입 후 안내되는 **MX / SPF(TXT)** 레코드를 같은 DNS 관리에 추가하면 됩니다. (도메인 메일 발신 신뢰도↑)

---

## 다음 개발
- 사전신청 이메일 → 백엔드(bloom-backend) 연동 또는 메일링(스티비/메일침프).
- 앱 출시 후 이 사이트에 앱스토어/플레이 배지 추가.
- KO/EN 외 카피·OG 이미지·GA4 추가.

*가격·환급 조건·일정은 예시이며 집행 전 표시·광고 표현 검토가 필요합니다.*
