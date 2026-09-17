/* Homepage video hero.
   The still poster is a CSS background on the media box (a different crop for
   phones and desktop), so the right image paints first and is the LCP
   candidate. The video source is attached only after window load, so the page
   never waits on a video download:
   - phones get a vertical cut (whole globe in frame), larger screens the 16:9 cut
   - WebM (VP9) is preferred because it loops without a stall; MP4 is the fallback
   Both files are edited so the last frame dissolves into the first, so the loop
   has no visible jump. Reduced-motion and data-saver visitors keep the still.
   A pause control is provided because the loop runs longer than five seconds. */
(function () {
  "use strict";

  var video = document.querySelector("[data-hero-video]");
  var toggle = document.querySelector("[data-hero-video-toggle]");
  if (!video) return;

  var mq = window.matchMedia;
  var reduce = mq && mq("(prefers-reduced-motion: reduce)").matches;
  var conn = navigator.connection || {};
  var lowData = conn.saveData || /2g/.test(conn.effectiveType || "");
  if (reduce || lowData) {
    if (toggle) toggle.hidden = true;
    return;
  }

  var userPaused = false;

  function setToggle(paused) {
    if (!toggle) return;
    toggle.setAttribute("aria-pressed", paused ? "true" : "false");
    toggle.setAttribute("aria-label", paused ? "Play background video" : "Pause background video");
    toggle.classList.toggle("is-paused", paused);
  }

  function pickSource() {
    var phone = mq && mq("(max-width: 760px)").matches;
    var size = phone ? "mobile" : "desktop";
    var webm = video.canPlayType('video/webm; codecs="vp9"');
    return video.getAttribute("data-src-" + size + (webm ? "-webm" : "-mp4"));
  }

  function attach() {
    video.src = pickSource();
    video.muted = true;
    video.loop = true;
    video.addEventListener("playing", function () { video.classList.add("is-playing"); }, { once: true });
    var p = video.play();
    if (p && p.catch) p.catch(function () { setToggle(true); });
  }

  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      if (video.paused) { userPaused = false; video.play(); setToggle(false); }
      else { userPaused = true; video.pause(); setToggle(true); }
    });
  }

  // Keep looping until the visitor pauses; only suspend while the hero is
  // off-screen, and resume when it returns (unless paused by hand).
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      if (!video.currentSrc || userPaused) return;
      if (entries[0].isIntersecting) video.play(); else video.pause();
    }, { threshold: 0.05 }).observe(video);
  }

  if (document.readyState === "complete") attach();
  else window.addEventListener("load", attach, { once: true });
})();
