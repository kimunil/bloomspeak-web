# BLOOM Mobile (Expo 스타터)
```
npx create-expo-app bloom-app
# 생성된 App.js 를 이 폴더의 App.js 로 교체
cd bloom-app && npx expo start
```
- 실기기 테스트 시 App.js 의 API_BASE 를 PC LAN IP(예: http://192.168.0.10:8000)로 변경.
- 실제 음성: `expo-av` 로 녹음 → `/speaking/score-audio` 멀티파트 업로드(STT 키 설정 시 Whisper 채점).
- 프로덕션 권장: React Native(Expo) 또는 Flutter 한 코드베이스, 큰글씨·음성 접근성(5060) 우선 QA.
