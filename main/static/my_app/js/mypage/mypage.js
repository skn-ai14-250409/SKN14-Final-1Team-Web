function openCardDetail(cardUrl) {
  window.open(cardUrl, 'CardDetail', 'width=500,height=300');
}

async function copyToClipboard(textToCopy) {
  try {
    await navigator.clipboard.writeText(textToCopy);
    alert('키가 복사되었습니다!');
  } catch (err) {
    console.error('클립보드 복사 실패:', err);
    alert('클립보드 복사에 실패했습니다.');
  }
}

// 키 복사 수정 : navigator.clipboard -> document.execCommand('copy')
// -> 배포환경에서 복붙되는지 확인 필
// async function copyToClipboard(textToCopy) {
//   try {
//     const tempInput = document.createElement('textarea');
//     tempInput.value = textToCopy;
//     tempInput.style.position = 'fixed';
//     tempInput.style.top = '-9999px';
//     document.body.appendChild(tempInput);
//     tempInput.focus();
//     tempInput.select();
//     document.execCommand('copy');
//     document.body.removeChild(tempInput);
//     alert('키가 복사되었습니다!');
//   } catch (err) {
//     console.error('클립보드 복사 실패:', err);
//     alert('클립보드 복사에 실패했습니다.');
//   }
// }

function toggleEditMode() {
  const editBtn = document.getElementById('edit-btn');
  const saveBtn = document.getElementById('save-btn');
  const genderText = document.getElementById('gender-text');
  const genderSelect = document.getElementById('gender-select');

  const editableInputs = document.querySelectorAll(
    '#profile-form input:not(#id):not(#rank):not(#department)'
  );
  const editableSelects = document.querySelectorAll('#profile-form select');

  const accountSection = document.querySelector('.account-section');
  const isEditMode = editBtn.style.display !== 'none';

  if (isEditMode) {
    editBtn.style.display = 'none';
    saveBtn.style.display = 'block';

    editableInputs.forEach(input => {
      input.removeAttribute('readonly');
    });

    editableSelects.forEach(select => {
      select.removeAttribute('disabled');
    });
    
    genderText.style.display = 'none';
    genderSelect.style.display = 'inline';

    accountSection.classList.add('editing');
  } else {
    editBtn.style.display = 'block';
    saveBtn.style.display = 'none';

    editableInputs.forEach(i => i.setAttribute('readonly', true));
    editableSelects.forEach(s => s.setAttribute('disabled', true));

    genderText.style.display = 'inline';
    genderSelect.style.display = 'none';

    accountSection.classList.remove('editing');

  
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const inputField = document.getElementById('api_key_name');
  const keyNameMessage = document.getElementById('api_key_message');
  const createKeyButton = document.getElementById('create_key_button');

  updateButtonState();

  inputField.addEventListener('keyup', function () {
    const keyName = inputField.value;

    if (keyName.trim() === '') {
      keyNameMessage.textContent = '';
      updateButtonState(false);
      return;
    }

    fetch('/mypage/check_api_key_name/?name=' + encodeURIComponent(keyName))
      .then(response => response.json())
      .then(data => {
        if (data.is_taken) {
          keyNameMessage.textContent = '동일한 이름의 API키가 존재합니다.';
          keyNameMessage.style.color = 'red';
          updateButtonState(false);
        } else {
          keyNameMessage.textContent = '등록 가능한 API키입니다.';
          keyNameMessage.style.color = 'green';
          updateButtonState(true);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        updateButtonState(false);
      });
  });

  function updateButtonState(isValid = false) {
    if (inputField.value.trim() === '' || !isValid) {
      createKeyButton.disabled = true;
    } else {
      createKeyButton.disabled = false;
    }
  }

  // 전화번호 자동 하이픈
  const phoneInput = document.getElementById('phone');
  const phoneErr = document.getElementById('phoneErr');
  if (phoneInput) {
    phoneInput.addEventListener('input', e => {
      let v = e.target.value.replace(/[^0-9]/g, '');
      if (v.startsWith('010')) {
        if (v.length > 11) v = v.slice(0, 11);
        if (v.length >= 8) {
          v = v.replace(/(\d{3})(\d{4})(\d{1,4})/, '$1-$2-$3');
        } else if (v.length >= 4) {
          v = v.replace(/(\d{3})(\d{1,4})/, '$1-$2');
        }
      }
      e.target.value = v;
      if (phoneErr) {
        if (!v || /^010-\d{4}-\d{4}$/.test(v)) phoneErr.textContent = '';
        else phoneErr.textContent = '올바른 형식으로 입력해주세요 (예: 010-1234-5678)';
      }
    });
  }
});

// API 키 삭제: 폼 submit을 가로채서 AJAX로 처리 (삭제 후 alert 띄우고 li 제거)
document.addEventListener('submit', async function (e) {
  const form = e.target; // 실제 제출된 폼

  if (!form.matches('form[action*="api_key_delete"]')) return;

  e.preventDefault(); // 기본 제출 막기

  if (!confirm('이 API 키를 삭제할까요?')) return;

  try {
    const res = await fetch(form.action, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      body: new FormData(form),
      credentials: 'same-origin',
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    // 성공: 해당 API 키 <li> 제거 + 알림
    const li = form.closest('li');
    alert('삭제 완료!');
    window.location.replace(REFRESH_URL);
  } catch (err) {
    console.error(err);
    alert('삭제 중 오류가 발생했습니다.');
  }
});


// ---- CSRF helper ----
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}
const CSRF = getCookie('csrftoken');

// 리다이렉트 대상 URL (템플릿에서 주입, 없으면 현재 경로)
const REFRESH_URL =
  (document.getElementById('mypageCtx')?.dataset.refreshUrl) ||
  window.location.pathname;

// 카드 삭제
async function deleteCard(cardId) {
  if (!confirm('이 카드를 삭제할까요?')) return;
  try {
    const res = await fetch(`/api-chat/cards/${cardId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      credentials: 'same-origin'
    });

    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`HTTP ${res.status}: ${txt.slice(0, 200)}`);
    }

    // 바로 리다이렉트 (서버 렌더링으로 empty 상태 표시 보장)
    alert('삭제 완료!');
    window.location.replace(REFRESH_URL);
  } catch (err) {
    console.error(err);
    alert('삭제 중 오류가 발생했습니다..');
  }
}

/* 미리보기: 즉시/지연 모두 커버 */
(function bindProfilePreview() {
  function attach() {
    const fileInput = document.getElementById('profile_image');
    const previewImg = document.querySelector('.profile-image');
    if (!fileInput || !previewImg) return;

    fileInput.addEventListener('change', function (e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      // Object URL 방식이 FileReader보다 간단하고 안정적
      const url = URL.createObjectURL(file);
      previewImg.src = url;
      previewImg.onload = () => URL.revokeObjectURL(url);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attach, { once: true });
  } else {
    attach();
  }
})();
