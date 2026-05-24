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
