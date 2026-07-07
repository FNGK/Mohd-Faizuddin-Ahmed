/* Enterprise 3D hero — an interactive WebGL globe (self-hosted Three.js).
   Progressive enhancement on every device: desktop and mobile both render
   the globe, with mobile tuned lighter (fewer particles, capped DPR, larger
   label pills, horizontal-only drag so page scroll is never trapped).
   Reduced-motion, save-data, very-low-memory, and no-WebGL users keep the
   lightweight fallback. Concept ties to the offer: global reach,
   connections lighting up a network. */
(function () {
  "use strict";

  var viz = document.querySelector("[data-hero-viz]");
  var canvas = document.querySelector("[data-hero-globe]");
  if (!viz || !canvas) return;

  var mq = window.matchMedia;
  var reduce = mq && mq("(prefers-reduced-motion: reduce)").matches;
  var coarse = !(mq && mq("(pointer: fine)").matches);
  var conn = navigator.connection || {};
  var lowData = conn.saveData || /2g/.test(conn.effectiveType || "");
  var veryLowMem = navigator.deviceMemory && navigator.deviceMemory < 2;

  function webglOK() {
    try {
      var c = document.createElement("canvas");
      return !!(window.WebGLRenderingContext && (c.getContext("webgl") || c.getContext("experimental-webgl")));
    } catch (e) { return false; }
  }

  // Gate: accessibility and genuinely-constrained devices keep the fallback.
  if (reduce || lowData || veryLowMem || !webglOK()) return;

  import("./vendor/three.module.min.js").then(function (THREE) {
    build(THREE);
  }).catch(function (err) {
    viz.classList.remove("is-3d"); // restore fallback on any failure
    if (window.console && console.warn) console.warn("hero-globe fallback:", err && err.message ? err.message : err);
  });

  function build(THREE) {
    // Reveal the 3D viewport first so the container takes its real
    // (mobile min-height) size before the canvas is measured.
    viz.classList.add("is-3d");
    var W = viz.clientWidth, H = viz.clientHeight;
    if (W < 40 || H < 40) { viz.classList.remove("is-3d"); return; }

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: !coarse, alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, coarse ? 1.75 : 2));
    renderer.setSize(W, H, false);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 100);
    camera.position.set(0, 0, 3.2);

    var globe = new THREE.Group();
    scene.add(globe);

    var TEAL = new THREE.Color(0x2fd4c6);
    var R = 1;

    // --- Opaque core so back-facing points are occluded (reads as a solid sphere) ---
    var core = new THREE.Mesh(
      new THREE.SphereGeometry(R * 0.985, 48, 48),
      new THREE.MeshBasicMaterial({ color: 0x061320 })
    );
    globe.add(core);

    // --- Point-cloud globe (Fibonacci sphere) ---
    var COUNT = coarse ? 1500 : 2400;
    var positions = new Float32Array(COUNT * 3);
    var golden = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < COUNT; i++) {
      var y = 1 - (i / (COUNT - 1)) * 2;
      var r = Math.sqrt(1 - y * y);
      var theta = golden * i;
      positions[i * 3] = Math.cos(theta) * r * R;
      positions[i * 3 + 1] = y * R;
      positions[i * 3 + 2] = Math.sin(theta) * r * R;
    }
    var pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    var dot = makeDotTexture(THREE);
    var points = new THREE.Points(pGeo, new THREE.PointsMaterial({
      color: TEAL, size: 0.028, map: dot, transparent: true, opacity: 0.9,
      depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true
    }));
    globe.add(points);

    // --- Faint wireframe shell ---
    var wire = new THREE.LineSegments(
      new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(R * 1.004, 3)),
      new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.08 })
    );
    globe.add(wire);

    // --- Atmosphere glow (fresnel rim, additive) ---
    var atmo = new THREE.Mesh(
      new THREE.SphereGeometry(R * 1.18, 48, 48),
      new THREE.ShaderMaterial({
        transparent: true, blending: THREE.AdditiveBlending, side: THREE.BackSide, depthWrite: false,
        vertexShader: "varying vec3 vN; void main(){ vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
        fragmentShader: "varying vec3 vN; void main(){ float i = pow(0.62 - dot(vN, vec3(0.0,0.0,1.0)), 3.0); i = clamp(i, 0.0, 1.0); gl_FragColor = vec4(0.18,0.83,0.78,1.0) * i; }"
      })
    );
    scene.add(atmo);

    // --- Connection arcs with traveling pulses ---
    var arcs = [];
    function randSurface() {
      var u = Math.random(), v = Math.random();
      var th = 2 * Math.PI * u, ph = Math.acos(2 * v - 1);
      return new THREE.Vector3(Math.sin(ph) * Math.cos(th), Math.cos(ph), Math.sin(ph) * Math.sin(th)).multiplyScalar(R);
    }
    for (var a = 0; a < 6; a++) {
      var s = randSurface(), e = randSurface();
      var mid = s.clone().add(e).multiplyScalar(0.5).normalize().multiplyScalar(R * (1.28 + Math.random() * 0.18));
      var curve = new THREE.QuadraticBezierCurve3(s, mid, e);
      var pts = curve.getPoints(50);
      var line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.32, blending: THREE.AdditiveBlending })
      );
      globe.add(line);
      var pulseGeo = new THREE.BufferGeometry();
      pulseGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(3), 3));
      var pulse = new THREE.Points(pulseGeo, new THREE.PointsMaterial({
        color: 0xeafffb, size: 0.06, map: dot, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending
      }));
      globe.add(pulse);
      arcs.push({ curve: curve, pulse: pulse, t: Math.random(), speed: 0.0025 + Math.random() * 0.0035 });
    }

    // --- Orbiting service terms: the offer, written into the scene.
    //     One term per orbit. Every orbit is a "latitude" ring on the same
    //     tilted axis: parallel planes with >= 0.14 vertical spacing, so no
    //     two labels can ever meet — regardless of speed or direction.
    //     Longest labels take the high-latitude (smaller-radius) rings so
    //     nothing clips the camera frame. Sprites depth-test against the
    //     opaque core, so labels genuinely pass behind the globe. ---
    var TERMS = [ // ordered longest -> shortest
      "Core Web Vitals", "Technical SEO", "Shopify Plus", "Paid Media",
      "WordPress", "3D / WebGL", "AEO + GEO", "hreflang",
      "Magento", "Next.js", "GA4", "CRO"
    ];
    var ORBIT_R = 1.42;
    var tiltGroup = new THREE.Group();
    tiltGroup.rotation.x = 0.30;
    tiltGroup.rotation.z = 0.10;
    scene.add(tiltGroup);
    var orbits = [];
    for (var ti = 0; ti < TERMS.length; ti++) {
      var label = makeLabelTexture(TERMS[ti]);
      var tex = new THREE.CanvasTexture(label.canvas);
      tex.minFilter = THREE.LinearFilter;
      tex.anisotropy = 2;
      var sprite = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tex, transparent: true, depthTest: true, depthWrite: false, opacity: 0.92
      }));
      var hWorld = coarse ? 0.105 : 0.08; // larger pills for small screens
      sprite.scale.set(hWorld * (label.w / label.h), hWorld, 1);

      // Unique latitude per term: alternate hemispheres from the poles in,
      // 0.14 apart (> pill height), longest labels at highest |y|.
      var slot = Math.floor(ti / 2);
      var y = (0.77 - slot * 0.14) * (ti % 2 === 0 ? 1 : -1);
      var r = Math.sqrt(ORBIT_R * ORBIT_R - y * y);

      var ring = new THREE.Group();
      sprite.position.set(r, y, 0);
      ring.add(sprite);
      ring.rotation.y = ti * 2.4; // spread starting phases
      tiltGroup.add(ring);
      orbits.push({ ring: ring, speed: (0.0014 + (ti % 5) * 0.0004) * (ti % 2 === 0 ? 1 : -1) });
    }

    globe.rotation.x = 0.32;

    // --- Interaction: drag to rotate + inertia + idle auto-rotate.
    //     On touch devices only horizontal drags rotate (pan-y), so a
    //     thumb over the globe still scrolls the page vertically. ---
    var dragging = false, lastX = 0, lastY = 0, velX = 0.0018, velY = 0;
    canvas.style.touchAction = coarse ? "pan-y" : "none";
    canvas.addEventListener("pointerdown", function (e) { dragging = true; lastX = e.clientX; lastY = e.clientY; velX = velY = 0; viz.classList.add("is-grabbing"); });
    window.addEventListener("pointerup", function () { dragging = false; viz.classList.remove("is-grabbing"); });
    window.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - lastX, dy = e.clientY - lastY;
      lastX = e.clientX; lastY = e.clientY;
      velY = dx * 0.005; velX = coarse ? 0 : dy * 0.005;
      globe.rotation.y += velY; globe.rotation.x += velX;
    });

    // --- Pause when off-screen / tab hidden ---
    var running = true, rafId = null;
    var io = new IntersectionObserver(function (en) { running = en[0].isIntersecting; if (running) start(); else stop(); }, { threshold: 0.01 });
    io.observe(viz);
    document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });

    var tmp = new THREE.Vector3();
    function frame() {
      if (!dragging) {
        velY += (0.0018 - velY) * 0.02; // ease back to gentle auto-spin
        globe.rotation.y += velY;
        globe.rotation.x += velX;
        velX *= 0.94;
        globe.rotation.x += (0.32 - globe.rotation.x) * 0.02; // settle tilt
      }
      for (var o = 0; o < orbits.length; o++) {
        orbits[o].ring.rotation.y += orbits[o].speed;
      }
      for (var k = 0; k < arcs.length; k++) {
        arcs[k].t += arcs[k].speed;
        if (arcs[k].t > 1) arcs[k].t -= 1;
        arcs[k].curve.getPoint(arcs[k].t, tmp);
        var pos = arcs[k].pulse.geometry.attributes.position;
        pos.array[0] = tmp.x; pos.array[1] = tmp.y; pos.array[2] = tmp.z;
        pos.needsUpdate = true;
        arcs[k].pulse.position.copy(globe.position);
        arcs[k].pulse.rotation.copy(globe.rotation);
      }
      renderer.render(scene, camera);
      rafId = requestAnimationFrame(frame);
    }
    function start() { if (!rafId && running && !document.hidden) rafId = requestAnimationFrame(frame); }
    function stop() { if (rafId) { cancelAnimationFrame(rafId); rafId = null; } }

    function resize() {
      var w = viz.clientWidth, h = viz.clientHeight;
      if (!w || !h) return;
      camera.aspect = w / h; camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
    var rt;
    window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(resize, 150); }, { passive: true });

    start();
  }

  function makeLabelTexture(text) {
    var dpr = 2;
    var padX = 18, h = 44;
    var c = document.createElement("canvas");
    var ctx = c.getContext("2d");
    ctx.font = "600 22px 'Hanken Grotesk', 'Segoe UI', Arial, sans-serif";
    var w = Math.ceil(ctx.measureText(text).width) + padX * 2;
    c.width = w * dpr; c.height = h * dpr;
    ctx = c.getContext("2d");
    ctx.scale(dpr, dpr);
    // glass pill
    var r = h / 2;
    ctx.beginPath();
    ctx.moveTo(r, 0); ctx.lineTo(w - r, 0); ctx.arc(w - r, r, r, -Math.PI / 2, Math.PI / 2);
    ctx.lineTo(r, h); ctx.arc(r, r, r, Math.PI / 2, -Math.PI / 2);
    ctx.closePath();
    ctx.fillStyle = "rgba(8, 24, 40, 0.78)";
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "rgba(47, 212, 198, 0.55)";
    ctx.stroke();
    // teal marker dot
    ctx.beginPath();
    ctx.arc(padX - 6, h / 2, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#2fd4c6";
    ctx.fill();
    // label
    ctx.font = "600 22px 'Hanken Grotesk', 'Segoe UI', Arial, sans-serif";
    ctx.fillStyle = "#e8fbf8";
    ctx.textBaseline = "middle";
    ctx.fillText(text, padX + 4, h / 2 + 1);
    return { canvas: c, w: w, h: h };
  }

  function makeDotTexture(THREE) {
    var s = 64, c = document.createElement("canvas");
    c.width = c.height = s;
    var ctx = c.getContext("2d");
    var g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
    g.addColorStop(0, "rgba(255,255,255,1)");
    g.addColorStop(0.35, "rgba(255,255,255,0.85)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, s, s);
    var tex = new THREE.CanvasTexture(c);
    tex.needsUpdate = true;
    return tex;
  }
})();
