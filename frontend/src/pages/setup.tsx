import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const SetupPage = () => {
  const [name, setName] = useState("아리아");
  const [prompt, setPrompt] = useState("당신은 친근하고 똑똑한 AI 비서입니다.");
  const [characterPrompt, setCharacterPrompt] = useState("귀엽고 다정한 AI 캐릭터");
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [gptAnswer, setGptAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const navigate = useNavigate();

  // GPT 대답을 받아오는 함수
  const getGptResponse = async (message: string) => {
    const systemPrompt = localStorage.getItem("systemPrompt") || "당신은 친근한 AI 비서입니다."; // 기본값 설정

    try {
      const res = await axios.post("http://localhost:8000/api/chat", {
        message: message,
        system_prompt: systemPrompt, // 시스템 프롬프트 동적 사용
      });

      if (res.data.answer) {
        setGptAnswer(res.data.answer); // GPT 대답을 상태로 설정
      } else {
        setGptAnswer("Sorry, I couldn't understand that.");
      }
    } catch (error) {
      console.error("GPT API 호출 오류:", error);
      setGptAnswer("Sorry, something went wrong. Please try again.");
    }
  };

  // 이미지 생성 함수
  const generateImage = async () => {
    setLoading(true);
    setImageBase64(null);
    setSelected(null);
    try {
      const res = await axios.post("http://localhost:8000/api/generate-character-image", {
        prompt: characterPrompt,
      });

      if (res.data.image_base64) {
        setImageBase64(res.data.image_base64);
      } else {
        alert("이미지 생성 실패. 응답 확인 필요.");
        console.error(res.data);
      }
    } catch (err) {
      console.error("이미지 생성 오류:", err);
      alert("이미지 생성 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 설정을 저장하고 대화 페이지로 이동
  const saveSettings = () => {
    if (!selected) {
      alert("캐릭터 이미지를 선택해주세요.");
      return;
    }
    localStorage.setItem("assistantName", name);
    localStorage.setItem("systemPrompt", prompt); // 시스템 프롬프트 저장
    localStorage.setItem("avatarUrl", selected);
    navigate("/");
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2>🧠 AI 비서 설정</h2>

      <label>비서 이름:</label>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        style={{ width: "100%", padding: "0.5rem", marginBottom: "1rem" }}
      />

      <label>비서 성격/말투 설명 (프롬프트):</label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        style={{ width: "100%", height: "100px", padding: "0.5rem", marginBottom: "1rem" }}
      />

      <label>캐릭터 외형 설명 (프롬프트):</label>
      <input
        value={characterPrompt}
        onChange={(e) => setCharacterPrompt(e.target.value)}
        style={{ width: "100%", padding: "0.5rem" }}
      />
      <button
        onClick={generateImage}
        disabled={loading}
        style={{ display: "block", marginTop: "1rem", marginBottom: "1rem" }}
      >
        {loading ? "이미지 생성 중..." : "이미지 생성"}
      </button>

      {imageBase64 && (
        <img
          src={`data:image/png;base64,${imageBase64}`}
          alt="생성된 캐릭터"
          style={{
            width: "256px", // 크기 조정
            borderRadius: "10px",
            marginTop: "1rem",
            border: selected === `data:image/png;base64,${imageBase64}` ? "3px solid #007BFF" : "2px solid #ccc",
            cursor: "pointer",
          }}
          onClick={() => {
            const full = `data:image/png;base64,${imageBase64}`;
            localStorage.setItem("avatarUrl", full);
            setSelected(full);
          }}
        />
      )}

      <button
        onClick={saveSettings}
        style={{ marginTop: "2rem", padding: "0.75rem 1.5rem", fontSize: "1rem" }}
      >
        설정 완료 → 대화 시작하기
      </button>

      <hr />
      <h3>💬 AI 비서 대화</h3>
      <textarea
        placeholder="여기에 질문을 입력하세요"
        style={{ width: "100%", padding: "0.5rem", marginBottom: "1rem" }}
        onKeyPress={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            getGptResponse(e.currentTarget.value);
            e.preventDefault();
          }
        }}
      />
      <div>
        <strong>GPT 대답:</strong>
        <p>{gptAnswer}</p>
      </div>
    </div>
  );
};

export default SetupPage;
