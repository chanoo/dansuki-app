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
