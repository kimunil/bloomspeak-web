// BLOOM English — Expo(React Native) 스타터 (발화채점 흐름 데모)
// 셋업:  npx create-expo-app bloom-app   →  이 App.js 로 교체  →  npx expo start
// 실기기에서 API_BASE 를 PC의 LAN IP로 변경하세요(예: http://192.168.0.10:8000).
import React, { useState } from "react";
import { SafeAreaView, View, Text, TextInput, TouchableOpacity, ScrollView } from "react-native";

const API_BASE = "http://localhost:8000";
const C = { coral: "#F04E6A", ame: "#6B3FA0", ink: "#22264B", soft: "#FAF7FD", line: "#ECE4F2", mut: "#7B7F9A" };

export default function App() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("demo@bloom.io");
  const [target] = useState("I am here to visit my friend");
  const [said, setSaid] = useState("I am here to visit my friend");
  const [log, setLog] = useState("로그인부터 시작하세요.");

  const api = async (path, opt = {}) => {
    const h = { "Content-Type": "application/json", ...(opt.headers || {}) };
    if (token) h.Authorization = "Bearer " + token;
    const r = await fetch(API_BASE + path, { ...opt, headers: h, body: opt.body ? JSON.stringify(opt.body) : undefined });
    const j = await r.json();
    if (!r.ok) throw new Error(JSON.stringify(j));
    return j;
  };

  const login = async () => { try { const j = await api("/auth/login", { method: "POST", body: { email } }); setToken(j.access_token); setLog("✅ 로그인 OK (user " + j.user_id + ")"); } catch (e) { setLog(e.message); } };
  const onboard = async () => { try { const j = await api("/onboarding/profile", { method: "POST", body: { segment: "5060", goal: "travel" } }); setLog("온보딩: " + JSON.stringify(j)); } catch (e) { setLog(e.message); } };
  const diagnose = async () => { try { const j = await api("/diagnosis/submit", { method: "POST", body: { answers: [1, 0, 1, 0] } }); setLog(`진단 ${j.score} · ${j.weakness} · ${j.weeks}주`); } catch (e) { setLog(e.message); } };
  // 실기기 음성: expo-av 로 녹음 → /speaking/score-audio 멀티파트 업로드. 여기선 텍스트 채점.
  const score = async () => { try { const j = await api("/speaking/score", { method: "POST", body: { target_sentence: target, transcript: said } }); setLog(`점수 ${j.score} · ${j.passed ? "통과 +🌸10" : "다시"}\n${j.feedback}`); } catch (e) { setLog(e.message); } };

  const Btn = ({ t, onPress, ghost }) => (
    <TouchableOpacity onPress={onPress} style={{ backgroundColor: ghost ? "#fff" : C.coral, borderColor: "#C9B8E8", borderWidth: ghost ? 1.5 : 0, padding: 13, borderRadius: 12, marginTop: 8 }}>
      <Text style={{ color: ghost ? C.ame : "#fff", fontWeight: "800", textAlign: "center" }}>{t}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.soft }}>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={{ fontSize: 24, fontWeight: "800", color: C.ame }}>🌸 BLOOM English</Text>
        <Text style={{ color: C.mut, marginBottom: 14 }}>Expo 스타터 — 백엔드 연동 데모</Text>
        <TextInput value={email} onChangeText={setEmail} style={{ backgroundColor: "#fff", borderColor: C.line, borderWidth: 1.5, borderRadius: 10, padding: 10 }} />
        <Btn t="① 로그인 / 가입" onPress={login} />
        <Btn t="② 온보딩(5060·여행)" onPress={onboard} ghost />
        <Btn t="③ 진단 → 로드맵" onPress={diagnose} ghost />
        <Text style={{ color: C.mut, marginTop: 16 }}>목표 문장</Text>
        <Text style={{ fontWeight: "700", color: C.ink, marginBottom: 6 }}>{target}</Text>
        <TextInput value={said} onChangeText={setSaid} style={{ backgroundColor: "#fff", borderColor: C.line, borderWidth: 1.5, borderRadius: 10, padding: 10 }} />
        <Btn t="④ 발화 채점" onPress={score} />
        <View style={{ backgroundColor: "#fff", borderColor: C.line, borderWidth: 1, borderRadius: 12, padding: 14, marginTop: 16 }}>
          <Text style={{ color: C.ink }}>{log}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
