// 요소 선택
const chatLog = document.getElementById('chatLog');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// 메시지를 채팅창에 추가하는 함수
function addMessage(text, role = 'user') {
  const li = document.createElement('li');
  li.textContent = text;
  li.className = role;
  chatLog.appendChild(li);
  chatLog.scrollTop = chatLog.scrollHeight; // 자동 스크롤
}

// 메시지 전송 공통 함수
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return; // 빈 입력은 무시

  // 입력 메시지를 채팅창에 추가
  addMessage(message, 'user');

  // 입력창 비우기
  chatInput.value = '';

  // 서버 전송 (추후 API 연동 가능)
  console.log('사용자 질문 전송:', message);

  // 임시 봇 응답 + 서버 호출
  try {
    const csrfToken = getCSRFToken();

    const response = await fetch('/api-chat/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,        // Django 표준 헤더명
      },
      credentials: 'same-origin',         // 쿠키 포함 (csrftoken 사용 시 필요)
      body: JSON.stringify({ message }),
    });

    // 네트워크/HTTP 에러 체크
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // JSON 파싱은 await 필요
    const data = await response.json();

    // 성공 여부에 따라 처리 (서버 스키마에 맞게 조정)
    if (data.success) {
      // 실제 응답 텍스트 키가 있으면 그걸 사용 (예: data.reply)
      addMessage(data.bot_message ?? `봇 응답 예시: "${message}"에 대한 답변입니다.`, 'bot');
    }
  } catch (err) {
    console.error('요청 실패:', err);
    addMessage('서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.', 'bot');
  } finally {
    // 필요 시 로딩 인디케이터 끄기 등 후처리
  }
}

// 보내기 버튼 클릭 이벤트
sendBtn.addEventListener('click', sendMessage);

// 엔터 키 이벤트 (Shift+Enter는 줄바꿈 유지)
chatInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault(); // 줄바꿈 방지
    sendMessage();
  }
});

// csrf 토큰 찾기
function getCSRFToken() {
  // 1) form input
  let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  if (token) return token;

  // 2) meta 태그
  token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (token) return token;

  // 3) 쿠키
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') return value;
  }

  console.warn('CSRF 토큰을 찾을 수 없습니다.');
  return '';
}
