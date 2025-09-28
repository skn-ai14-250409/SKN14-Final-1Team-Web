console.log('채팅 페이지 JavaScript 시작!');
const sessionList = document.getElementById('sessionList');
const sessionTitle = document.getElementById('sessionTitle');

let selectedSessionId = null; // 현재 선택된 세션 id
let selectedImage = null; // 선택된 이미지 데이터
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;


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
  // 추가=======
  const urlParams = new URLSearchParams(window.location.search);
  const sessionIdFromUrl = urlParams.get('session_id');

  if (sessionIdFromUrl) {
    // URL에서 세션 ID를 찾았다면 해당 세션을 선택
    const sessionLink = document.querySelector(`[data-session-id="${sessionIdFromUrl}"]`);
    if (sessionLink) {
      selectedSessionId = sessionIdFromUrl;
      sessionTitle.textContent = sessionLink.textContent.trim();
      sessionLink.parentElement.classList.add('is-active');
      await loadChatHistory(selectedSessionId);
      return; 
    }
  }
  //=====================
  
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

  // 추가: URL 변경======
  const newUrl = new URL(window.location.href);
  newUrl.searchParams.set('session_id', selectedSessionId);
  window.history.pushState({ sessionId: selectedSessionId }, '', newUrl.href);
  //=====================
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
      // 이미지가 있으면 이미지 URL 사용
      let imageData = null;
      if (msg.images && msg.images.length > 0 && msg.images[0] && msg.images[0].url) {
        imageData = msg.images[0].url; // 이미지 URL
      }
      
      addMessage(msg.content, msg.role === 'user' ? 'user' : 'assistant', msg.id, imageData);
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
function addMessage(text, role = 'user', id = null, imageData = null) {
  const li = document.createElement('li');
  li.className = `msg msg--${role}`;
  if (id != null) li.dataset.mid = id;

  let content = `<div class="bubble">${marked.parse(text)}</div>`;

  if (imageData) {
    content += `<div class="image-preview"><img src="${imageData}" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 8px;"></div>`;
  }

  li.innerHTML = content;
  chatLog.appendChild(li);
  chatLog.scrollTop = chatLog.scrollHeight;
  return li;
}
// 메시지 전송 함수 수정
async function sendMessage() {
    const messageInput = document.getElementById('chatInput');
    const message = messageInput.value.trim();
    
    if (!message && !selectedImage) return;

    // 현재 선택된 세션 확인
    if (!selectedSessionId) {
    alert("세션을 선택해주세요.");
    return;
  }
    
    // Object URL로 즉시 표시 (임시)
    let tempImageUrl = null;
    if (selectedImage) {
        tempImageUrl = URL.createObjectURL(selectedImage);
    }
    
    // 사용자 메시지 표시 (임시 Object URL)
    addMessage(message || '[이미지]', 'user', null, tempImageUrl);
    
    // 입력 필드 초기화
    messageInput.value = '';
    
    try {
        const csrfToken = getCSRFToken();
        
        // FormData로 파일과 메시지를 함께 전송
        const formData = new FormData();
        formData.append('message', message);
        formData.append('session_id', selectedSessionId);
        if (selectedImage) {
            formData.append('image', selectedImage);
        }
        
        const response = await fetch('/api-chat/chat/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            credentials: 'same-origin',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // 서버에서 S3 URL을 받아서 메시지 업데이트
            if (data.image_url) {
                // 마지막 사용자 메시지의 이미지를 S3 URL로 업데이트
                const lastUserMessage = chatLog.querySelector('.msg--user:last-child');
                if (lastUserMessage) {
                    const img = lastUserMessage.querySelector('.image-preview img');
                    if (img) {
                        img.src = data.image_url; // S3 URL로 교체
                    }
                }
            }
            
            const assistantLi = addMessage(data.bot_message ?? `봇 응답 예시: "${message}"에 대한 답변입니다.`, 'assistant');

            if (Array.isArray(data.suggestions) && data.suggestions.length) {
                renderSuggestions(assistantLi, data.suggestions);
            }
            
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
        addMessage('죄송합니다. 요청 처리 중 오류가 발생했습니다.', 'assistant');
    } finally {
        // 임시 Object URL 정리
        if (tempImageUrl) {
            URL.revokeObjectURL(tempImageUrl);
        }
        clearImage();
    }
}

// 보내기 버튼 클릭 이벤트
sendBtn.addEventListener('click', sendMessage);

// 음성 녹음 버튼 이벤트
document.getElementById('voiceBtn').addEventListener('click', function() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

// 이미지 업로드 버튼 이벤트
document.getElementById('uploadBtn').addEventListener('click', function() {
    document.getElementById('imageInput').click();
});

// 이미지 파일 선택 이벤트
document.getElementById('imageInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        selectedImage = file; // File 객체 자체를 저장
        showImagePreview(file); // File 객체로 미리보기
    }
});

