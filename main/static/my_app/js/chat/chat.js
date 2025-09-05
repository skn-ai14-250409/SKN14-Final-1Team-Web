console.log('채팅 페이지 JavaScript 시작!');
const sessionList = document.getElementById('sessionList');
const sessionTitle = document.getElementById('sessionTitle');

let selectedSessionId = null; // 현재 선택된 세션 id


// 요소 선택
const chatLog = document.getElementById('chatLog');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

const newsessionBtn = document.querySelector('.btn-new-chat');

if (newsessionBtn) {
  newsessionBtn.addEventListener('click', session_create);
} else {
  console.warn('.btn-new-chat 를 찾지 못했습니다.');}

// 초기 세션 선택 (Django 템플릿으로 렌더링된 첫 번째 세션 선택)
async function initializeFirstSession() {
    if (!sessionList) { 
    console.warn('#sessionList 가 없어 초기 선택을 건너뜀'); 
    return;
    }
  const firstSession = sessionList.querySelector('.session-link');
  if (firstSession) {
    selectedSessionId = firstSession.dataset.sessionId;
    sessionTitle.textContent = firstSession.textContent.trim();
    firstSession.parentElement.classList.add('is-active');
    await loadChatHistory(selectedSessionId);
  }
}

// 세션 클릭 이벤트
if (sessionList) {
  sessionList.addEventListener('click', async (e) => {
    // 삭제 버튼 클릭 처리
    if (e.target.classList.contains('delete-btn')) {
      const sessionId = e.target.dataset.sessionId;
      if (confirm('이 세션을 삭제하시겠습니까?')) {
        await deleteSession(sessionId);
      }
      return;
    }

  // 세션 선택 처리
  const btn = e.target.closest('.session-link');
  if (!btn) return;
  selectedSessionId = btn.dataset.sessionId;
  console.log('선택된 세션 ID:', selectedSessionId);
  sessionTitle.textContent = btn.textContent.trim();

  // 선택 표시 업데이트
  document.querySelectorAll('#sessionList .is-active').forEach(el => el.classList.remove('is-active'));
  btn.parentElement.classList.add('is-active');

  // 채팅 히스토리 로드
  await loadChatHistory(selectedSessionId);
});
} else {
    console.warn('#sessionList 요소가 없어 세션 클릭 바인딩을 건너뜀');
}

// 세션 삭제 함수
async function deleteSession(sessionId) {
  try {
    const response = await fetch(`/api-chat/delete_session/${sessionId}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'same-origin'
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // 삭제된 세션을 리스트에서 제거
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`).parentElement;
    sessionItem.remove();

    // 현재 선택된 세션이 삭제된 경우 채팅 내역 비우기
    if (selectedSessionId === sessionId) {
      selectedSessionId = null;
      sessionTitle.textContent = '세션을 선택하세요';
      chatLog.innerHTML = '';
    }

    console.log(`세션 ${sessionId} 삭제 완료`);

  } catch (err) {
    console.error('세션 삭제 실패:', err);
    alert('세션 삭제에 실패했습니다.');
  }
}

// 채팅 히스토리 로드 함수
async function loadChatHistory(sessionId) {
  try {
    const response = await fetch(`/api-chat/chat_history/${sessionId}/`, {
      credentials: 'same-origin'
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    
    // 채팅창 초기화
    chatLog.innerHTML = '';
    
    // 메시지 히스토리 표시
    data.messages.forEach(msg => {
  addMessage(msg.content, msg.role === 'user' ? 'user' : 'assistant', msg.id); // id 전달
    });

    console.log(`세션 ${sessionId} 히스토리 로드 완료:`, data.messages.length, '개 메시지');

  } catch (err) {
    console.error('채팅 히스토리 로드 실패:', err);
    chatLog.innerHTML = '<li class="error">채팅 히스토리를 불러올 수 없습니다.</li>';
  }
}

// 초기 실행 (새로고침 시, 가장 첫번째 채팅세션을 선택하도록)
initializeFirstSession();



async function session_create() {
  try {
    const csrfToken = getCSRFToken();

    const response = await fetch('/api-chat/session_create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
      body: JSON.stringify({ title: 'title' }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error('HTTP', response.status, text);
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('성공', data);

    // 새 세션 리스트에 추가
    const li = document.createElement('li');
    li.className = 'session-item';
    li.innerHTML = `
      <button class="session-link" data-session-id="${data.session.id}">${data.session.title}</button>
      <button class="delete-btn" data-session-id="${data.session.id}">×</button>
    `;
    // sessionList가 있을 때만 prepend 호출
    if (sessionList) { 
      sessionList.prepend(li); 
    } else {
      console.warn('#sessionList 없음: 새 세션 UI 추가를 건너뜀');
    }

    // 새 세션 자동 선택
    selectedSessionId = data.session.id;
    sessionTitle.textContent = data.session.title;
    
    // 선택 표시 업데이트
    document.querySelectorAll('#sessionList .is-active').forEach(el => el.classList.remove('is-active'));
    li.classList.add('is-active');
    
    // 채팅창 초기화 (새 세션이므로 빈 상태)
    chatLog.innerHTML = '';
    
    console.log('새 세션 생성 및 선택 완료:', selectedSessionId);
  } catch (err) {
    console.error('요청 실패:', err);
  }
}



function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/[&<>"']/g, (m) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]
  ));
}

// 메시지를 채팅창에 추가하는 함수
function addMessage(text, role = 'user', id = null) {
  const li = document.createElement('li');
  li.className = `msg msg--${role}`;   // 선택 모드가 찾는 클래스
  if (id != null) li.dataset.mid = id; // 데이터 id 부여
  li.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  chatLog.appendChild(li);
  chatLog.scrollTop = chatLog.scrollHeight;
}

// 메시지 전송 공통 함수
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return; // 빈 입력은 무시

  // 현재 선택된 세션 확인
  if (!selectedSessionId) {
    alert('세션을 선택해주세요.');
    return;
  }

  // 입력 메시지를 채팅창에 추가
  addMessage(message, 'user');

  // 입력창 비우기
  chatInput.value = '';

  // 서버 전송 (추후 API 연동 가능)
  console.log('사용자 질문 전송:', message, '세션 ID:', selectedSessionId);

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
      body: JSON.stringify({ 
        message: message,
        session_id: selectedSessionId 
      }),
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
      addMessage(data.bot_message ?? `봇 응답 예시: "${message}"에 대한 답변입니다.`, 'assistant');

      if (data.title) {
        if(sessionTitle) sessionTitle.textContent = data.title;

        const btn = document.querySelector(
            `#sessionList .session-link[data-session-id="${selectedSessionId}"]`
        );
        if (btn) btn.textContent = data.title;
      }
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
  return '';}


// ---------- 선택 모드 상태 ----------
let selecting = false;
let selectedIds = []; // 순서대로

const $chatLog   = document.getElementById('chatLog');
const $btnSelect = document.getElementById('btnCardSelect');
const $btnSave   = document.getElementById('btnCardSave');
const $selCount  = document.getElementById('selCount');
// const sessionId  = document.getElementById('ctx')?.dataset.sessionId; // 템플릿에서 주입

// CSRF
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}
const CSRF = getCookie('csrftoken');

