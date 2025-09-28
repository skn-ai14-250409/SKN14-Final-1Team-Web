console.log("internal-docs 페이지 JavaScript 시작!");

let selectedSessionId = null; // 현재 선택된 세션 id

// 요소 선택
const sessionList = document.getElementById("sessionList");
const sessionTitle = document.getElementById("sessionTitle");
const chatLog = document.getElementById("chatLog");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const newsessionBtn = document.querySelector(".btn-new-chat");

if (newsessionBtn) {
  newsessionBtn.addEventListener("click", session_create);
} else {
  console.warn(".btn-new-chat 를 찾지 못했습니다.");
}

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
      await loadSessionTone(selectedSessionId);
      return; 
    }
  }
  //=====================
  if (!sessionList) {
    console.warn("#sessionList 가 없어 초기 선택을 건너뜀");
    return;
  }
  const firstSession = sessionList.querySelector(".session-link");
  if (firstSession) {
    selectedSessionId = firstSession.dataset.sessionId;
    sessionTitle.textContent = firstSession.textContent.trim();
    firstSession.parentElement.classList.add("is-active");
    await loadChatHistory(selectedSessionId);
    await loadSessionTone(selectedSessionId);
  }
}

// 세션 클릭 이벤트
sessionList.addEventListener("click", async (e) => {
  // 삭제 버튼 클릭 처리
  if (e.target.classList.contains("delete-btn")) {
    const sessionId = e.target.dataset.sessionId;
    if (confirm("이 세션을 삭제하시겠습니까?")) {
      await deleteSession(sessionId);
    }
    return;
  }

  // 세션 선택 처리
  const btn = e.target.closest(".session-link");
  if (!btn) return;

  selectedSessionId = btn.dataset.sessionId;
  console.log("선택된 세션 ID:", selectedSessionId);
  sessionTitle.textContent = btn.textContent.trim();

  // 선택 표시 업데이트
  document
    .querySelectorAll("#sessionList .is-active")
    .forEach((el) => el.classList.remove("is-active"));
  btn.parentElement.classList.add("is-active");

  // 채팅 히스토리 로드
  await loadChatHistory(selectedSessionId);

  // 세션의 말투 정보 가져오기
  await loadSessionTone(selectedSessionId);

  // 추가: URL 변경======
  const newUrl = new URL(window.location.href);
  newUrl.searchParams.set('session_id', selectedSessionId);
  window.history.pushState({ sessionId: selectedSessionId }, '', newUrl.href);
  //=====================
});

