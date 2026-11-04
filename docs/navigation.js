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

/* Android 휴대폰: App Store 링크를 Google Play로(2026-11-04 Play 정식 출시). Google Play 배지가 옆에 따로 있으면 App Store 배지는 숨긴다. */
(() => {
  if (!/Android/i.test(navigator.userAgent)) return;
  const PLAY = 'https://play.google.com/store/apps/details?id=com.dansuki.android';
  const play = '<path d="M4.2 2.6c-.2.2-.3.6-.3 1v16.8c0 .4.1.8.3 1l9.4-9.4zM14.6 13l2.6 2.6-11.1 6.3c-.4.2-.8.3-1.1.2zm3.9-3.9 2.9 1.7c.8.5.8 1.8 0 2.3l-2.9 1.6-2.8-2.8zM6.1 2.1l11.1 6.3L14.6 11 5 1.9c.3-.1.7 0 1.1.2z"/>';
  document.querySelectorAll('a[href*="apps.apple.com"]').forEach(link => {
    const box = link.parentElement;
    if (link.classList.contains('store') && box && box.querySelector('.store.gp')) { link.hidden = true; link.style.display = 'none'; return; }
    if (box && box.classList.contains('get-row') && box.querySelector('a[href*="play.google.com"]')) {
      link.style.display = 'none';
      const sep = link.nextElementSibling; if (sep && sep.tagName === 'SPAN') sep.style.display = 'none';
      return;
    }
    link.href = PLAY;
    if (link.classList.contains('store')) {
      link.setAttribute('aria-label', 'Google Play에서 단숙이 받기');
      const svg = link.querySelector('svg'), small = link.querySelector('small');
      if (svg) svg.innerHTML = play;
      if (small) small.textContent = 'Google Play에서';
    }
  });
})();
