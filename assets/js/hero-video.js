/* Homepage video hero.
   The still poster is a CSS background on the media box (a different crop for
   phones and desktop), so the right image paints first and is the LCP
   candidate. The video source is attached once the page is idle after load,
   so the page never waits on a video download:
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

  var inView = true;
  // Tracked by hand: video.currentSrc stays empty until the next task after src is set.
  var attached = false;

  // The button follows what the video is actually doing, so it stays truthful
  // when the browser starts or blocks playback on its own. Suspending while the
  // hero is off-screen or the tab is hidden is not a pause the visitor chose,
  // so it leaves the button alone.
  video.addEventListener("playing", function () {
    video.classList.add("is-playing");
    setToggle(false);
  });
  video.addEventListener("pause", function () {
    if (inView && !document.hidden) setToggle(true);
  });

  // Play unless the visitor paused by hand, the hero is off-screen or the tab
  // is hidden. A refused play (e.g. a tab opened in the background) is retried
  // when the tab becomes visible.
  function resume() {
    if (!attached || userPaused || !inView || document.hidden) return;
    var p = video.play();
    if (p && p.catch) p.catch(function () { setToggle(true); });
  }

  function attach() {
    video.src = pickSource();
    video.muted = true;
    video.loop = true;
    attached = true;
    resume();
  }

  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      // clicked before the video attached: remember the choice for when it does
      if (!attached) { userPaused = !userPaused; setToggle(userPaused); return; }
      if (video.paused) { userPaused = false; resume(); }
      else { userPaused = true; video.pause(); }
    });
  }

  // Keep looping until the visitor pauses; only suspend while the hero is
  // off-screen, and resume when it returns (unless paused by hand).
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      inView = entries[0].isIntersecting;
      if (inView) resume(); else if (!video.paused) video.pause();
    }, { threshold: 0.05 }).observe(video);
  }
  document.addEventListener("visibilitychange", resume);

  // Wait for load, then for the main thread to go quiet, so the download and
  // first decode never compete with the page's own rendering. The poster is
  // already on screen, so the only visible change is the fade into motion.
  function whenIdle() {
    if ("requestIdleCallback" in window) requestIdleCallback(attach, { timeout: 2500 });
    else setTimeout(attach, 1200);
  }
  if (document.readyState === "complete") whenIdle();
  else window.addEventListener("load", whenIdle, { once: true });
})();
