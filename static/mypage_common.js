
// 전역 콘텐츠 영역
const content = document.getElementById('content-area');
const menuItems = document.querySelectorAll('.sidebar li');

// 공통 페이지 객체 (파트별 JS에서 여기에 추가할 예정)
const pages = {};

// 메뉴 클릭 시 오른쪽 화면 전환
menuItems.forEach(item => {
  item.addEventListener('click', () => {
    if (item.classList.contains('disabled')) return;

    menuItems.forEach(li => li.classList.remove('active'));
    item.classList.add('active');

    const section = item.getAttribute('data-section');
    content.innerHTML = pages[section] || '<p>아직 준비 중입니다.</p>';

    // 섹션별 초기화 함수 실행
    if (window.initFunctions && window.initFunctions[section]) {
      window.initFunctions[section]();
    }
  });
});

// URL 파라미터로 바로 열기 (예: ?section=wishlist) 근데 별 아이콘 누르면 관심목록으로 안 넘어가는 이슈 있음...
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const section = params.get('section') || 'profile';

  content.innerHTML = pages[section] || '<p>아직 준비 중입니다.</p>';
  document.querySelectorAll('.sidebar li').forEach(li => li.classList.remove('active'));
  const active = document.querySelector(`.sidebar li[data-section="${section}"]`);
  if (active) active.classList.add('active');

  if (window.initFunctions && window.initFunctions[section]) {
    window.initFunctions[section]();
  }
});

// 로그인 버튼 이동
document.getElementById('authBtn').addEventListener('click', () => {
  window.location.href = '../templates/login.html';
});
