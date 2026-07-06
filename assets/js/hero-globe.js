/* Enterprise 3D hero — an interactive WebGL globe (self-hosted Three.js).
   Progressive enhancement: only capable desktops load Three and render the
   globe. Phones, reduced-motion, save-data, and no-WebGL users keep the
   lightweight fallback, so the "Lighthouse 95+" promise holds everywhere.
   Concept ties to the offer: global reach, connections lighting up a network. */
(function () {
  "use strict";

  var viz = document.querySelector("[data-hero-viz]");
  var canvas = document.querySelector("[data-hero-globe]");
  if (!viz || !canvas) return;

  var mq = window.matchMedia;
  var reduce = mq && mq("(prefers-reduced-motion: reduce)").matches;
  var finePointer = mq && mq("(pointer: fine)").matches;
  var wideEnough = window.innerWidth >= 900;
  var conn = navigator.connection || {};
  var lowData = conn.saveData || /2g/.test(conn.effectiveType || "");
  var lowMem = navigator.deviceMemory && navigator.deviceMemory < 4;

  function webglOK() {
    try {
      var c = document.createElement("canvas");
      return !!(window.WebGLRenderingContext && (c.getContext("webgl") || c.getContext("experimental-webgl")));
    } catch (e) { return false; }
  }

  // Gate: only enhance where it will look and perform great.
  if (reduce || !finePointer || !wideEnough || lowData || lowMem || !webglOK()) return;

  import("./vendor/three.module.min.js").then(function (THREE) {
    build(THREE);
  }).catch(function () { /* keep fallback */ });

  function build(THREE) {
    var W = viz.clientWidth, H = viz.clientHeight;
    if (W < 40 || H < 40) return;

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(W, H, false);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 100);
    camera.position.set(0, 0, 2.9);

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
    var COUNT = 2400;
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

    globe.rotation.x = 0.32;

    // --- Interaction: drag to rotate + inertia + idle auto-rotate ---
    var dragging = false, lastX = 0, lastY = 0, velX = 0.0018, velY = 0;
    canvas.style.touchAction = "none";
    canvas.addEventListener("pointerdown", function (e) { dragging = true; lastX = e.clientX; lastY = e.clientY; velX = velY = 0; viz.classList.add("is-grabbing"); });
    window.addEventListener("pointerup", function () { dragging = false; viz.classList.remove("is-grabbing"); });
    window.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - lastX, dy = e.clientY - lastY;
      lastX = e.clientX; lastY = e.clientY;
      velY = dx * 0.005; velX = dy * 0.005;
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

    // Success: reveal the globe, hide the fallback.
    viz.classList.add("is-3d");
    start();
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