// 이미지 미리보기 표시 함수 (File 객체 사용)
function showImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('imagePreview');
        if (preview) {
            preview.style.display = 'block'; // 컨테이너 표시
            preview.innerHTML = `
                <img src="${e.target.result}" style="max-width: 200px; max-height: 200px; border-radius: 5px;">
                <br>
                <button type="button" onclick="clearImage()" style="margin-top: 5px; padding: 5px 10px; background: #ff4444; color: white; border: none; border-radius: 3px; cursor: pointer;">삭제</button>
            `;
        }
    };
    reader.readAsDataURL(file);
}

// 이미지 제거 함수 (clearImage로 이름 변경)
function clearImage() {
    selectedImage = null;
    document.getElementById('imageInput').value = '';
    const preview = document.getElementById('imagePreview');
    if (preview) {
        preview.style.display = 'none';
        preview.innerHTML = '';
    }
}

// 음성 녹음 시작
function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToServer(audioBlob);
            };
            
            mediaRecorder.start();
            isRecording = true;
            const vb = document.getElementById('voiceBtn');
            if (vb) {
                vb.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';
            }
        })
        .catch(error => {
            console.error('마이크 접근 오류:', error);
        });
}

// 음성 녹음 중지
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        const vb = document.getElementById('voiceBtn');
        if (vb) {
            vb.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 1.75a3.25 3.25 0 0 0-3.25 3.25v6a3.25 3.25 0 1 0 6.5 0v-6A3.25 3.25 0 0 0 12 1.75z"/><path d="M5 11.5a7 7 0 0 0 14 0"/><path d="M12 18.5v3"/></svg>';
        }
    }
}

// 서버로 음성 데이터 전송
async function sendAudioToServer(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.wav');
        formData.append('session_id', selectedSessionId);
        
        const response = await fetch('/api-chat/transcribe/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.transcribed_text, 'user');
            addMessage(data.bot_response, 'bot');
        }
    } catch (error) {
        console.error('음성 전송 에러:', error);
    }
}

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
  const raw = prompt('카드 제목(비우면 세션 제목 사용)');

  if (raw === null) return;

  const title = raw.trim();

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

function renderSuggestions(afterLi, items = []) {
  // 기존 추천 영역 있으면 제거
  const old = afterLi.querySelector('.suggest-row');
  if (old) old.remove();
  if (!items.length) return;

  const row = document.createElement('div');
  row.className = 'suggest-row';
  // 칩 컨테이너
  row.innerHTML = items.map(q => 
    `<button class="suggest-chip" type="button" data-q="${escapeHtml(q)}">${escapeHtml(q)}</button>`
  ).join('');

  afterLi.appendChild(row);

  // 칩 클릭 -> 입력창 채우고 전송
  row.addEventListener('click', (e) => {
    const btn = e.target.closest('.suggest-chip');
    if (!btn) return;
    chatInput.value = btn.dataset.q || '';
    chatInput.focus();
    sendMessage();
  });
}
