(function () {
  var root = document.documentElement;
  var savedTheme = window.localStorage.getItem("theme");
  if (savedTheme === "dark" || savedTheme === "light") {
    root.dataset.theme = savedTheme;
  }

  function updateToggle(toggle) {
    var isDark = root.dataset.theme === "dark";
    toggle.textContent = isDark ? "☀" : "☾";
    toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    toggle.setAttribute("aria-pressed", String(isDark));
  }

  function positionBioPhoto() {
    var photo = document.querySelector(".bio-photo");
    var text = document.querySelector(".bio-intro");
    if (!photo || !text || window.matchMedia("(max-width: 760px)").matches) {
      if (photo) {
        photo.style.removeProperty("--bio-photo-left");
      }
      return;
    }

    var textRight = text.getBoundingClientRect().right;
    var midpoint = textRight + (window.innerWidth - textRight) / 2;
    var bias = parseFloat(getComputedStyle(document.documentElement)
      .getPropertyValue("--bio-photo-horizontal-bias")) || 0;
    var photoRect = photo.getBoundingClientRect();
    var left = midpoint - bias - photoRect.width / 2;

    photo.style.setProperty("--bio-photo-left", left + "px");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector(".theme-toggle");
    if (toggle) {
      updateToggle(toggle);
      toggle.addEventListener("click", function () {
        var nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        root.dataset.theme = nextTheme;
        window.localStorage.setItem("theme", nextTheme);
        updateToggle(toggle);
      });
    }
    positionBioPhoto();
    window.addEventListener("resize", positionBioPhoto);
  });
}());
