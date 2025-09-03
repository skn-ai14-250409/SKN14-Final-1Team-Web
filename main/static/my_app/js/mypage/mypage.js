function openCardDetail(cardUrl) { // card 팝업창
    // const url = `mypage/card_detail/${cardId}/`; 
    window.open(cardUrl, 'CardDetail', 'width=500,height=300');
}

async function copyToClipboard(textToCopy) {
    try {
        await navigator.clipboard.writeText(textToCopy); // 비동기적으로 복사
        alert('키가 복사되었습니다!');
    } catch (err) {
        console.error('클립보드 복사 실패:', err);
        alert('클립보드 복사에 실패했습니다.');
    }
}

// 정보 수정
function toggleEditMode() {
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');
    const editableInputs = document.querySelectorAll('#profile-form input:not(#id)');

    // 현재 상태가 '편집' 모드인지 확인
    const isEditMode = editBtn.style.display !== 'none';

    if (isEditMode) {
        editBtn.style.display = 'none';
        saveBtn.style.display = 'block';
        editableInputs.forEach(input => {
            input.removeAttribute('readonly');
        });
    } else {
        editBtn.style.display = 'block';
        saveBtn.style.display = 'none';
        editableInputs.forEach(input => {
            input.setAttribute('readonly', true);
        });
    }
}

// 이미 있는 apikey 체크
document.addEventListener('DOMContentLoaded', function() {
    const inputField = document.getElementById('api_key_name');
    const keyNameMessage = document.getElementById('api_key_message');
    const createKeyButton = document.getElementById('create_key_button'); 
    
    updateButtonState();

    inputField.addEventListener('keyup', function() {
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

    // apikey 버튼
    function updateButtonState(isValid = false) {
        if (inputField.value.trim() === '' || !isValid) {
            createKeyButton.disabled = true;
        } else {
            createKeyButton.disabled = false;
        }
    }
});