// SEO With Faiz — Google Tag Manager loader (GTM-KQ9KNHN2).
//
// The standard GTM head snippet is an INLINE <script>, which this site's
// strict CSP (script-src 'self' — no 'unsafe-inline') would block, so GTM
// would never load. This external file runs the exact same bootstrap from
// 'self', keeping the CSP intact. It ALSO sets Google Consent Mode v2
// defaults to "denied" BEFORE the container loads (the consent banner in
// site.js flips them on opt-in), and re-applies any stored choice for
// returning visitors so they aren't re-gated.
(function () {
  var w = window, d = document;
  w.dataLayer = w.dataLayer || [];
  function gtag() { w.dataLayer.push(arguments); }

  // Consent Mode v2 — deny by default until the banner grants.
  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    wait_for_update: 500
  });

  // Honor a returning visitor's saved choice immediately.
  try {
    var c = JSON.parse(localStorage.getItem("swf-consent-v1") || "null");
    if (c) {
      gtag("consent", "update", {
        analytics_storage: c.analytics ? "granted" : "denied",
        ad_storage: c.advertising ? "granted" : "denied",
        ad_user_data: c.advertising ? "granted" : "denied",
        ad_personalization: c.advertising ? "granted" : "denied"
      });
      // Non-Google tags (e.g. a GTM-hosted LinkedIn Insight Tag) can gate on this.
      w.dataLayer.push({ event: "swf_consent", analytics_consent: !!c.analytics, ad_consent: !!c.advertising });
    }
  } catch (e) {}

  // Google Tag Manager (standard snippet, externalized for CSP).
  (function (w, d, s, l, i) {
    w[l] = w[l] || [];
    w[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    var f = d.getElementsByTagName(s)[0],
      j = d.createElement(s),
      dl = l != "dataLayer" ? "&l=" + l : "";
    j.async = true;
    j.src = "https://www.googletagmanager.com/gtm.js?id=" + i + dl;
    f.parentNode.insertBefore(j, f);
  })(w, d, "script", "dataLayer", "GTM-KQ9KNHN2");
})();
