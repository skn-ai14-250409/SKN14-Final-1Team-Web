// uauth/js/signup.js

// ===============================
// 0) 유틸: 안전하게 DOM 준비 후 실행
// ===============================
(function ready(fn) {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
  else fn();
})(function () {

  // ===============================
  // 1) 날짜 max=오늘로 설정
  // ===============================
  (function(){
    const t=new Date();
    const y=t.getFullYear();
    const m=String(t.getMonth()+1).padStart(2,'0');
    const d=String(t.getDate()).padStart(2,'0');
    const bd = document.getElementById('birthDate');
    if (bd) bd.setAttribute('max', `${y}-${m}-${d}`);
  })();

  // ===============================
  // 2) 비밀번호 보기/숨기기 토글 (로그인과 동일한 아이콘 토글)
  // ===============================
  document.querySelectorAll('.toggle').forEach(button => {
    button.addEventListener('click', () => {
      const target = document.getElementById(button.dataset.target);
      if (!target) return;

      const isVisible = target.type === 'text';
      target.type = isVisible ? 'password' : 'text';

      // 아이콘 토글: .eye-on / .eye-off
      const eyeOn  = button.querySelector('.eye-on');
      const eyeOff = button.querySelector('.eye-off');
      if (eyeOn && eyeOff) {
        eyeOn.style.display  = isVisible ? 'block' : 'none';
        eyeOff.style.display = isVisible ? 'none' : 'block';
      }

      // 접근성 상태 업데이트
      button.setAttribute('aria-pressed', (!isVisible).toString());
      const isPw = button.dataset.target === 'password' || button.dataset.target === 'confirmPassword';
      if (isPw) {
        button.setAttribute('aria-label', isVisible ? '비밀번호 표시' : '비밀번호 숨김');
      }

      target.focus();
    });
  });

const fileInput = document.getElementById("profile_image");
const previewImg = document.getElementById("profilePreview");

if (fileInput && previewImg) {
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) {
      previewImg.style.display = "none";
      previewImg.src = "";
      return;
    }
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    previewImg.style.display = "block";
  });
}

  // ===============================
  // 3) 전화번호 자동 하이픈(010만)
  // ===============================
  const phoneInput = document.getElementById('phoneNumber');
  if (phoneInput) {
    phoneInput.addEventListener('input', e => {
      const el = e.target;
      let value = el.value.replace(/[^0-9]/g,'');
      if (value.startsWith('010')) {
        if (value.length > 11) value = value.slice(0,11);
        if (value.length >= 8) {
          value = value.replace(/(\d{3})(\d{4})(\d{1,4})/,'$1-$2-$3');
        } else if (value.length >= 4) {
          value = value.replace(/(\d{3})(\d{1,4})/,'$1-$2');
        }
      }
      el.value = value;
    });
  }

  // ===============================
  // 4) 검증 메시지 사전(한글)
  // ===============================
  const validationMessages = {
    userId: {
      valueMissing: '아이디는 필수 항목입니다',
      patternMismatch: '아이디는 영문, 숫자, 언더바만 사용할 수 있습니다 (4~20자)',
      tooShort: '아이디는 최소 4자 이상이어야 합니다',
      tooLong: '아이디는 최대 20자까지 가능합니다'
    },
    // ※ HTML의 pattern이 "소문자 + 숫자 + 특수문자, 8자 이상"에 맞춰져 있어야 합니다.
    password: {
      valueMissing: '비밀번호를 입력해주세요',
      patternMismatch: '비밀번호는 소문자, 숫자, 특수문자를 포함하고 8자 이상이어야 합니다'
    },
    confirmPassword: {
      valueMissing: '비밀번호를 다시 입력해주세요',
      mismatch: '비밀번호가 일치하지 않습니다'
    },
    email: {
      valueMissing: '이메일을 입력해주세요',
      typeMismatch: '올바른 이메일 주소를 입력해주세요'
    },
    name: {
      valueMissing: '이름을 입력해주세요',
      tooShort: '이름은 최소 2자 이상이어야 합니다',
      tooLong: '이름은 최대 10자까지 가능합니다'
    },
    team: {
      valueMissing: '팀을 선택해주세요'
    },
    role: {
      valueMissing: '직급을 선택해주세요'
    },
    birthDate: {
      valueMissing: '생년월일을 선택해주세요',
      rangeOverflow: '미래 날짜는 선택할 수 없습니다',
      rangeUnderflow: '1900-01-01 이후여야 합니다'
    },
    gender: {
      valueMissing: '성별을 선택해주세요'
    },
    phoneNumber: {
      valueMissing: '전화번호를 입력해주세요',
      patternMismatch: '올바른 휴대폰 번호 형식을 입력해주세요 (예: 010-1234-5678)'
    }
  };
  // 전역 접근이 필요한 경우를 대비
  window.validationMessages = validationMessages;

  // ===============================
  // 5) 에러 박스 접근성 세팅(aria-live)
  // ===============================
  (function attachAriaLive() {
    const ids = [
      'userIdErr','passwordErr','confirmErr','emailErr','nameErr',
      'teamErr','roleErr','birthErr','genderErr','phoneErr'
    ];
    ids.forEach(id => {
      const box = document.getElementById(id);
      if (box && !box.hasAttribute('aria-live')) {
        box.setAttribute('aria-live', 'polite');
      }
    });
  })();

  // ===============================
  // 6) 공통 검증 유틸
  // ===============================
  const form = document.getElementById('registerForm');
  if (!form) return;

  const fields = {
    userId:        document.getElementById('userId'),
    password:      document.getElementById('password'),
    confirmPassword: document.getElementById('confirmPassword'),
    email:         document.getElementById('email'),
    name:          document.getElementById('name'),
    team:          document.getElementById('team'),
    role:          document.getElementById('role'),
    birthDate:     document.getElementById('birthDate'),
    gender:        document.getElementById('gender'),
    phoneNumber:   document.getElementById('phoneNumber')
  };

  // cto -> 팀선택x
  (function setupRoleTeamDependency(){
    const roleEl = fields.role;
    const teamEl = fields.team;
    if (!roleEl || !teamEl) return;

    function applyRoleGuard() {
      const v = (roleEl.value || '').toLowerCase();
      if (v === 'cto') {
        teamEl.value = '';
        teamEl.setAttribute('disabled', '');
        teamEl.removeAttribute('required');
        teamEl.setAttribute('aria-disabled', 'true');
        setError('team', ''); 
      } else {
        teamEl.removeAttribute('disabled');
        teamEl.setAttribute('required', '');
        teamEl.removeAttribute('aria-disabled');
      }
    }

    roleEl.addEventListener('change', applyRoleGuard);
    roleEl.addEventListener('input', applyRoleGuard); 
    applyRoleGuard(); 
  })();

  function errBoxFor(name) {
    return document.getElementById(name + 'Err');
  }

  // (6) 공통 유틸 위나 아래 적당한 곳에 추가
