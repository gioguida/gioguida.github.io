(function () {
  "use strict";

  var busy = false;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var pageCache = new Map();
  var imageCache = new Map();
  var warmedPages = new Set();

  function loadPage(url) {
    if (!pageCache.has(url)) {
      var request = fetch(url).then(function (response) {
        if (!response.ok) throw new Error("Page could not be loaded: " + response.status);
        return response.text();
      }).catch(function (error) {
        pageCache.delete(url);
        throw error;
      });
      pageCache.set(url, request);
    }
    return pageCache.get(url);
  }

  function loadImage(url) {
    if (!imageCache.has(url)) {
      var image = new Image();
      image.src = url;
      var ready = image.decode ? image.decode().catch(function () { imageCache.delete(url); }) : Promise.resolve();
      imageCache.set(url, ready);
    }
    return imageCache.get(url);
  }

  function warmPage(url) {
    if (new URL(url).pathname === window.location.pathname || warmedPages.has(url)) return;
    warmedPages.add(url);
    loadPage(url).then(function (markup) {
      var documentCopy = new DOMParser().parseFromString(markup, "text/html");
      documentCopy.querySelectorAll("main img[src]").forEach(function (image) {
        loadImage(new URL(image.getAttribute("src"), url).href);
      });
    }).catch(function () { warmedPages.delete(url); });
  }

  function timing(name, fallback) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
  }

  function milliseconds(value) {
    return value.endsWith("ms") ? parseFloat(value) : parseFloat(value) * 1000;
  }

  function visible(element) {
    if (!element) return false;
    var rect = element.getBoundingClientRect();
    return rect.top < window.innerHeight && rect.bottom > 0;
  }

  function selectorBounds(nav, link) {
    var navRect = nav.getBoundingClientRect();
    var linkRect = link.getBoundingClientRect();
    return {
      left: linkRect.left - navRect.left,
      top: linkRect.top - navRect.top,
      width: linkRect.width,
      height: linkRect.height
    };
  }

  function positionNavSelector(nav) {
    var active = nav.querySelector('a[aria-current="page"]');
    var selector = nav.querySelector(".nav-selector");
    if (!active || !selector) return;
    var bounds = selectorBounds(nav, active);
    selector.style.left = bounds.left + "px";
    selector.style.top = bounds.top + "px";
    selector.style.width = bounds.width + "px";
    selector.style.height = bounds.height + "px";
    updateNavLens(nav);
  }

  function updateNavLens(nav) {
    var selector = nav.querySelector(".nav-selector");
    if (!selector) return;
    var lensRect = selector.getBoundingClientRect();
    var magnification = parseFloat(timing("--nav-lens-scale", "1.12"));
    nav.querySelectorAll("a").forEach(function (link) {
      var label = link.querySelector(".nav-label");
      if (!label || !link.getClientRects().length) return;
      var linkRect = link.getBoundingClientRect();
      if (!linkRect.width) return;
      var overlap = Math.max(0, Math.min(lensRect.right, linkRect.right) - Math.max(lensRect.left, linkRect.left));
      var coverage = Math.min(1, overlap / linkRect.width);
      var smoothCoverage = coverage * coverage * (3 - 2 * coverage);
      label.style.setProperty("--lens-scale", String(1 + (magnification - 1) * smoothCoverage));
    });
  }

  function prepareNavSelector(nav) {
    var active = nav.querySelector('a[aria-current="page"]');
    if (!active || !active.getClientRects().length) return;
    nav.querySelectorAll("a").forEach(function (link) {
      var label = document.createElement("span");
      label.className = "nav-label";
      while (link.firstChild) label.appendChild(link.firstChild);
      link.appendChild(label);
    });
    var selector = document.createElement("span");
    selector.className = "nav-selector";
    selector.setAttribute("aria-hidden", "true");
    nav.appendChild(selector);
    positionNavSelector(nav);
    nav.classList.add("has-selector");
  }

  function slideNavSelector(nav, destination, duration) {
    var selector = nav.querySelector(".nav-selector");
    if (!selector) return Promise.resolve();
    var bounds = selectorBounds(nav, destination);
    var distance = bounds.left - parseFloat(selector.style.left);
    var animation = selector.animate(
      [{ transform: "translateX(0)" },
        { transform: "translateX(" + distance + "px)" }],
      { duration: duration, easing: timing("--page-slide-easing", "ease-out"), fill: "forwards" });
    function followLens() {
      updateNavLens(nav);
      if (animation.playState === "running") requestAnimationFrame(followLens);
    }
    requestAnimationFrame(followLens);
    return animation.finished.then(function () { updateNavLens(nav); });
  }

  function resolveLinks(scope, base) {
    scope.querySelectorAll("[href], [src]").forEach(function (element) {
      ["href", "src"].forEach(function (attribute) {
        var value = element.getAttribute(attribute);
        if (value && !value.startsWith("#") && !/^(?:[a-z]+:|\/\/)/i.test(value)) {
          element.setAttribute(attribute, new URL(value, base).href);
        }
      });
    });
  }

  function panel(main, footer, home) {
    var wrapper = document.createElement("div");
    wrapper.className = "transition-panel" + (home ? " home-page" : "");
    wrapper.appendChild(main);
    footer.style.visibility = "hidden";
    wrapper.appendChild(footer);
    return wrapper;
  }

  function preparePanel(panelElement, stage) {
    var footer = panelElement.querySelector(":scope > .footer");
    var main = panelElement.querySelector("main");
    var isHome = panelElement.classList.contains("home-page");
    var enteringFooter = null;
    if (stage) {
      if (!isHome) {
        panelElement.style.height = "auto";
        panelElement.style.minHeight = "100%";
        main.style.minHeight = "auto";
        main.style.overflow = "visible";
      }
      var footerTop = footer.getBoundingClientRect().top - stage.getBoundingClientRect().top;
      if (!isHome) {
        panelElement.style.height = "";
        panelElement.style.minHeight = "";
        main.style.minHeight = "";
        main.style.overflow = "";
      }
      if (footerTop < stage.clientHeight) {
        enteringFooter = document.createElement("div");
        enteringFooter.className = "transition-footer";
        enteringFooter.style.top = footerTop + "px";
      }
    }
    if (isHome) {
      main.style.paddingBottom = footer.getBoundingClientRect().height + "px";
    }
    if (enteringFooter) {
      footer.style.visibility = "";
      enteringFooter.appendChild(footer);
      stage.appendChild(enteringFooter);
    } else {
      footer.remove();
    }
    return enteringFooter;
  }

  function attachPhoto(panelElement, existingPhoto) {
    if (window.matchMedia("(max-width: " + timing("--bio-stack-breakpoint", "1000px") + ")").matches) return;
    var photo = panelElement.querySelector(".bio-photo");
    if (!photo) return;
    var left;
    var top;
    if (existingPhoto) {
      var originalRect = existingPhoto.getBoundingClientRect();
      left = originalRect.left;
      top = originalRect.top;
    } else {
      var intro = panelElement.querySelector(".bio-intro");
      var introRight = intro.getBoundingClientRect().right - panelElement.getBoundingClientRect().left;
      var bias = parseFloat(timing("--bio-photo-horizontal-bias", "0")) || 0;
      var photoWidth = photo.getBoundingClientRect().width;
      var gap = parseFloat(timing("--bio-photo-column-gap", "24px")) || 0;
      var pageRight = panelElement.querySelector("main").getBoundingClientRect().right - panelElement.getBoundingClientRect().left;
      left = Math.max(introRight + gap,
        Math.min(pageRight - photoWidth, introRight + (window.innerWidth - introRight) / 2 - bias - photoWidth / 2));
      top = parseFloat(timing("--bio-photo-fixed-top", "160px"));
    }
    panelElement.appendChild(photo);
    photo.style.left = left + "px";
    photo.style.top = top + "px";
  }

  function animate(element, keyframes, options) {
    return element.animate(keyframes, options).finished;
  }

  function resetScroll() {
    var root = document.documentElement;
    var previous = root.style.getPropertyValue("scroll-behavior");
    var previousPriority = root.style.getPropertyPriority("scroll-behavior");
    root.style.setProperty("scroll-behavior", "auto", "important");
    // Apply the override before asking the browser to change scroll position.
    getComputedStyle(root).scrollBehavior;
    window.scrollTo(0, 0);
    requestAnimationFrame(function () {
      if (previous) root.style.setProperty("scroll-behavior", previous, previousPriority);
      else root.style.removeProperty("scroll-behavior");
    });
  }

  async function navigate(link, direction) {
    if (busy) return;
    busy = true;
    var target = link.href;
    var oldMain = document.querySelector("body > main");
    var oldFooter = document.querySelector("body > footer");
    var stage;
    try {
      var next = new DOMParser().parseFromString(await loadPage(target), "text/html");
      var nextMain = next.querySelector("body > main");
      var nextFooter = next.querySelector("body > footer");
      var nextNav = next.querySelector(".site-nav");
      if (!nextMain || !nextFooter || !nextNav) throw new Error("Page markup is incomplete");
      resolveLinks(nextMain, target);
      resolveLinks(nextFooter, target);
      resolveLinks(nextNav, target);
      await Promise.all(Array.from(nextMain.querySelectorAll("img[src]"), function (image) {
        return image.decode ? image.decode().catch(function () { /* Keep navigation usable if an image fails. */ }) : Promise.resolve();
      }));

      var footerWasVisible = visible(oldFooter);
      var footerDuration = milliseconds(timing("--footer-slide-duration", "170ms"));
      var slideDuration = milliseconds(timing("--page-slide-duration", "520ms"));
      if (footerWasVisible && !reduceMotion.matches) {
        await animate(oldFooter, [{ transform: "translateY(0)" }, { transform: "translateY(110%)" }],
          { duration: footerDuration, easing: timing("--footer-slide-easing", "ease-in"), fill: "forwards" });
      }

      if (!reduceMotion.matches) {
        stage = document.createElement("div");
        stage.className = "transition-stage";
        var track = document.createElement("div");
        track.className = "transition-track";
        var currentPanel = panel(oldMain.cloneNode(true), oldFooter.cloneNode(true), document.body.classList.contains("home-page"));
        var nextPanel = panel(nextMain.cloneNode(true), nextFooter.cloneNode(true), next.body.classList.contains("home-page"));
        if (direction < 0) {
          track.append(nextPanel, currentPanel);
          track.style.transform = "translateX(-50%)";
        } else {
          track.append(currentPanel, nextPanel);
        }
        stage.appendChild(track);
        document.body.appendChild(stage);
        preparePanel(currentPanel, null);
        var enteringFooter = preparePanel(nextPanel, stage);
        attachPhoto(currentPanel, oldMain.querySelector(".bio-photo"));
        attachPhoto(nextPanel, null);
        currentPanel.querySelector("main").scrollTop = window.scrollY;
        oldMain.style.visibility = "hidden";
        oldFooter.style.visibility = "hidden";
        var slideEasing = timing("--page-slide-easing", "ease-out");
        var animations = [
          animate(track,
            [{ transform: direction < 0 ? "translateX(-50%)" : "translateX(0)" },
              { transform: direction < 0 ? "translateX(0)" : "translateX(-50%)" }],
            { duration: slideDuration, easing: slideEasing, fill: "forwards" }),
          slideNavSelector(document.querySelector(".site-nav"), link, slideDuration)
        ];
        if (enteringFooter) {
          animations.push(animate(enteringFooter,
            [{ transform: "translateY(110%)" }, { transform: "translateY(0)" }],
            { duration: slideDuration, easing: slideEasing, fill: "forwards" }));
        }
        await Promise.all(animations);
      }

      document.body.classList.toggle("home-page", next.body.classList.contains("home-page"));
      oldMain.replaceWith(nextMain);
      oldFooter.replaceWith(nextFooter);
      document.querySelector(".site-nav").replaceWith(nextNav);
      prepareNavSelector(nextNav);
      document.title = next.title;
      ["description"].forEach(function (name) {
        var source = next.querySelector('meta[name="' + name + '"]');
        var destination = document.querySelector('meta[name="' + name + '"]');
        if (source && destination) destination.content = source.content;
      });
      var canonical = next.querySelector('link[rel="canonical"]');
      var currentCanonical = document.querySelector('link[rel="canonical"]');
      if (canonical && currentCanonical) currentCanonical.href = canonical.href;
      history.pushState({}, "", target);
      resetScroll();
      window.dispatchEvent(new Event("resize"));
      if (stage) stage.remove();
    } catch (error) {
      console.error("Page transition failed; opening the destination normally.", error);
      if (stage) stage.remove();
      if (oldMain.isConnected) oldMain.style.visibility = "";
      if (oldFooter.isConnected) {
        oldFooter.style.visibility = "";
        oldFooter.getAnimations().forEach(function (animation) { animation.cancel(); });
      }
      window.location.href = target;
    } finally {
      busy = false;
    }
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest(".site-nav a");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var links = Array.from(link.closest(".site-nav").querySelectorAll("a"));
    var current = links.findIndex(function (item) { return item.getAttribute("aria-current") === "page"; });
    var destination = links.indexOf(link);
    if (new URL(link.href).pathname === window.location.pathname || busy) {
      event.preventDefault();
      return;
    }
    event.preventDefault();
    navigate(link, destination < current ? -1 : 1);
  });

  document.addEventListener("DOMContentLoaded", function () {
    prepareNavSelector(document.querySelector(".site-nav"));
    if (document.fonts) document.fonts.ready.then(function () {
      positionNavSelector(document.querySelector(".site-nav"));
    });
    window.addEventListener("resize", function () {
      if (!busy) positionNavSelector(document.querySelector(".site-nav"));
    });
  });

  document.addEventListener("pointerover", function (event) {
    var link = event.target.closest(".site-nav a");
    if (link) warmPage(link.href);
  });
  document.addEventListener("focusin", function (event) {
    var link = event.target.closest(".site-nav a");
    if (link) warmPage(link.href);
  });
  window.addEventListener("load", function () {
    var schedule = window.requestIdleCallback || function (callback) { return setTimeout(callback, 200); };
    schedule(function () {
      document.querySelectorAll(".site-nav a").forEach(function (link) { warmPage(link.href); });
    });
  });

  window.addEventListener("popstate", function () { window.location.reload(); });
}());
