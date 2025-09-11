document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.getElementById('passwordToggle');
    const eyeIcon = document.getElementById('eyeIcon');
    const eyeOffIcon = document.getElementById('eyeOffIcon');
    const loginButton = document.getElementById('loginButton');

    // 비밀번호 표시/숨김
    passwordToggle.addEventListener('click', function() {
        const isVisible = passwordInput.type === 'text';
        passwordInput.type = isVisible ? 'password' : 'text';
        eyeIcon.style.display = isVisible ? 'block' : 'none';
        eyeOffIcon.style.display = isVisible ? 'none' : 'block';
        passwordToggle.setAttribute('aria-pressed', !isVisible);
        passwordToggle.setAttribute('aria-label', isVisible ? '비밀번호 표시' : '비밀번호 숨김');
        passwordInput.focus();
    });

    // 에러 처리
    function showError(input, message) {
        const el = document.getElementById(input.id + 'Error');
        if (el) {
            el.textContent = message;
            el.classList.add('show');
            input.classList.add('error');
        }
    }
    function hideError(input) {
        const el = document.getElementById(input.id + 'Error');
        if (el) {
            el.classList.remove('show');
            input.classList.remove('error');
        }
    }

    // 유효성 검사
    function validateInput(input) {
        const value = input.value.trim();
        if (input.id === 'username') {
            if (!value) return showError(input, '아이디를 입력해주세요.'), false;
            if (value.length < 3) return showError(input, '아이디는 3자 이상이어야 합니다.'), false;
            hideError(input); return true;
        }
        if (input.id === 'password') {
            if (!value) return showError(input, '비밀번호를 입력해주세요.'), false;
            if (value.length < 4) return showError(input, '비밀번호는 4자 이상이어야 합니다.'), false;
            hideError(input); return true;
        }
        return true;
    }

    [usernameInput, passwordInput].forEach(input => {
        input.addEventListener('blur', () => validateInput(input));
        input.addEventListener('input', () => { if (input.classList.contains('error')) hideError(input); });
        input.addEventListener('focus', () => input.parentElement.classList.add('focused'));
        input.addEventListener('blur', () => { if (!input.value) input.parentElement.classList.remove('focused'); });
        if (input.value) input.parentElement.classList.add('focused');
    });

    // 로딩 상태
    function setLoadingState(isLoading) {
        loginButton.classList.toggle('loading', isLoading);
        loginButton.disabled = isLoading;
    }

    // 폼 제출
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const okU = validateInput(usernameInput);
        const okP = validateInput(passwordInput);
        if (!okU || !okP) {
            (loginForm.querySelector('.error') || usernameInput).focus();
            return;
        }
        setLoadingState(true);
        const formData = new FormData(loginForm);
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
            credentials: 'same-origin'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                
                setTimeout(() => window.location.href = data.redirect_url || '/dashboard/', 1000);
            } else {
                if (data.field_errors) {
                    Object.keys(data.field_errors).forEach(field => {
                        const input = document.getElementById(field);
                        if (input) showError(input, data.field_errors[field][0]);
                    });
                } else {
                    showError(passwordInput, data.message || '로그인에 실패했습니다.');
                }
                setLoadingState(false);
            }
        })
        .catch(() => {
            showError(passwordInput, '네트워크 오류가 발생했습니다. 다시 시도해주세요.');
            setLoadingState(false);
        });
    });

    function showSuccessMessage(msg) {
        const existing = document.querySelector('.success-message');
        if (existing) existing.remove();
        const div = document.createElement('div');
        div.className = 'success-message alert alert-success';
        div.textContent = msg;
        loginForm.insertBefore(div, loginForm.firstChild);
    }

    // Enter 키 처리 (중복 제출 방지)
    usernameInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); passwordInput.focus(); }
    });
    passwordInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); loginForm.requestSubmit(); }
    });

    // ESC로 에러 제거
    loginForm.addEventListener('keydown', e => {
        if (e.key === 'Escape') loginForm.querySelectorAll('.error').forEach(i => hideError(i));
    });

    // 초기 포커스
    if (!usernameInput.value) usernameInput.focus();

    // 뒤로가기 시 로딩 상태 해제
    window.addEventListener('pageshow', e => { if (e.persisted) setLoadingState(false); });
});
