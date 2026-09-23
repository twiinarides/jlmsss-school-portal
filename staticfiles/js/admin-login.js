(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    var password = document.getElementById('id_password');
    var username = document.getElementById('id_username');
    var toggle = document.querySelector('[data-toggle-password]');
    var remember = document.querySelector('[data-remember-username]');

    try {
      var saved = window.localStorage.getItem('jlmss_admin_username');
      if (saved && username && !username.value) {
        username.value = saved;
      }
    } catch (e) {
    }

    if (toggle && password) {
      toggle.addEventListener('click', function () {
        var isHidden = password.type === 'password';
        password.type = isHidden ? 'text' : 'password';
        var icon = toggle.querySelector('i');
        if (icon) {
          icon.className = isHidden ? 'fas fa-eye-slash' : 'fas fa-eye';
        }
      });
    }

    var form = document.querySelector('form.jlmss-login__form');
    if (form && username) {
      form.addEventListener('submit', function () {
        if (!remember) return;
        try {
          if (remember.checked) {
            window.localStorage.setItem('jlmss_admin_username', username.value || '');
          } else {
            window.localStorage.removeItem('jlmss_admin_username');
          }
        } catch (e) {
        }
      });
    }

    if (username && !username.value) {
      username.focus();
    } else if (password) {
      password.focus();
    }
  });
})();
