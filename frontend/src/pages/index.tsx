import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const ChatPage = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [assistantName, setAssistantName] = useState('비서');
  const [systemPrompt, setSystemPrompt] = useState('당신은 친절한 AI 비서입니다.');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  const navigate = useNavigate();

  // 설정 불러오기
  useEffect(() => {
    const storedName = localStorage.getItem('assistantName');
    const storedPrompt = localStorage.getItem('systemPrompt');
    const storedAvatar = localStorage.getItem('avatarUrl');
    if (storedName) setAssistantName(storedName);
    if (storedPrompt) setSystemPrompt(storedPrompt);
    if (storedAvatar) setAvatarUrl(storedAvatar);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, `🙋‍♂️ 너: ${input}`]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: input,
        system_prompt: systemPrompt,
      });

      // 응답에서 answer 키로 접근하여 메시지 표시
      setMessages((prev) => [...prev, `🤖 ${assistantName}: ${response.data.answer}`]);
    } catch (error: any) {
      setMessages((prev) => [...prev, `⚠️ 오류: ${error.message}`]);
    } finally {
      setInput('');
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: '2rem', padding: '2rem', fontFamily: 'sans-serif' }}>
      {/* 왼쪽: 캐릭터 이미지 */}
      <div style={{ width: '40%', textAlign: 'center' }}>
        {avatarUrl ? (
          <img
            src={avatarUrl}
            alt="AI 캐릭터"
            style={{ maxWidth: '100%', borderRadius: '1rem' }}
          />
        ) : (
          <p>⚠️ 캐릭터 이미지를 설정해 주세요</p>
        )}
      </div>

      {/* 오른쪽: 대화 UI */}
      <div style={{ width: '60%' }}>
        <h1>{assistantName}와 대화하기</h1>

        <div
          style={{
            maxHeight: '400px',
            overflowY: 'auto',
            marginBottom: '1rem',
            border: '1px solid #ccc',
            padding: '1rem',
            backgroundColor: '#f9f9f9',
          }}
        >
          {messages.map((msg, i) => (
            <div key={i} style={{ marginBottom: '0.5rem' }}>{msg}</div>
          ))}
        </div>

        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="메시지를 입력하세요"
          style={{ width: '70%', padding: '0.5rem', fontSize: '1rem' }}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{ padding: '0.5rem 1rem', marginLeft: '0.5rem' }}
        >
          {loading ? '생각 중...' : '보내기'}
        </button>

        {/* 설정으로 이동 버튼 */}
        <button
          onClick={() => navigate('/setup')}
          style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}
        >
          ⚙️ 비서 설정 다시 하기
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