const ERROR_ID_MAP = {
  confirmPassword: 'confirmErr',
  birthDate: 'birthErr',
  phoneNumber: 'phoneErr',
};

function errBoxFor(name) {
  return document.getElementById(ERROR_ID_MAP[name] || (name + 'Err'));
}


  function setError(name, message) {
    const box = errBoxFor(name);
    const input = fields[name];
    if (box) box.textContent = message || '';
    if (input) input.setAttribute('aria-invalid', message ? 'true' : 'false');
  }

  // 개별 필드 기본(validity) 검사
  function validateByValidity(name) {
    const input = fields[name];
    const msgs  = validationMessages[name];
    if (!input || !msgs) return true;

    // select 요소도 validity를 지원
    const v = input.validity;

    setError(name, ''); // 초기화

    if (v.valueMissing && msgs.valueMissing) {
      setError(name, msgs.valueMissing);
      return false;
    }
    if (v.patternMismatch && msgs.patternMismatch) {
      setError(name, msgs.patternMismatch);
      return false;
    }
    if (v.tooShort && msgs.tooShort) {
      setError(name, msgs.tooShort);
      return false;
    }
    if (v.tooLong && msgs.tooLong) {
      setError(name, msgs.tooLong);
      return false;
    }
    if (v.typeMismatch && msgs.typeMismatch) {
      setError(name, msgs.typeMismatch);
      return false;
    }
    if (v.rangeOverflow && msgs.rangeOverflow) {
      setError(name, msgs.rangeOverflow);
      return false;
    }
    if (v.rangeUnderflow && msgs.rangeUnderflow) {
      setError(name, msgs.rangeUnderflow);
      return false;
    }
    return true;
  }

  // 교차 검증: 비밀번호 확인
  function validateConfirmPassword() {
    const pw  = fields.password;
    const cpw = fields.confirmPassword;
    if (!pw || !cpw) return true;

    // 값이 없으면 기본 valueMissing 로직에 맡김
    if (!cpw.value) {
      setError('confirmPassword', '');
      return true;
    }
    if (pw.value !== cpw.value) {
      const msg = validationMessages.confirmPassword.mismatch || '비밀번호가 일치하지 않습니다';
      setError('confirmPassword', msg);
      return false;
    }
    setError('confirmPassword', '');
    return true;
  }

  // 전화번호 추가 규칙(010-1234-5678) — patternMismatch가 잡아주지만, 커스텀 로직 예시
  function validatePhoneNumber() {
    const input = fields.phoneNumber;
    if (!input) return true;
    const value = input.value.trim();
    setError('phoneNumber', '');

    // 값이 비었거나 기본 validity가 처리 가능한 경우는 기본 로직에 맡김
    if (!value) return validateByValidity('phoneNumber');

    const ok = /^010-\d{4}-\d{4}$/.test(value);
    if (!ok) {
      setError('phoneNumber', validationMessages.phoneNumber.patternMismatch);
      return false;
    }
    return true;
  }

  // 한 필드 통합 검사
  function validateField(name) {
    // 순서 중요: 기본 validity → 추가/교차 규칙
    if (!validateByValidity(name)) return false;
    if (name === 'confirmPassword') return validateConfirmPassword();
    if (name === 'phoneNumber')     return validatePhoneNumber();
    return true;
  }

  // 전체 검사
  function validateAll() {
    let ok = true;
    Object.keys(fields).forEach(name => {
      const pass = validateField(name);
      if (!pass) ok = false;
    });
    return ok;
  }

  // ===============================
  // 7) 실시간/포커스 아웃 시 검증
  // ===============================
  Object.keys(fields).forEach(name => {
    const input = fields[name];
    if (!input) return;

    const handler = () => validateField(name);

    // 입력 중/포커스 아웃 시
    input.addEventListener('input', handler);
    input.addEventListener('blur', handler);
    // select는 change
    if (input.tagName === 'SELECT') {
      input.addEventListener('change', handler);
    }
  });

  // 비밀번호와 비밀번호 확인은 상호 영향 → 즉시 업데이트
  if (fields.password && fields.confirmPassword) {
    fields.password.addEventListener('input', validateConfirmPassword);
    fields.confirmPassword.addEventListener('input', validateConfirmPassword);
  }

  // ===============================
  // 8) 제출 제어
  //    - novalidate 상태에서 우리가 직접 검사
  //    - 에러가 있으면 제출 막음
  //    - 통과 시에만 실제 제출
  // ===============================
  form.addEventListener('submit', function (e) {
    const pass = validateAll();
    if (!pass) {
      e.preventDefault();
      // 첫 에러 필드로 포커스 이동
      for (const name of Object.keys(fields)) {
        const input = fields[name];
        const box = errBoxFor(name);
        if (box && box.textContent) {
          input && input.focus();
          break;
        }
      }
      return;
    }
    // 통과 시: 기본 동작(실제 제출) 그대로 진행
    // e.preventDefault(); // ❌ 금지: 무조건 막지 마세요.
    // form.submit();      // ❌ 강제 제출 불필요. 기본 제출로 충분.
  }, true); // 캡처 단계에서 먼저 검사

});
