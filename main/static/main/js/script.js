document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('mobile-toggle');
  const menu = document.getElementById('mobile-menu');
  const closeBtn = document.getElementById('mobile-close');
  const overlay = document.getElementById('mobile-overlay');

  function openMenu() {
    menu.classList.add('open');
    overlay.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
    menu.setAttribute('aria-hidden', 'false');
  }
  function closeMenu() {
    menu.classList.remove('open');
    overlay.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-hidden', 'true');
  }

  toggle.addEventListener('click', openMenu);
  closeBtn.addEventListener('click', closeMenu);
  overlay.addEventListener('click', closeMenu);

  // ESC закрывает
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

  // при смене размера экрана — скрываем мобильное меню
  window.addEventListener('resize', () => { if (window.innerWidth > 768) closeMenu(); });

  // на случай, если где-то вызываешь openNav()/closeNav()
  window.openNav = openMenu;
  window.closeNav = closeMenu;
});
