/**
 * Theme bootstrap — runs synchronously in <head> before first paint to avoid
 * a light->dark flash. Dark-premium is the default brand identity; an explicit
 * stored choice wins. Full theme toggle wiring lives in site.js.
 */
(function () {
  try {
    var stored = localStorage.getItem('seowithfaiz-theme');
    document.documentElement.setAttribute('data-theme', stored || 'dark');
  } catch (e) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
})();

/**
 * Redirect GitHub Pages project URLs to the canonical custom domain.
 * Loaded synchronously in <head> so visitors and crawlers reach seowithfaiz.com quickly.
 */
(function () {
  var GITHUB_HOST = 'fngk.github.io';
  var GITHUB_BASE = '/Mohd-Faizuddin-Ahmed';
  var CANONICAL_ORIGIN = 'https://seowithfaiz.com';

  if (location.hostname !== GITHUB_HOST) return;
  if (!location.pathname.startsWith(GITHUB_BASE)) return;

  var path = location.pathname.slice(GITHUB_BASE.length) || '/';
  if (path.charAt(0) !== '/') path = '/' + path;

  var target =
    CANONICAL_ORIGIN.replace(/\/$/, '') + path + location.search + location.hash;

  if (location.href === target) return;
  location.replace(target);
})();

/**
 * Google Analytics 4 (G-LQZ72RK5LM). Installed here so it loads on every page
 * via the single shared head script. Skipped on the GitHub Pages host (that
 * request is redirected to the canonical domain above, where GA4 fires cleanly).
 */
(function () {
  if (location.hostname === 'fngk.github.io') return;
  var ID = 'G-LQZ72RK5LM';
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', ID, { anonymize_ip: true });
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
  document.head.appendChild(s);
})();
