(function () {
  var root = document.documentElement;
  var savedTheme = window.localStorage.getItem("theme");
  if (savedTheme === "dark" || savedTheme === "light") {
    root.dataset.theme = savedTheme;
  }

  function updateToggle(toggle) {
    var isDark = root.dataset.theme === "dark";
    toggle.textContent = isDark ? "light" : "dark";
    toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    toggle.setAttribute("aria-pressed", String(isDark));
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector(".theme-toggle");
    if (!toggle) {
      return;
    }
    updateToggle(toggle);
    toggle.addEventListener("click", function () {
      var nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = nextTheme;
      window.localStorage.setItem("theme", nextTheme);
      updateToggle(toggle);
    });
  });
}());
