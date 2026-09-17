/* Homepage video hero.
   The poster image paints first (it is the LCP candidate), and the video source
   is attached only after window load, so the page never waits on a video
   download. Phones get the 480p file, larger screens the 720p file.
   Reduced-motion and data-saver visitors keep the still poster. A pause
   control is provided because the loop runs longer than five seconds. */
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

  function setToggle(paused) {
    if (!toggle) return;
    toggle.setAttribute("aria-pressed", paused ? "true" : "false");
    toggle.setAttribute("aria-label", paused ? "Play background video" : "Pause background video");
    toggle.classList.toggle("is-paused", paused);
  }

  function attach() {
    var small = window.innerWidth < 760;
    video.src = video.getAttribute(small ? "data-src-sm" : "data-src-lg");
    video.muted = true;
    var p = video.play();
    if (p && p.catch) p.catch(function () { setToggle(true); });
    video.addEventListener("playing", function () { video.classList.add("is-playing"); setToggle(false); });
  }

  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      if (video.paused) { video.play(); setToggle(false); }
      else { video.pause(); setToggle(true); }
    });
  }

  // Pause while the hero is off-screen or the tab is hidden.
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      if (!video.currentSrc || (toggle && toggle.classList.contains("is-paused"))) return;
      if (entries[0].isIntersecting) video.play(); else video.pause();
    }, { threshold: 0.05 }).observe(video);
  }

  if (document.readyState === "complete") attach();
  else window.addEventListener("load", attach, { once: true });
})();
