(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    var navbar = document.getElementById('jazzy-navbar');
    if (!navbar) return;

    var userMenu = document.getElementById('jazzy-usermenu');
    if (!userMenu) return;

    var toggle = navbar.querySelector('a[data-toggle="dropdown"][title]');
    if (!toggle) {
      toggle = navbar.querySelector('a.nav-link.btn[title]');
    }
    if (!toggle) return;

    function openMenu() {
      userMenu.classList.add('show');
      userMenu.style.display = 'block';
      toggle.setAttribute('aria-expanded', 'true');
    }

    function closeMenu() {
      userMenu.classList.remove('show');
      userMenu.style.display = '';
      toggle.setAttribute('aria-expanded', 'false');
    }

    function isOpen() {
      return userMenu.classList.contains('show') || userMenu.style.display === 'block';
    }

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (isOpen()) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    document.addEventListener('click', function (e) {
      if (!isOpen()) return;
      if (userMenu.contains(e.target)) return;
      if (toggle.contains(e.target)) return;
      closeMenu();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) {
        closeMenu();
      }
    });

    var body = document.body;
    var overlay = document.createElement('div');
    overlay.className = 'jlmss-sidebar-overlay';
    document.body.appendChild(overlay);

    function isMobileSidebar() {
      return window.matchMedia('(max-width: 1023.98px)').matches;
    }

    function lockScroll(locked) {
      document.documentElement.classList.toggle('jlmss-admin-scroll-lock', locked);
      document.body.classList.toggle('jlmss-admin-scroll-lock', locked);
    }

    function setOverlay(active) {
      overlay.classList.toggle('is-active', !!active);
      lockScroll(!!active);
    }

    function closeSidebar() {
      body.classList.remove('sidebar-open');
      body.classList.add('sidebar-collapse');
      setOverlay(false);
    }

    function syncSidebar() {
      if (!isMobileSidebar()) {
        setOverlay(false);
        return;
      }

      var open = body.classList.contains('sidebar-open') && !body.classList.contains('sidebar-collapse');
      setOverlay(open);
    }

    if (isMobileSidebar()) {
      body.classList.add('sidebar-collapse');
    }

    overlay.addEventListener('click', function (e) {
      e.preventDefault();
      closeSidebar();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isMobileSidebar()) {
        closeSidebar();
      }
    });

    var observer = new MutationObserver(function () {
      syncSidebar();
    });

    observer.observe(body, { attributes: true, attributeFilter: ['class'] });

    var pushMenuBtn = document.querySelector('[data-widget="pushmenu"], [data-widget="PushMenu"], .nav-link[data-widget="pushmenu"]');
    if (pushMenuBtn) {
      pushMenuBtn.addEventListener('click', function () {
        window.setTimeout(syncSidebar, 0);
      });
    }

    window.setTimeout(syncSidebar, 0);

    window.addEventListener('resize', function () {
      if (isMobileSidebar()) {
        body.classList.add('sidebar-collapse');
      } else {
        setOverlay(false);
      }
    });
  });
})();