// 카드 버튼/카운터 요소 존재 여부 가드 + 초기 상태 보정
if ($btnSave) $btnSave.disabled = true;
if (!$btnSelect || !$btnSave || !$selCount) {
  console.warn('카드 버튼 또는 카운터 요소를 찾지 못했습니다. 선택 기능을 건너뜁니다.');
} else {

// -------- 선택 모드 ON/OFF --------
$btnSelect.addEventListener('click', () => {
  selecting = !selecting;
  selectedIds = [];
  updateSelectUI();

  // 버튼 라벨/상태
  $btnSelect.textContent = selecting ? '선택 취소' : '카드만들기';
  $btnSave.disabled = !selecting;
  $selCount.style.display = selecting ? 'inline' : 'none';
  $selCount.textContent = '0개 선택';
});

// -------- 메시지 클릭으로 선택/해제 --------
$chatLog.addEventListener('click', (e) => {
  if (!selecting) return;
  const li = e.target.closest('li.msg');
  if (!li) return;

  const mid = li.dataset.mid;
  if (!mid) return;

  // 토글
  const idx = selectedIds.indexOf(mid);
  if (idx === -1) selectedIds.push(mid);
  else selectedIds.splice(idx, 1);

  updateSelectUI();
});

// -------- 선택 UI 갱신 --------
function updateSelectUI() {
  // 스타일/체크박스 표시
  [...$chatLog.querySelectorAll('li.msg')].forEach(li => {
    const mid = li.dataset.mid;
    const chosen = selectedIds.includes(mid);

    if (selecting) {
      li.classList.toggle('msg--selecting', true);
      li.classList.toggle('msg--chosen', chosen);

      // 체크 오버레이 (없으면 생성)
      let mark = li.querySelector('.select-mark');
      if (!mark) {
        mark = document.createElement('span');
        mark.className = 'select-mark';
        mark.textContent = '✓';
        li.appendChild(mark);
      }
      mark.style.display = 'inline';
      mark.style.opacity = chosen ? '1' : '0.25';
    } else {
      li.classList.remove('msg--selecting','msg--chosen');
      const mark = li.querySelector('.select-mark');
      if (mark) mark.remove();
    }
  });

  $selCount.textContent = `${selectedIds.length}개 선택`;
}

// -------- 카드 저장 --------
$btnSave.addEventListener('click', async () => {
  if (!selecting) return;
  if (!selectedSessionId) { alert('세션 ID가 없습니다.'); return; }
  if (selectedIds.length === 0) { alert('선택된 메시지가 없습니다.'); return; }

  // 제목 입력 받기. 비우면 서버가 session.title 사용
  const title = prompt('카드 제목(비우면 세션 제목 사용)') || '';

  try {
    const res = await fetch('/api-chat/cards/save/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': CSRF
      },
      body: JSON.stringify({
        session_id: Number(selectedSessionId),
        title,
        message_ids: selectedIds.map(Number) // INT PK라면 숫자 변환
      })
    });

    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data.error || '저장 실패');

    alert('카드 저장 완료!');
  } catch (err) {
    console.error(err);
    alert(`저장 중 오류: ${err.message}`);
  } finally {
    // 선택 모드 종료
    selecting = false;
    selectedIds = [];
    updateSelectUI();
    $btnSelect.textContent = '카드만들기';
    $btnSave.disabled = true;
    $selCount.style.display = 'none';
  }
});
}
