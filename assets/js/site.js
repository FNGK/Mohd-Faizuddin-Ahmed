(function () {
  const root = document.documentElement;
  const menuButton = document.getElementById("menuToggle");
  const mobileNav = document.getElementById("mobileNav");
  const yearNodes = document.querySelectorAll("[data-current-year]");
  const topbarInner = document.querySelector(".topbar-inner");

  initTheme();
  initMobileMenu();
  initYear();
  initDynamicCtas();
  initPredictivePrefetching();
  initTableOfContents();
  initAudioMode();
  initBackToTop();

  function initTheme() {
    const key = "seowithfaiz-theme";
    const stored = safeGet(key);
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const activeTheme = stored || (prefersDark ? "dark" : "light");
    applyTheme(activeTheme);

    if (!topbarInner) return;

    let btn = document.getElementById("themeToggle");
    if (!btn) {
      btn = document.createElement("button");
      btn.id = "themeToggle";
      btn.className = "theme-toggle";
      btn.type = "button";
      btn.setAttribute("aria-label", "Toggle dark mode");
      btn.title = "Toggle dark mode";
      const menu = document.getElementById("menuToggle");
      if (menu) {
        topbarInner.insertBefore(btn, menu);
      } else {
        topbarInner.appendChild(btn);
      }
    }

    setThemeIcon(btn, activeTheme);
    btn.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      setThemeIcon(btn, next);
      safeSet(key, next);
    });
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) {
      themeMeta.setAttribute("content", theme === "dark" ? "#0b1220" : "#f4f6f8");
    }
  }

  function setThemeIcon(button, theme) {
    button.textContent = theme === "dark" ? "☀" : "☾";
    button.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
  }

  function initMobileMenu() {
    if (!menuButton || !mobileNav) return;

    menuButton.addEventListener("click", function () {
      const expanded = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", expanded ? "false" : "true");
      mobileNav.classList.toggle("open");
    });

    mobileNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        mobileNav.classList.remove("open");
        menuButton.setAttribute("aria-expanded", "false");
      });
    });
  }

  function initYear() {
    yearNodes.forEach(function (node) {
      node.textContent = String(new Date().getFullYear());
    });
  }

  function initDynamicCtas() {
    const dynamicCtas = Array.from(document.querySelectorAll('[data-dynamic-cta], .nav-cta, .cta-band .btn-primary'));
    if (!dynamicCtas.length) return;

    const params = new URLSearchParams(window.location.search);
    const utmSource = (params.get("utm_source") || "").toLowerCase();
    const refHost = getRefHost();
    const source = utmSource || refHost;

    dynamicCtas.forEach(function (cta) {
      if (!cta.dataset.defaultLabel) {
        cta.dataset.defaultLabel = cta.textContent.trim();
      }
      if (source.includes("linkedin")) {
        cta.textContent = "Book LinkedIn strategy call";
      } else if (source.includes("google")) {
        cta.textContent = "Get custom SEO growth plan";
      } else if (source.includes("youtube")) {
        cta.textContent = "Book 15-min SEO review";
      }
    });

    let scrolled = false;
    window.addEventListener(
      "scroll",
      function () {
        const depth = getScrollDepth();
        if (!scrolled && depth > 0.45) {
          scrolled = true;
          dynamicCtas.forEach(function (cta) {
            cta.textContent = "Request custom SEO action plan";
          });
        }
      },
      { passive: true }
    );
  }

  function initPredictivePrefetching() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection && (connection.saveData || /2g/.test(connection.effectiveType || ""))) return;

    const prefetched = new Set();
    const links = document.querySelectorAll('a[href]');
    links.forEach(function (link) {
      const href = link.getAttribute("href");
      if (!isPrefetchable(href)) return;

      const prefetch = function () {
        const abs = toAbsoluteUrl(href);
        if (!abs || prefetched.has(abs)) return;
        const hint = document.createElement("link");
        hint.rel = "prefetch";
        hint.href = abs;
        hint.as = "document";
        document.head.appendChild(hint);
        prefetched.add(abs);
      };

      link.addEventListener("mouseenter", prefetch, { once: true });
      link.addEventListener("focus", prefetch, { once: true });
    });
  }

  function initTableOfContents() {
    const tocContainer = document.getElementById("toc");
    if (!tocContainer) return;

    const scope = document.querySelector('[data-toc-scope]') || document.querySelector(".post-body");
    if (!scope) return;
    const headings = Array.from(scope.querySelectorAll("h2, h3"));
    if (!headings.length) return;

    const list = document.createElement("ol");
    list.className = "toc-list";
    headings.forEach(function (heading, index) {
      if (!heading.id) {
        heading.id = slugify(heading.textContent || "section-" + String(index + 1));
      }
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = "#" + heading.id;
      a.textContent = heading.textContent || "Section";
      li.appendChild(a);
      list.appendChild(li);
    });

    tocContainer.innerHTML = "";
    const title = document.createElement("strong");
    title.textContent = "On this page";
    tocContainer.appendChild(title);
    tocContainer.appendChild(list);

    const back = document.createElement("a");
    back.href = "#main";
    back.className = "back-to-top";
    back.textContent = "Back to top";
    tocContainer.appendChild(back);
  }

  function initAudioMode() {
    const button = document.querySelector("[data-audio-toggle]");
    const target = document.querySelector("[data-audio-source]");
    if (!button || !target) return;
    if (!("speechSynthesis" in window)) return;

    let speaking = false;

    button.addEventListener("click", function () {
      if (speaking) {
        window.speechSynthesis.cancel();
        speaking = false;
        button.textContent = "Listen to this article";
        return;
      }

      const text = target.innerText.replace(/\s+/g, " ").trim();
      if (!text) return;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.onend = function () {
        speaking = false;
        button.textContent = "Listen to this article";
      };
      speaking = true;
      button.textContent = "Stop audio";
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    });
  }

  function initBackToTop() {
    const button = document.querySelector("[data-back-to-top]");
    if (!button) return;
    button.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function getRefHost() {
    if (!document.referrer) return "";
    try {
      return new URL(document.referrer).hostname.toLowerCase();
    } catch (_e) {
      return "";
    }
  }

  function getScrollDepth() {
    const h = document.documentElement;
    const scrollTop = h.scrollTop || document.body.scrollTop || 0;
    const max = h.scrollHeight - h.clientHeight;
    if (max <= 0) return 0;
    return scrollTop / max;
  }

  function isPrefetchable(href) {
    if (!href) return false;
    if (
      href.startsWith("#") ||
      href.startsWith("mailto:") ||
      href.startsWith("tel:") ||
      href.startsWith("javascript:") ||
      href.startsWith("http://") ||
      href.startsWith("https://")
    ) {
      return false;
    }
    return href.endsWith(".html") || href.includes("/") || href === ".";
  }

  function toAbsoluteUrl(href) {
    try {
      return new URL(href, window.location.href).href;
    } catch (_e) {
      return "";
    }
  }

  function slugify(value) {
    return String(value)
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-");
  }

  function safeGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (_e) {
      return null;
    }
  }

  function safeSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (_e) {
      // ignore storage errors
    }
  }
})();
