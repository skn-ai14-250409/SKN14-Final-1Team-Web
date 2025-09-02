// 날짜 max=오늘로 설정
(function(){
  const t=new Date();
  const y=t.getFullYear();
  const m=String(t.getMonth()+1).padStart(2,'0');
  const d=String(t.getDate()).padStart(2,'0');
  const bd = document.getElementById('birthDate');
  if (bd) bd.setAttribute('max', `${y}-${m}-${d}`);
})();

// 비밀번호 보기/숨기기 토글
document.querySelectorAll('.toggle').forEach(button => {
  button.addEventListener('click', () => {
    const target = document.getElementById(button.dataset.target);
    if (!target) return;
    target.type = target.type === 'password' ? 'text' : 'password';
  });
});

// 전화번호 자동 하이픈 추가
const phoneInput = document.getElementById('phoneNumber');
if (phoneInput) {
  phoneInput.addEventListener('input', e => {
    let value = e.target.value.replace(/[^0-9]/g,'');
    if (value.startsWith('010')) {
      if (value.length > 11) value = value.slice(0,11);
      if (value.length >= 8) {
        value = value.replace(/(\d{3})(\d{4})(\d{1,4})/,'$1-$2-$3');
      } else if (value.length >= 4) {
        value = value.replace(/(\d{3})(\d{1,4})/,'$1-$2');
      }
    }
    e.target.value = value;
  });
}

// 검증 메시지
const validationMessages = {
  userId: {
    valueMissing: '아이디는 필수 항목입니다',
    patternMismatch: '아이디는 영문, 숫자, 언더바만 사용할 수 있습니다 (4~20자)',
    tooShort: '아이디는 최소 4자 이상이어야 합니다',
    tooLong: '아이디는 최대 20자까지 가능합니다'
  },
  password: {
    valueMissing: '비밀번호를 입력해주세요',
    patternMismatch: '비밀번호는 대소문자, 숫자, 특수문자를 포함하고 8자 이상이어야 합니다'
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

// 폼 제출 → 검증 통과 시 실제 제출(서버로 POST)
document.getElementById('registerForm').addEventListener('submit', e => {
  e.preventDefault();

  let isFormValid = true;
  document.querySelectorAll('#registerForm input, #registerForm select').forEach(el => {
    if (!validateField(el)) isFormValid = false;
  });
  if (!isFormValid) return;

  // AJAX가 아니라 실제 제출
  e.currentTarget.submit();
});

// (참고) showToast는 AJAX 방식에서만 사용하세요. 기본 제출은 곧 페이지 이동됨.
