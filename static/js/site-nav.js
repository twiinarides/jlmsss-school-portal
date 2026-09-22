document.addEventListener("DOMContentLoaded", function () {

    const navbar = document.querySelector(".navbar");

    if (!navbar) return;

    function closeAll(exceptDropdown) {
        navbar.querySelectorAll('.dropdown.show').forEach(function (dd) {
            if (exceptDropdown && dd === exceptDropdown) return;

            dd.classList.remove('show');

            var menu = dd.querySelector('.dropdown-menu');
            if (menu) menu.classList.remove('show');

            var toggle = dd.querySelector('.dropdown-toggle');
            if (toggle) toggle.setAttribute('aria-expanded', 'false');
        });
    }

    // Dropdown toggle
    navbar.querySelectorAll('.dropdown-toggle').forEach(function (toggle) {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();

            var dropdown = toggle.closest('.dropdown');
            if (!dropdown) return;

            var menu = dropdown.querySelector('.dropdown-menu');
            var willOpen = !dropdown.classList.contains('show');

            closeAll(dropdown);

            dropdown.classList.toggle('show', willOpen);
            if (menu) menu.classList.toggle('show', willOpen);

            toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        });
    });

    // Close when clicking outside
    document.addEventListener('click', function (e) {
        if (!navbar.contains(e.target)) closeAll();
    });

    // ESC key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAll();
    });

    // Mobile drawer toggle
    const drawer = document.getElementById("kabaDrawer");
    const openBtn = document.querySelector("[data-drawer-open]");

    function openDrawer() {
        if (drawer) {
            drawer.classList.add("is-open");
            drawer.setAttribute("aria-hidden", "false");
        }
    }

    function closeDrawer() {
        if (drawer) {
            drawer.classList.remove("is-open");
            drawer.setAttribute("aria-hidden", "true");
        }
    }

    if (openBtn) {
        openBtn.addEventListener("click", function (e) {
            e.preventDefault();
            openDrawer();
        });
    }

    document.querySelectorAll("[data-drawer-close]").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            closeDrawer();
        });
    });

});
