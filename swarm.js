/* Agent-swarm background.
 *
 * A fixed canvas behind every page. It is meant to read as a network of agents
 * passing messages, not as a starfield, so three things drive it:
 *
 *   depth       every node has a z, which scales its size, its brightness and
 *               how far it parallaxes with the pointer. The field has layers.
 *   flocking    nodes steer by the three boid rules (cohesion toward their
 *               swarm's centre, separation from crowding, alignment with
 *               neighbours) instead of drifting on fixed velocities.
 *   messages    a pulse travels an edge, lights the node it reaches, and that
 *               node forwards it to one of its own neighbours. Traffic
 *               cascades through the graph the way real message passing does.
 *
 * Colours come from tokens.css (--swarm-*), never from here. How far back the
 * swarm sits is a CSS concern too: the .veil layer over this canvas.
 */
(function () {
  'use strict';

  var canvas = document.getElementById('swarm');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- tuning -------------------------------------------------------------
  var LINK_RADIUS = 200;      // px: beyond this, two nodes are not neighbours
  var AREA_PER_NODE = 26000;  // px² of viewport per node
  var NODES_PER_SWARM = 13;
  var MAX_MESSAGES = 9;
  var FORWARD_CHANCE = 0.62;  // a node that receives a message relays it
  var MAX_HOPS = 5;
  var EMIT_CHANCE = 0.02;     // per frame, a fresh message enters the network
  var PARALLAX = 26;          // px of pointer parallax at the nearest depth
  var POINTER_DAMPING = 0.1;  // lerp constant, measured off monks.com

  // --- state --------------------------------------------------------------
  var width = 0, height = 0, dpr = 1;
  var nodes = [], swarms = [], messages = [];
  var pointerX = 0, pointerY = 0, easedX = 0, easedY = 0;
  var frame = null, tick = 0;
  var palette = {};

  function cssValue(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
  }

  function readPalette() {
    palette.node = cssValue('--swarm-node', '#AEB8E8');
    palette.edge = cssValue('--swarm-edge', '#7C8CFF');
    palette.signal = cssValue('--swarm-signal', '#C7D2FF');
    palette.glow = cssValue('--swarm-glow', '#26316B');
    palette.nodeAlpha = parseFloat(cssValue('--swarm-node-a', '.4'));
    palette.edgeAlpha = parseFloat(cssValue('--swarm-edge-a', '.13'));
    palette.glowAlpha = parseFloat(cssValue('--swarm-glow-a', '.42'));
  }

  function rgba(hex, alpha) {
    var h = hex.replace('#', '');
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    if (h.length !== 6) return hex;
    var n = parseInt(h, 16);
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + alpha + ')';
  }

  function random(min, max) { return min + Math.random() * (max - min); }

  // --- building the field -------------------------------------------------
  function build() {
    var count = Math.max(34, Math.min(88, Math.round(width * height / AREA_PER_NODE)));
    var swarmCount = Math.max(3, Math.round(count / NODES_PER_SWARM));

    swarms = [];
    for (var s = 0; s < swarmCount; s++) {
      swarms.push({
        x: random(0.1, 0.9) * width,
        y: random(0.12, 0.88) * height,
        driftX: random(-0.05, 0.05),
        driftY: random(-0.04, 0.04)
      });
    }

    nodes = [];
    for (var i = 0; i < count; i++) {
      var swarm = swarms[i % swarmCount];
      var angle = random(0, Math.PI * 2);
      var spread = random(40, 200);
      var isHub = i < swarmCount;
      // Hubs sit near the front of the field; leaves scatter through its depth.
      var z = isHub ? random(0.8, 1) : random(0.35, 0.95);
      nodes.push({
        index: i, swarm: swarm, z: z, hub: isHub,
        x: swarm.x + Math.cos(angle) * spread,
        y: swarm.y + Math.sin(angle) * spread,
        vx: random(-0.1, 0.1), vy: random(-0.1, 0.1),
        radius: (isHub ? random(3.2, 4.4) : random(1, 2.2)) * z,
        phase: random(0, Math.PI * 2),   // offsets each hub's breathing
        energy: 0,                        // lights up on receiving a message
        neighbours: []
      });
    }
  }

  function resize() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    pointerX = easedX = width / 2;
    pointerY = easedY = height / 2;
    build();
  }

  // --- messages -----------------------------------------------------------
  function sendMessage(from, hops) {
    if (messages.length >= MAX_MESSAGES || !from.neighbours.length) return;
    var to = from.neighbours[(Math.random() * from.neighbours.length) | 0];
    messages.push({ from: from, to: to, t: 0, speed: random(0.007, 0.014), hops: hops });
  }

  function emitMessage() {
    // Hubs originate most traffic, which is what makes the graph read as a
    // network with coordinators rather than a uniform mesh.
    var pool = Math.random() < 0.7 ? nodes.filter(function (n) { return n.hub; }) : nodes;
    if (!pool.length) return;
    sendMessage(pool[(Math.random() * pool.length) | 0], 0);
  }

  // --- simulation ---------------------------------------------------------
  /* One pass over every pair: it fills each node's neighbour list, applies
     separation and alignment, and leaves the distances the renderer needs. */
  function relate() {
    var i, node;
    for (i = 0; i < nodes.length; i++) nodes[i].neighbours.length = 0;

    for (i = 0; i < nodes.length; i++) {
      var a = nodes[i];
      for (var j = i + 1; j < nodes.length; j++) {
        var b = nodes[j];
        var dx = a.x - b.x, dy = a.y - b.y;
        var squared = dx * dx + dy * dy;
        if (squared > LINK_RADIUS * LINK_RADIUS || squared === 0) continue;

        a.neighbours.push(b);
        b.neighbours.push(a);

        var distance = Math.sqrt(squared);
        // separation: crowding pushes apart, and only at close range
        if (distance < 46) {
          var push = (46 - distance) / 46 * 0.012;
          a.vx += dx / distance * push; a.vy += dy / distance * push;
          b.vx -= dx / distance * push; b.vy -= dy / distance * push;
        }
        // alignment: neighbours gradually agree on a heading
        var blend = 0.0016;
        var avx = (a.vx + b.vx) * 0.5, avy = (a.vy + b.vy) * 0.5;
        a.vx += (avx - a.vx) * blend; a.vy += (avy - a.vy) * blend;
        b.vx += (avx - b.vx) * blend; b.vy += (avy - b.vy) * blend;
      }
    }

    for (i = 0; i < nodes.length; i++) {
      node = nodes[i];
      // cohesion: a weak spring home, so a swarm stays a swarm
      node.vx += (node.swarm.x - node.x) * 0.00005;
      node.vy += (node.swarm.y - node.y) * 0.00005;
      node.vx *= 0.994;
      node.vy *= 0.994;
      // depth: distant nodes move more slowly, which is what sells the layers
      node.x += node.vx * node.z;
      node.y += node.vy * node.z;
      node.energy *= 0.94;

      if (node.x < -80) node.x = width + 80;
      if (node.x > width + 80) node.x = -80;
      if (node.y < -80) node.y = height + 80;
      if (node.y > height + 80) node.y = -80;
    }

    for (i = 0; i < swarms.length; i++) {
      var swarm = swarms[i];
      swarm.x += swarm.driftX;
      swarm.y += swarm.driftY;
      if (swarm.x < 0 || swarm.x > width) swarm.driftX *= -1;
      if (swarm.y < 0 || swarm.y > height) swarm.driftY *= -1;
    }

    for (i = messages.length - 1; i >= 0; i--) {
      var message = messages[i];
      message.t += message.speed;
      if (message.t < 1) continue;
      message.to.energy = 1;                       // the node lights up
      if (message.hops < MAX_HOPS && Math.random() < FORWARD_CHANCE) {
        sendMessage(message.to, message.hops + 1); // and relays it onward
      }
      messages.splice(i, 1);
    }

    if (Math.random() < EMIT_CHANCE) emitMessage();

    easedX += (pointerX - easedX) * POINTER_DAMPING;
    easedY += (pointerY - easedY) * POINTER_DAMPING;
    tick++;
  }

  // --- rendering ----------------------------------------------------------
  function offsetX(node) { return (easedX - width / 2) / width * PARALLAX * node.z; }
  function offsetY(node) { return (easedY - height / 2) / height * PARALLAX * node.z; }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    // the soft light source the field sits in
    var gx = width * 0.72, gy = height * 0.34, gr = Math.max(width, height) * 0.55;
    var glow = ctx.createRadialGradient(gx, gy, 0, gx, gy, gr);
    glow.addColorStop(0, rgba(palette.glow, palette.glowAlpha));
    glow.addColorStop(1, rgba(palette.glow, 0));
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, width, height);

    var i, j, a, b, ax, ay, bx, by;

    // edges, faded by distance and by the depth of the shallower endpoint
    for (i = 0; i < nodes.length; i++) {
      a = nodes[i];
      ax = a.x + offsetX(a); ay = a.y + offsetY(a);
      for (j = 0; j < a.neighbours.length; j++) {
        b = a.neighbours[j];
        if (b.index < a.index) continue;              // each pair drawn once
        bx = b.x + offsetX(b); by = b.y + offsetY(b);
        var dx = ax - bx, dy = ay - by;
        var distance = Math.sqrt(dx * dx + dy * dy);
        if (distance > LINK_RADIUS) continue;
        var falloff = 1 - distance / LINK_RADIUS;
        var depth = Math.min(a.z, b.z);
        var live = Math.max(a.energy, b.energy);
        ctx.strokeStyle = live > 0.05
          ? rgba(palette.signal, palette.edgeAlpha * falloff * falloff * depth + live * 0.25)
          : rgba(palette.edge, palette.edgeAlpha * falloff * falloff * depth);
        ctx.lineWidth = (a.hub || b.hub ? 1 : 0.7) * depth;
        ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
      }
    }

    // nodes
    for (i = 0; i < nodes.length; i++) {
      a = nodes[i];
      ax = a.x + offsetX(a); ay = a.y + offsetY(a);
      // hubs breathe slowly, so the network never looks frozen between messages
      var breathe = a.hub ? 1 + Math.sin(tick * 0.012 + a.phase) * 0.12 : 1;
      var radius = a.radius * breathe;

      if (a.hub || a.energy > 0.05) {
        var halo = radius * (a.hub ? 6 : 5) * (1 + a.energy);
        var ring = ctx.createRadialGradient(ax, ay, 0, ax, ay, halo);
        ring.addColorStop(0, rgba(palette.signal, (0.22 * a.z + a.energy * 0.45)));
        ring.addColorStop(1, rgba(palette.signal, 0));
        ctx.fillStyle = ring;
        ctx.beginPath(); ctx.arc(ax, ay, halo, 0, 6.2832); ctx.fill();
      }

      var alpha = palette.nodeAlpha * (a.hub ? 1 : 0.8) * a.z + a.energy * 0.4;
      ctx.fillStyle = rgba(a.hub || a.energy > 0.3 ? palette.signal : palette.node, alpha);
      ctx.beginPath(); ctx.arc(ax, ay, radius, 0, 6.2832); ctx.fill();
    }

    // messages in flight: a bright head with a short trail behind it
    for (i = 0; i < messages.length; i++) {
      var m = messages[i];
      var fx = m.from.x + offsetX(m.from), fy = m.from.y + offsetY(m.from);
      var tx = m.to.x + offsetX(m.to), ty = m.to.y + offsetY(m.to);
      var x = fx + (tx - fx) * m.t, y = fy + (ty - fy) * m.t;
      var trailT = Math.max(0, m.t - 0.22);
      var fade = Math.sin(m.t * Math.PI);

      var trail = ctx.createLinearGradient(fx + (tx - fx) * trailT, fy + (ty - fy) * trailT, x, y);
      trail.addColorStop(0, rgba(palette.signal, 0));
      trail.addColorStop(1, rgba(palette.signal, 0.5 * fade));
      ctx.strokeStyle = trail;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.moveTo(fx + (tx - fx) * trailT, fy + (ty - fy) * trailT);
      ctx.lineTo(x, y);
      ctx.stroke();

      var head = ctx.createRadialGradient(x, y, 0, x, y, 9);
      head.addColorStop(0, rgba(palette.signal, 0.8 * fade));
      head.addColorStop(1, rgba(palette.signal, 0));
      ctx.fillStyle = head;
      ctx.beginPath(); ctx.arc(x, y, 9, 0, 6.2832); ctx.fill();
      ctx.fillStyle = rgba(palette.signal, 0.95 * fade);
      ctx.beginPath(); ctx.arc(x, y, 1.6, 0, 6.2832); ctx.fill();
    }
  }

  function step() {
    relate();
    draw();
    frame = requestAnimationFrame(step);
  }

  function start() { if (!frame && !reducedMotion) frame = requestAnimationFrame(step); }
  function stop() { if (frame) { cancelAnimationFrame(frame); frame = null; } }

  // --- boot ---------------------------------------------------------------
  readPalette();
  resize();
  relate();
  draw();               // one static frame, which is all reduced motion gets
  start();

  addEventListener('resize', function () { resize(); relate(); draw(); }, { passive: true });
  addEventListener('pointermove', function (event) {
    pointerX = event.clientX;
    pointerY = event.clientY;
  }, { passive: true });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();   // no work while the tab is hidden
  });
})();