// 세션 삭제 함수
async function deleteSession(sessionId) {
  try {
    const response = await fetch(
      `/internal-chat/delete_session/${sessionId}/`,
      {
        method: "DELETE",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
        credentials: "same-origin",
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // 삭제된 세션을 리스트에서 제거
    const sessionItem = document.querySelector(
      `[data-session-id="${sessionId}"]`
    ).parentElement;
    sessionItem.remove();

    // 현재 선택된 세션이 삭제된 경우 채팅 내역 비우기
    if (selectedSessionId === sessionId) {
      selectedSessionId = null;
      sessionTitle.textContent = "세션을 선택하세요";
      chatLog.innerHTML = "";
    }

    console.log(`세션 ${sessionId} 삭제 완료`);
  } catch (err) {
    console.error("세션 삭제 실패:", err);
    alert("세션 삭제에 실패했습니다.");
  }
}

// 채팅 히스토리 로드 함수
async function loadChatHistory(sessionId) {
  try {
    const response = await fetch(`/internal-chat/chat_history/${sessionId}/`, {
      credentials: "same-origin",
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    // 채팅창 초기화
    chatLog.innerHTML = "";

    // 메시지 히스토리 표시
    data.messages.forEach((msg) => {
      addMessage(
        msg.content,
        msg.role === "user" ? "user" : "assistant",
        msg.id
      ); // id 전달
    });

    console.log(
      `세션 ${sessionId} 히스토리 로드 완료:`,
      data.messages.length,
      "개 메시지"
    );
  } catch (err) {
    console.error("채팅 히스토리 로드 실패:", err);
    chatLog.innerHTML =
      '<li class="error">채팅 히스토리를 불러올 수 없습니다.</li>';
  }
}

// 초기 실행 (새로고침 시, 가장 첫번째 채팅세션을 선택하도록)
initializeFirstSession();

// 모달 관련 변수
let selectedTone = null;

// 모달 이벤트 리스너 추가
document.addEventListener('DOMContentLoaded', function() {
  const toneModal = document.getElementById('toneModal');
  const selectFormal = document.getElementById('selectFormal');
  const selectInformal = document.getElementById('selectInformal');
  const closeModal = document.getElementById('closeModal');
  

  // 공손 말투 선택
  if (selectFormal) {
    selectFormal.addEventListener('click', function() {
      selectedTone = 'formal';
      updateCurrentTone('formal');
      hideToneModal();
      createSessionWithTone('formal');
    });
  }

  // 친구 말투 선택
  if (selectInformal) {
    selectInformal.addEventListener('click', function() {
      selectedTone = 'informal';
      updateCurrentTone('informal');
      hideToneModal();
      createSessionWithTone('informal');
    });
  }

  // 모달 닫기
  if (closeModal) {
    closeModal.addEventListener('click', hideToneModal);
  }

  // 모달 외부 클릭 시 닫기
  if (toneModal) {
    toneModal.addEventListener('click', function(e) {
      if (e.target === toneModal) {
        hideToneModal();
      }
    });
  }
});

// 모달 표시
function showToneModal() {
  const toneModal = document.getElementById('toneModal');
  if (toneModal) {
    toneModal.style.display = 'flex';
  }
}

// 모달 숨기기
function hideToneModal() {
  const toneModal = document.getElementById('toneModal');
  if (toneModal) {
    toneModal.style.display = 'none';
  }
}

// 현재 말투 표시 업데이트
function updateCurrentTone(tone) {
  const currentTone = document.getElementById('toneSelectBtn');
  if (currentTone) {
    if (tone === 'formal') {
      currentTone.textContent = '말투: 공손 말투';
      currentTone.style.color = '#28a745';
    } else if (tone === 'informal') {
      currentTone.textContent = '말투: 친구 말투';
      currentTone.style.color = '#ffc107';
    } else {
      currentTone.textContent = '말투: 선택되지 않음';
      currentTone.style.color = '#666';
    }
  }
}

// 세션의 말투 정보 가져오기
async function loadSessionTone(sessionId) {
  try {
    const response = await fetch(`/internal-chat/session_info/${sessionId}/`, {
      method: 'GET',
      headers: {
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'same-origin',
    });

    if (response.ok) {
      const data = await response.json();
      updateCurrentTone(data.text_mode);
    } else {
      console.warn('세션 말투 정보를 가져올 수 없습니다.');
      updateCurrentTone(null);
    }
  } catch (err) {
    console.error('세션 말투 정보 로드 실패:', err);
    updateCurrentTone(null);
  }
}

// 새 채팅 버튼 클릭 시 모달 표시
async function session_create() {
  showToneModal();
}

// 선택한 말투로 세션 생성
async function createSessionWithTone(tone) {
  try {
    const csrfToken = getCSRFToken();

    const response = await fetch("/internal-chat/session_create/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "same-origin",
      body: JSON.stringify({ 
        title: "title",
        text_mode: tone 
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("HTTP", response.status, text);
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log("성공", data);

    // 새 세션 리스트에 추가
    const li = document.createElement("li");
    li.className = "session-item";
    li.innerHTML = `
      <button class="session-link" data-session-id="${data.session.id}">${data.session.title}</button>
      <button class="delete-btn" data-session-id="${data.session.id}">×</button>
    `;
    // sessionList가 있을 때만 prepend 호출
    if (sessionList) {
      sessionList.prepend(li);
    } else {
      console.warn("#sessionList 없음: 새 세션 UI 추가를 건너뜀");
    }

    // 새 세션 자동 선택
    selectedSessionId = data.session.id;
    sessionTitle.textContent = data.session.title;

    // 선택 표시 업데이트
    document
      .querySelectorAll("#sessionList .is-active")
      .forEach((el) => el.classList.remove("is-active"));
    li.classList.add("is-active");

    // 채팅창 초기화 (새 세션이므로 빈 상태)
    chatLog.innerHTML = "";

    // 현재 말투 표시 업데이트
    updateCurrentTone(tone);

    console.log("새 세션 생성 및 선택 완료:", selectedSessionId, "말투:", tone);
  } catch (err) {
    console.error("요청 실패:", err);
  }
}

function escapeHtml(str) {
  if (str == null) return "";
  return String(str).replace(
    /[&<>"']/g,
    (m) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[
        m
      ])
  );
}

// 메시지를 채팅창에 추가하는 함수
function addMessage(text, role = "user", id = null) {
  const li = document.createElement("li");
  li.className = `msg msg--${role}`;
  if (id != null) li.dataset.mid = id;

  li.innerHTML = `<div class="bubble">${marked.parse(text)}</div>`;

  chatLog.appendChild(li);
  chatLog.scrollTop = chatLog.scrollHeight;
}

// 기존 말투 선택 버튼 코드는 제거됨 (모달 방식으로 변경)

// 메시지 전송 공통 함수
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return; // 빈 입력은 무시

  // 현재 선택된 세션 확인
  if (!selectedSessionId) {
    alert("세션을 선택해주세요.");
    return;
  }

  // 입력 메시지를 채팅창에 추가
  addMessage(message, "user");

  // 입력창 비우기
  chatInput.value = "";

  // 서버 전송 (추후 API 연동 가능)
  console.log("사용자 질문 전송:", message, "세션 ID:", selectedSessionId);

  // 임시 봇 응답 + 서버 호출
  try {
    const csrfToken = getCSRFToken();

    const response = await fetch("/internal-chat/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken, // Django 표준 헤더명
      },
      credentials: "same-origin", // 쿠키 포함 (csrftoken 사용 시 필요)
      body: JSON.stringify({
        message: message,
        session_id: selectedSessionId,
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
      addMessage(
        data.bot_message ?? `봇 응답 예시: "${message}"에 대한 답변입니다.`,
        "bot"
      );

      // 챗팅 타이틀 갱신
      if (data.title) {
        if (sessionTitle) sessionTitle.textContent = data.title;
        const btn = document.querySelector(
          `#sessionList .session-link[data-session-id="${selectedSessionId}"]`
        );
        if (btn) btn.textContent = data.title;
      }
    }
  } catch (err) {
    console.error("요청 실패:", err);
    addMessage("서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.", "bot");
  } finally {
    // 필요 시 로딩 인디케이터 끄기 등 후처리
  }
}

// 보내기 버튼 클릭 이벤트
sendBtn.addEventListener("click", sendMessage);

// 엔터 키 이벤트 (Shift+Enter는 줄바꿈 유지)
chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault(); // 줄바꿈 방지
    sendMessage();
  }
});

// csrf 토큰 찾기
function getCSRFToken() {
  // 1) form input
  let token = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
  if (token) return token;

  // 2) meta 태그
  token = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");
  if (token) return token;

  // 3) 쿠키
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === "csrftoken") return value;
  }

  console.warn("CSRF 토큰을 찾을 수 없습니다.");
  return "";
}

// CSRF
function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return m ? m.pop() : "";
}
const CSRF = getCookie("csrftoken");

// ====== 카드 선택/저장 기능 ======
(function initCardSelectSave() {
  const $btnSelect = document.getElementById('btnCardSelect');
  const $btnSave   = document.getElementById('btnCardSave');
  const $selCount  = document.getElementById('selCount');

  const $chatLog = chatLog;

  if ($btnSave) $btnSave.disabled = true;
  if (!$btnSelect || !$btnSave || !$selCount || !$chatLog) {
    console.warn('카드 선택/저장 UI 요소를 찾지 못해 기능을 건너뜁니다.');
    return;
  }

  let selecting   = false;
  let selectedIds = [];

  function updateSelectUI() {
    [...$chatLog.querySelectorAll('li.msg')].forEach(li => {
      const mid = li.dataset.mid;
      const chosen = selectedIds.includes(mid);

      if (selecting) {
        li.classList.add('msg--selecting');
        li.classList.toggle('msg--chosen', chosen);

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
        li.classList.remove('msg--selecting', 'msg--chosen');
        const mark = li.querySelector('.select-mark');
        if (mark) mark.remove();
      }
    });

    $btnSave.disabled = !selecting || selectedIds.length === 0;
    $selCount.style.display = selecting ? 'inline' : 'none';
    $selCount.textContent = `${selectedIds.length}개 선택`;
    $btnSelect.textContent = selecting ? '선택 취소' : '카드만들기';
  }

  $btnSelect.addEventListener('click', () => {
    selecting = !selecting;
    if (!selecting) selectedIds = [];
    updateSelectUI();
  });

  $chatLog.addEventListener('click', (e) => {
    if (!selecting) return;
    const li = e.target.closest('li.msg');
    if (!li) return;
    const mid = li.dataset.mid;
    if (!mid) return;

    const idx = selectedIds.indexOf(mid);
    if (idx === -1) selectedIds.push(mid);
    else selectedIds.splice(idx, 1);

    updateSelectUI();
  });

  // 카드 저장
  $btnSave.addEventListener('click', async () => {
    if (!selecting) return;
    if (!selectedSessionId) { alert('세션 ID가 없습니다.'); return; }
    if (selectedIds.length === 0) { alert('선택된 메시지가 없습니다.'); return; }

    const raw = prompt('카드 제목(비우면 세션 제목 사용)');
    if (raw === null) return;
    const title = raw.trim();

    try {
      const res = await fetch('/api-chat/cards/save/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          session_id: Number(selectedSessionId),
          title,
          message_ids: selectedIds.map(Number)
        })
      });

      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data.error || '저장 실패');
      alert('카드 저장 완료!');
    } catch (err) {
      console.error(err);
      alert(`저장 중 오류: ${err.message}`);
    } finally {
      // 저장 후 선택모드 해제
      selecting = false;
      selectedIds = [];
      updateSelectUI();
    }
  });

  updateSelectUI();
})();
