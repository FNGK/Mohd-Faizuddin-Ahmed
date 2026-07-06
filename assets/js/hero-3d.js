/* Elite 3D hero: pointer-driven tilt + lightweight particle constellation.
   Zero dependencies. GPU-friendly, capped node counts, paused when the hero
   is off-screen or the tab is hidden, and fully frozen under reduced motion. */
(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia && window.matchMedia("(pointer: fine)").matches;

  var hero = document.querySelector(".hero-3d");
  var scene = document.querySelector("[data-hero-scene]");
  var panel = document.querySelector("[data-hero-tilt]");
  var canvas = document.querySelector("[data-hero-canvas]");
  if (!hero) return;

  var pointer = { x: -9999, y: -9999 };

  /* ---------- 1. Pointer-driven 3D tilt on the console ---------- */
  if (panel && scene && !reduce && finePointer) {
    var MAX = 6; // degrees
    var rafTilt = null, rx = 0, ry = 0;

    var onMove = function (e) {
      var r = scene.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      ry = px * MAX * 2;
      rx = -py * MAX * 2;
      pointer.x = e.clientX - r.left;
      pointer.y = e.clientY - r.top;
      if (!rafTilt) rafTilt = requestAnimationFrame(applyTilt);
    };
    var onLeave = function () {
      rx = 0; ry = 0;
      pointer.x = -9999; pointer.y = -9999;
      if (!rafTilt) rafTilt = requestAnimationFrame(applyTilt);
    };
    function applyTilt() {
      rafTilt = null;
      panel.style.setProperty("--rx", rx.toFixed(2) + "deg");
      panel.style.setProperty("--ry", ry.toFixed(2) + "deg");
    }
    scene.addEventListener("pointermove", onMove);
    scene.addEventListener("pointerleave", onLeave);
  }

  /* ---------- 2. Particle constellation ---------- */
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var nodes = [], w = 0, h = 0;
  var rafId = null, visible = true, resizeTimer = null;

  function nodeCount() {
    var vw = window.innerWidth;
    if (vw < 640) return 26;
    if (vw < 1024) return 44;
    return 66;
  }
  function linkDist() { return window.innerWidth < 640 ? 92 : 132; }

  function resize() {
    var r = canvas.getBoundingClientRect();
    w = r.width; h = r.height;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function seed() {
    nodes = [];
    for (var i = 0, n = nodeCount(); i < n; i++) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.24,
        vy: (Math.random() - 0.5) * 0.24,
        r: Math.random() * 1.5 + 0.8
      });
    }
  }
  function teal(a) { return "rgba(47,212,198," + a + ")"; }

  function draw(animate) {
    ctx.clearRect(0, 0, w, h);
    var maxD = linkDist();

    if (animate) {
      for (var i = 0; i < nodes.length; i++) {
        var p = nodes[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > w) p.vx *= -1;
        if (p.y < 0 || p.y > h) p.vy *= -1;
        var ex = p.x - pointer.x, ey = p.y - pointer.y;
        var ed = Math.sqrt(ex * ex + ey * ey);
        if (ed < 110 && ed > 0.01) { p.x += (ex / ed) * 0.5; p.y += (ey / ed) * 0.5; }
      }
    }

    for (var a = 0; a < nodes.length; a++) {
      for (var b = a + 1; b < nodes.length; b++) {
        var dx = nodes[a].x - nodes[b].x, dy = nodes[a].y - nodes[b].y;
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < maxD) {
          ctx.strokeStyle = teal(0.16 * (1 - d / maxD));
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(nodes[a].x, nodes[a].y);
          ctx.lineTo(nodes[b].x, nodes[b].y);
          ctx.stroke();
        }
      }
    }
    for (var k = 0; k < nodes.length; k++) {
      ctx.fillStyle = teal(0.7);
      ctx.beginPath();
      ctx.arc(nodes[k].x, nodes[k].y, nodes[k].r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function loop() {
    draw(true);
    rafId = requestAnimationFrame(loop);
  }
  function start() {
    if (rafId || !visible || document.hidden) return;
    rafId = requestAnimationFrame(loop);
  }
  function stop() {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
  }

  resize();
  seed();

  if (reduce) {
    draw(false); // one static frame — still an elegant graphic, no motion
  } else {
    start();

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) start(); else stop();
      }, { threshold: 0.01 }).observe(hero);
    }
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { resize(); seed(); if (reduce) draw(false); }, 180);
    }, { passive: true });
  }
})();
