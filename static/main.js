
(function () {
  const toggleBtn =
    document.querySelector('.navbar__toogleBtn') ||
    document.querySelector('.navbar__toggleBtn');

  const menu = document.querySelector('.navbar__menu');

  if (!toggleBtn || !menu) return;

  toggleBtn.setAttribute('role', 'button');
  toggleBtn.setAttribute('aria-controls', 'nav-menu');
  toggleBtn.setAttribute('aria-expanded', 'false');
  toggleBtn.setAttribute('aria-label', 'Toggle navigation menu'); // 폰트어썸 없을 때도 의미 전달

  // Give the menu an id if absent
  if (!menu.id) menu.id = 'nav-menu';

  const closeMenu = () => {
    menu.classList.remove('is-open');
    toggleBtn.setAttribute('aria-expanded', 'false');
  };

  const openMenu = () => {
    menu.classList.add('is-open');
    toggleBtn.setAttribute('aria-expanded', 'true');
  };

  const toggleMenu = () => {
    if (menu.classList.contains('is-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  };

  // Click to toggle
  toggleBtn.addEventListener('click', (e) => {
    e.preventDefault();
    toggleMenu();
  });

  // Keyboard: Enter/Space on the toggle button
  toggleBtn.addEventListener('keydown', (e) => {
    const key = e.key || e.code;
    if (key === 'Enter' || key === ' ' || key === 'Spacebar') {
      e.preventDefault();
      toggleMenu();
    }
  });

  // Close on Esc
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMenu();
  });

  // Close menu when a nav link is clicked (모바일 UX)
  menu.addEventListener('click', (e) => {
    const target = e.target;
    if (target && target.closest('a')) {
      closeMenu();
    }
  });

  // Close menu when clicking outside on mobile
  document.addEventListener('click', (e) => {
    const clickedInsideNav =
      e.target.closest('.navbar') || e.target === toggleBtn;
    if (!clickedInsideNav) closeMenu();
  });

  // Optional: sync state when resizing across breakpoints
  // (데스크톱으로 넓어지면 강제로 열림 상태 가릴 필요 없음)
  const mq = window.matchMedia('(min-width: 768px)');
  mq.addEventListener('change', () => {
    // On desktop, menu is always visible via CSS; keep aria in a neutral state
    toggleBtn.setAttribute('aria-expanded', 'false');
    menu.classList.remove('is-open');
  });
})();