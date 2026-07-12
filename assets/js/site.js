(function () {
  const root = document.documentElement;
  const menuButton = document.getElementById("menuToggle");
  const mobileNav = document.getElementById("mobileNav");
  const yearNodes = document.querySelectorAll("[data-current-year]");
  const topbarInner = document.querySelector(".topbar-inner");

  initTheme();
  initTopbarScroll();
  initMobileMenu();
  initYear();
  initDynamicCtas();
  initPredictivePrefetching();
  initTableOfContents();
  initAudioMode();
  initBackToTop();
  initScrollReveal();
  initCounters();
  initReadingProgress();
  initAnalyticsEvents();
    initConsent();

  function initTheme() {
    const key = "seowithfaiz-theme";
    const stored = safeGet(key);
    // Dark-premium is the brand's default identity; honor an explicit stored
    // choice, otherwise default everyone to dark. Light remains a toggle.
    const activeTheme = stored || "dark";
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
      themeMeta.setAttribute("content", theme === "dark" ? "#08111f" : "#f2ebe0");
    }
  }

  function setThemeIcon(button, theme) {
    button.textContent = theme === "dark" ? "☀" : "☾";
    button.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
  }

  function initTopbarScroll() {
    const topbar = document.querySelector(".topbar");
    if (!topbar) return;

    const sync = function () {
      topbar.classList.toggle("is-scrolled", window.scrollY > 12);
    };

    sync();
    window.addEventListener("scroll", sync, { passive: true });
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
        cta.textContent = "Get a custom growth plan";
      } else if (source.includes("youtube")) {
        cta.textContent = "Book a 15-min review";
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
            cta.textContent = "Request a custom growth plan";
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

  function initAnalyticsEvents() {
    if (typeof window.gtag !== "function") return;

    document.addEventListener(
      "click",
      function (event) {
        const el = event.target.closest ? event.target.closest("a, button") : null;
        if (!el) return;

        if (el.matches("[data-dynamic-cta], .nav-cta, .btn-primary")) {
          window.gtag("event", "cta_click", {
            cta_label: (el.textContent || "").trim().slice(0, 60),
            cta_href: el.getAttribute("href") || "",
          });
        }

        const href = el.getAttribute && el.getAttribute("href");
        if (href && /^https?:\/\//i.test(href) && href.indexOf("seowithfaiz.com") === -1) {
          window.gtag("event", "outbound_click", { link_url: href });
        }
      },
      { passive: true }
    );

    const form = document.querySelector(".contact-form, form[data-contact]");
    if (form) {
      form.addEventListener("submit", function () {
        window.gtag("event", "generate_lead", { method: "contact_form" });
      });
    }
  }

  function initReadingProgress() {
    const bar = document.querySelector("[data-read-progress]");
    if (!bar) return;
    const article = document.querySelector(".post-body") || document.querySelector("main");
    if (!article) return;

    const update = function () {
      const rect = article.getBoundingClientRect();
      const total = rect.height - window.innerHeight;
      const scrolled = Math.min(Math.max(-rect.top, 0), Math.max(total, 1));
      const ratio = total > 0 ? Math.min(scrolled / total, 1) : 0;
      bar.style.transform = "scaleX(" + ratio + ")";
    };

    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update, { passive: true });
  }

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function initScrollReveal() {
    if (prefersReducedMotion() || !("IntersectionObserver" in window)) return;

    // Elements worth revealing on scroll. Hero content animates on load, so skip it.
    const selectors = [
      ".section .kicker",
      ".section h2",
      ".card",
      ".proof-card",
      ".visual-pillar",
      ".stat-ribbon__item",
      ".price-card",
      ".process-step",
      ".market-strip__item",
      ".faq-item",
      ".timeline-item",
      ".blog-card",
      ".answer-box",
      ".service-table",
      ".quote"
    ];

    const seen = new Set();
    const targets = [];
    selectors.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el) {
        if (seen.has(el) || el.closest(".hero")) return;
        seen.add(el);
        targets.push(el);
      });
    });
    if (!targets.length) return;

    // Stagger by index within the same parent for a wave effect.
    targets.forEach(function (el) {
      el.classList.add("reveal");
      const siblings = Array.prototype.filter.call(
        el.parentNode ? el.parentNode.children : [],
        function (c) { return c.classList && c.classList.contains("reveal"); }
      );
      const idx = Math.max(0, siblings.indexOf(el));
      el.style.transitionDelay = Math.min(idx * 80, 360) + "ms";
    });

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal--in");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );

    targets.forEach(function (el) { observer.observe(el); });
  }

  function initCounters() {
    const counters = document.querySelectorAll("[data-count-to]");
    if (!counters.length) return;

    const run = function (el) {
      const target = parseFloat(el.getAttribute("data-count-to"));
      if (isNaN(target)) return;
      const prefix = el.getAttribute("data-count-prefix") || "";
      const suffix = el.getAttribute("data-count-suffix") || "";
      const decimals = parseInt(el.getAttribute("data-count-decimals") || "0", 10);

      if (prefersReducedMotion()) {
        el.textContent = prefix + target.toFixed(decimals) + suffix;
        return;
      }

      const duration = 1400;
      const start = performance.now();
      const step = function (now) {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + (target * eased).toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    if (!("IntersectionObserver" in window)) {
      counters.forEach(run);
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            run(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.6 }
    );
    counters.forEach(function (el) { observer.observe(el); });
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

  // ───────────────────────────────────────────────────────────────
  // Cookie consent — drives Cloudflare Zaraz's consent API and emits
  // Google Consent Mode v2 signals. CSP-safe: this script is 'self', and
  // the injected <style> is allowed by style-src 'unsafe-inline'. The
  // banner only appears once Zaraz (the tag host) is live — no tags, no
  // banner — so it activates automatically when you enable Zaraz.
  // ───────────────────────────────────────────────────────────────
  var CONSENT_KEY = "swf-consent-v1";
  // After creating consent purposes in Cloudflare → Zaraz → Consent, paste
  // their purpose IDs here so granular Analytics/Marketing choices map exactly.
  // Left empty, we fall back to Zaraz setAll() for a simple accept/reject.
  var CONSENT_PURPOSES = { analytics: "", advertising: "" };

  function initConsent() {
    // Consent Mode defaults are set in gtm-loader.js (before GTM loads). Here
    // we just apply a stored choice or show the banner. Tags now always exist
    // (GTM is site-wide), so the banner shows whenever there's no saved choice.
    var stored = readConsent();
    if (stored) {
      applyConsent(stored, false);
    } else {
      renderConsentBanner(false);
    }
    document.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("[data-cookie-settings]") : null;
      if (t) { e.preventDefault(); renderConsentBanner(true); }
    });
    window.swfOpenConsent = function () { renderConsentBanner(true); };
  }

  function readConsent() {
    var raw = safeGet(CONSENT_KEY);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch (_e) { return null; }
  }

  function saveConsent(choice) {
    safeSet(CONSENT_KEY, JSON.stringify(choice));
    try {
      document.cookie = "swf_consent=" + (choice.analytics ? "a" : "") + (choice.advertising ? "m" : "") +
        "; Max-Age=31536000; Path=/; SameSite=Lax" + (location.protocol === "https:" ? "; Secure" : "");
    } catch (_e) {}
  }

  function consentModeDefault() {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(["consent", "default", {
      ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied",
      analytics_storage: "denied", wait_for_update: 500
    }]);
  }

  function applyConsent(choice, isUpdate) {
    applyZarazConsent(choice);
    if (isUpdate) {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(["consent", "update", {
        analytics_storage: choice.analytics ? "granted" : "denied",
        ad_storage: choice.advertising ? "granted" : "denied",
        ad_user_data: choice.advertising ? "granted" : "denied",
        ad_personalization: choice.advertising ? "granted" : "denied"
      }]);
      // Non-Google tags (e.g. a GTM-hosted LinkedIn Insight Tag) can gate on this event.
      window.dataLayer.push({ event: "swf_consent", analytics_consent: !!choice.analytics, ad_consent: !!choice.advertising });
    }
  }

  function applyZarazConsent(choice) {
    var tries = 0;
    (function attempt() {
      if (window.zaraz && zaraz.consent) {
        try {
          if (CONSENT_PURPOSES.analytics || CONSENT_PURPOSES.advertising) {
            var map = {};
            if (CONSENT_PURPOSES.analytics) map[CONSENT_PURPOSES.analytics] = !!choice.analytics;
            if (CONSENT_PURPOSES.advertising) map[CONSENT_PURPOSES.advertising] = !!choice.advertising;
            zaraz.consent.set(map);
          } else {
            zaraz.consent.setAll(!!(choice.analytics && choice.advertising));
          }
          if (typeof zaraz.consent.sendQueuedEvents === "function") zaraz.consent.sendQueuedEvents();
        } catch (_e) {}
        return;
      }
      if (tries++ < 20) setTimeout(attempt, 250);
    })();
  }

  function waitForZaraz(cb) {
    var tries = 0;
    (function attempt() {
      if (window.zaraz && zaraz.consent) return cb(true);
      if (tries++ < 20) return setTimeout(attempt, 250);
      return cb(false);
    })();
  }

  function injectConsentStyles() {
    if (document.getElementById("swf-consent-style")) return;
    var css = [
      ".swf-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;",
      "max-width:520px;margin-left:auto;background:var(--surface,#0e1a2c);color:var(--text,#e8fbf8);",
      "border:1px solid var(--border,rgba(255,255,255,.14));border-radius:16px;",
      "box-shadow:0 18px 48px rgba(0,0,0,.45);padding:20px 20px 16px;font-family:inherit;",
      "transform:translateY(140%);opacity:0;transition:transform .35s ease,opacity .35s ease;}",
      ".swf-consent.is-open{transform:translateY(0);opacity:1;}",
      ".swf-consent h2{font-size:1.05rem;margin:0 0 6px;}",
      ".swf-consent p{font-size:.9rem;line-height:1.5;margin:0 0 14px;color:var(--muted,#a8c3cd);}",
      ".swf-consent a{color:var(--primary,#2fd4c6);}",
      ".swf-consent__row{display:flex;flex-wrap:wrap;gap:8px;}",
      ".swf-consent__btn{font:inherit;font-weight:700;font-size:.85rem;cursor:pointer;border-radius:10px;",
      "padding:10px 16px;border:1px solid var(--border,rgba(255,255,255,.2));background:transparent;color:var(--text,#e8fbf8);}",
      ".swf-consent__btn--primary{background:var(--primary,#2fd4c6);border-color:var(--primary,#2fd4c6);color:#04231f;}",
      ".swf-consent__btn--ghost{opacity:.85;}",
      ".swf-consent__prefs{margin:2px 0 12px;display:none;}",
      ".swf-consent__prefs.is-open{display:block;}",
      ".swf-consent__pref{display:flex;align-items:flex-start;gap:10px;font-size:.85rem;margin:8px 0;color:var(--text,#e8fbf8);}",
      ".swf-consent__pref input{margin-top:3px;}",
      "@media(max-width:600px){.swf-consent{left:10px;right:10px;bottom:10px;}}"
    ].join("");
    var style = document.createElement("style");
    style.id = "swf-consent-style";
    style.textContent = css;
    document.head.appendChild(style);
  }

  function renderConsentBanner(forceOpen) {
    var existing = document.getElementById("swf-consent");
    if (existing) { existing.classList.add("is-open"); return; }
    injectConsentStyles();
    var stored = readConsent() || { analytics: false, advertising: false };
    var el = document.createElement("div");
    el.id = "swf-consent";
    el.className = "swf-consent";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", "Cookie consent");
    el.innerHTML =
      '<h2>Your privacy</h2>' +
      '<p>We use analytics and (for our LinkedIn ads) advertising cookies to see what works. Essential site functions always run. See our <a href="/privacy/">privacy policy</a>.</p>' +
      '<div class="swf-consent__prefs" id="swfPrefs">' +
        '<label class="swf-consent__pref"><input type="checkbox" id="swfAnalytics"' + (stored.analytics ? " checked" : "") + '><span><strong>Analytics</strong> &mdash; anonymous usage stats (Google Analytics).</span></label>' +
        '<label class="swf-consent__pref"><input type="checkbox" id="swfAds"' + (stored.advertising ? " checked" : "") + '><span><strong>Marketing</strong> &mdash; measure &amp; improve our LinkedIn ads (LinkedIn Insight Tag).</span></label>' +
      '</div>' +
      '<div class="swf-consent__row">' +
        '<button class="swf-consent__btn swf-consent__btn--primary" id="swfAcceptAll" type="button">Accept all</button>' +
        '<button class="swf-consent__btn" id="swfReject" type="button">Reject non-essential</button>' +
        '<button class="swf-consent__btn swf-consent__btn--ghost" id="swfManage" type="button" aria-expanded="false">Manage</button>' +
        '<button class="swf-consent__btn swf-consent__btn--ghost" id="swfSave" type="button" style="display:none;">Save choices</button>' +
      '</div>';
    document.body.appendChild(el);
    // setTimeout (not requestAnimationFrame) so the reveal still fires in a
    // background/inactive tab, where rAF is paused.
    setTimeout(function () { el.classList.add("is-open"); }, 20);

    function choose(choice) {
      saveConsent(choice);
      applyConsent(choice, true);
      el.classList.remove("is-open");
      setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 400);
    }
    el.querySelector("#swfAcceptAll").addEventListener("click", function () {
      choose({ analytics: true, advertising: true });
    });
    el.querySelector("#swfReject").addEventListener("click", function () {
      choose({ analytics: false, advertising: false });
    });
    el.querySelector("#swfManage").addEventListener("click", function () {
      var prefs = el.querySelector("#swfPrefs");
      var save = el.querySelector("#swfSave");
      var open = prefs.classList.toggle("is-open");
      this.setAttribute("aria-expanded", open ? "true" : "false");
      save.style.display = open ? "" : "none";
    });
    el.querySelector("#swfSave").addEventListener("click", function () {
      choose({
        analytics: el.querySelector("#swfAnalytics").checked,
        advertising: el.querySelector("#swfAds").checked
      });
    });
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
