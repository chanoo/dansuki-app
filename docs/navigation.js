/* Native details keeps study navigation usable without JavaScript. */
(() => {
  const menus = [...document.querySelectorAll('nav.top .study-menu')];
  if (!menus.length) return;
  const closeAll = () => menus.forEach(menu => { menu.open = false; });
  menus.forEach((menu, index) => {
    const summary = menu.querySelector('summary');
    const panel = menu.querySelector('.study-dropdown');
    panel.id = `study-links-${index + 1}`;
    summary.setAttribute('aria-controls', panel.id);
    summary.setAttribute('aria-expanded', String(menu.open));
    menu.addEventListener('toggle', () => {
      summary.setAttribute('aria-expanded', String(menu.open));
      if (menu.open) menus.forEach(other => { if (other !== menu) other.open = false; });
    });
  });
  document.addEventListener('pointerdown', event => {
    menus.forEach(menu => { if (!menu.contains(event.target)) menu.open = false; });
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const open = menus.find(menu => menu.open);
    if (!open) return;
    event.preventDefault();
    closeAll();
    open.querySelector('summary').focus();
  });
  matchMedia('(max-width: 880px)').addEventListener('change', closeAll);
})();

/* 휴대폰: 내려 읽는 동안 위 막대를 숨기고, 조금이라도 올리면 다시 보여 준다. */
(() => {
  const nav = document.querySelector('nav.top');
  if (!nav) return;
  const narrow = matchMedia('(max-width: 880px)');
  let lastY = scrollY, ticking = false;
  const sync = () => {
    ticking = false;
    const y = scrollY, delta = y - lastY;
    // 메뉴가 열려 있거나 맨 위 근처면 늘 보인다. 작은 흔들림(관성 스크롤 끝)은 무시한다.
    if (!narrow.matches || y < 120 || nav.querySelector('.study-menu[open]')) nav.classList.remove('away');
    else if (delta > 6) nav.classList.add('away');
    else if (delta < -6) nav.classList.remove('away');
    if (Math.abs(delta) > 6 || y < 120) lastY = y;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(sync); } }, { passive: true });
  nav.addEventListener('focusin', () => nav.classList.remove('away'));
})();

/* Android 휴대폰: App Store 대신 테스터 신청 페이지로(Google Play 비공개 테스트, 2026-10-20). */
(() => {
  if (!/Android/i.test(navigator.userAgent)) return;
  const play = '<path d="M4.2 2.6c-.2.2-.3.6-.3 1v16.8c0 .4.1.8.3 1l9.4-9.4zM14.6 13l2.6 2.6-11.1 6.3c-.4.2-.8.3-1.1.2zm3.9-3.9 2.9 1.7c.8.5.8 1.8 0 2.3l-2.9 1.6-2.8-2.8zM6.1 2.1l11.1 6.3L14.6 11 5 1.9c.3-.1.7 0 1.1.2z"/>';
  document.querySelectorAll('a[href*="apps.apple.com"]').forEach(link => {
    link.href = '/android/';
    if (link.classList.contains('store')) {
      link.setAttribute('aria-label', 'Android 먼저 써 보기 신청');
      const svg = link.querySelector('svg'), small = link.querySelector('small'), b = link.querySelector('b');
      if (svg) svg.innerHTML = play;
      if (small) small.textContent = 'Android';
      if (b) b.textContent = '먼저 써 보기';
    } else if (link.classList.contains('get')) link.textContent = '먼저 써 보기';
    else if (link.closest('.dock')) link.textContent = '신청';
  });
  // Android 사용자에겐 '먼저 써 보기' 배지가 위 버튼과 겹치므로 숨긴다.
  document.querySelectorAll('.store.soon').forEach(el => { el.style.display = 'none'; });
  const dockSmall = document.querySelector('.dock small');
  if (dockSmall) dockSmall.textContent = 'Android 먼저 써 보기';
})();
