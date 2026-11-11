/* BrownDust II Library: board planner.
   Place tiles on a 7x7 board, units on the tiles, gear on the units. Shows the running cost,
   checks pieces fit, and exports a ```board block for build pages. The plan lives in the URL
   (so it can be shared) and in localStorage (so it survives a reload).
   Data comes from <script id="swg-planner-data">, written by swg-build from content/. */
(function () {
  "use strict";

  var root = document.getElementById("swg-planner");
  var dataEl = document.getElementById("swg-planner-data");
  if (!root || !dataEl) return;
  var D = JSON.parse(dataEl.textContent);
  var N = D.grid || 7;
  var STORE = "swg-planner";

  var byId = { unit: {}, tile: {}, gear: {} };
  D.units.forEach(function (u) { byId.unit[u.id] = u; });
  D.tiles.forEach(function (t) { byId.tile[t.id] = t; });
  D.gear.forEach(function (g) { byId.gear[g.id] = g; });

  // ---------- shapes ----------
  function parseShape(s) {
    var cells = [];
    String(s).split("/").forEach(function (row, r) {
      row.trim().split("").forEach(function (ch, c) { if (ch === "#") cells.push([r, c]); });
    });
    return cells;
  }
  function rotate(cells, times) {
    var out = cells;
    for (var i = 0; i < ((times % 4) + 4) % 4; i++) {
      var h = Math.max.apply(null, out.map(function (p) { return p[0]; })) + 1;
      out = out.map(function (p) { return [p[1], h - 1 - p[0]]; });
    }
    var minR = Math.min.apply(null, out.map(function (p) { return p[0]; }));
    var minC = Math.min.apply(null, out.map(function (p) { return p[1]; }));
    return out.map(function (p) { return [p[0] - minR, p[1] - minC]; });
  }
  function footprint(p) {
    var def = byId[p.kind][p.id];
    return rotate(parseShape(def.shape), p.rot).map(function (c) { return [c[0] + p.r, c[1] + p.c]; });
  }
  function size(cells) {
    return [Math.max.apply(null, cells.map(function (p) { return p[0]; })) + 1,
            Math.max.apply(null, cells.map(function (p) { return p[1]; })) + 1];
  }

  // ---------- state ----------
  var state = { pieces: [], budget: "", name: "" };
  var seq = 1;
  var ui = { tab: "unit", query: "", placing: null, hover: null, selected: null, msg: "", moving: null };

  function at(kind, r, c) {
    for (var i = 0; i < state.pieces.length; i++) {
      var p = state.pieces[i];
      if (p.kind !== kind) continue;
      var f = footprint(p);
      for (var j = 0; j < f.length; j++) if (f[j][0] === r && f[j][1] === c) return p;
    }
    return null;
  }

  // Why a piece can't go here, or "" if it can.
  function problem(p) {
    var f = footprint(p);
    for (var i = 0; i < f.length; i++) {
      var r = f[i][0], c = f[i][1];
      if (r < 0 || c < 0 || r >= N || c >= N) return "It doesn't fit inside the board there.";
      var same = at(p.kind, r, c);
      if (same && same !== p) return p.kind === "tile" ? "Tiles can't overlap." : "Units can't overlap.";
      if (p.kind === "unit" && !at("tile", r, c)) return "A unit needs a tile under every square. Place tiles first.";
    }
    return "";
  }

  function letters() {
    // Units first, then tiles, in the order they were placed. A-Z, then a-z.
    var abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    var map = new Map(), i = 0;
    state.pieces.filter(function (p) { return p.kind === "unit"; })
      .concat(state.pieces.filter(function (p) { return p.kind === "tile"; }))
      .forEach(function (p) { map.set(p, abc[i++] || "?"); });
    return map;
  }

  function cost() {
    var t = { unit: 0, tile: 0, gear: 0 };
    state.pieces.forEach(function (p) {
      t[p.kind] += byId[p.kind][p.id].price;
      (p.gear || []).forEach(function (g) { t.gear += byId.gear[g].price; });
    });
    t.total = t.unit + t.tile + t.gear;
    return t;
  }

  // Gear text says "When equipped by a Utility / Attacking / Curse Character". Which half does this unit get?
  var CHECKS = [
    // Weapons: both halves are useful, the attacker half on attackers and the other half on supports.
    { re: /Attacking Character/i, ok: function (u) { return u.tags.some(function (t) { return /Attack/.test(t); }); },
      yes: "Attacker effect", no: "Non-attacker effect", weak: false },
    // Armor and Knight's Necklace: the other half is a small fraction of the real one.
    { re: /Utility Character/i, ok: function (u) { return u.tags.indexOf("Support") >= 0; },
      yes: "Utility effect", no: "Weak effect: not a Utility (Support) character", weak: true },
    { re: /Curse Character/i, ok: function (u) { return u.tags.indexOf("Curse") >= 0; },
      yes: "Curse effect", no: "Other effect: not a Curse character", weak: true }
  ];
  function gearFit(gid, unit) {
    var g = byId.gear[gid];
    for (var i = 0; i < CHECKS.length; i++) {
      if (CHECKS[i].re.test(g.effect)) {
        return CHECKS[i].ok(unit)
          ? { good: true, text: CHECKS[i].yes }
          : { good: !CHECKS[i].weak, text: CHECKS[i].no };
      }
    }
    return null;
  }

  // ---------- save, load, share ----------
  function encode() {
    var parts = state.pieces.map(function (p) {
      return [p.kind === "unit" ? "u" : "t", p.id, p.r, p.c, p.rot].join(".") + ((p.gear || []).length ? "." + p.gear.join(",") : "");
    });
    var q = "plan=" + parts.join("~");
    if (state.budget !== "") q += "&b=" + encodeURIComponent(state.budget);
    if (state.name) q += "&n=" + encodeURIComponent(state.name);
    return q;
  }
  function decode(str) {
    var out = { pieces: [], budget: "", name: "", skipped: 0 };
    str.replace(/^#/, "").split("&").forEach(function (kv) {
      var i = kv.indexOf("="), k = kv.slice(0, i), v = kv.slice(i + 1);
      if (k === "b") out.budget = decodeURIComponent(v);
      if (k === "n") out.name = decodeURIComponent(v);
      if (k === "plan" && v) v.split("~").forEach(function (s) {
        var f = s.split("."), kind = f[0] === "u" ? "unit" : "tile";
        if (!byId[kind][f[1]]) { out.skipped++; return; }
        out.pieces.push({ key: seq++, kind: kind, id: f[1], r: +f[2] || 0, c: +f[3] || 0, rot: +f[4] || 0,
          gear: (f[5] ? f[5].split(",") : []).filter(function (g) { return byId.gear[g]; }) });
      });
    });
    return out;
  }
  function save() {
    var q = encode();
    try { history.replaceState(null, "", state.pieces.length || state.budget !== "" ? "#" + q : location.pathname + location.search); } catch (e) {}
    try { localStorage.setItem(STORE, q); } catch (e) {}
  }
  function load() {
    var src = location.hash.indexOf("plan=") >= 0 ? location.hash : "";
    if (!src) { try { src = localStorage.getItem(STORE) || ""; } catch (e) {} }
    if (!src) return;
    var got = decode(src);
    state.pieces = got.pieces; state.budget = got.budget; state.name = got.name;
    if (got.skipped) ui.msg = got.skipped + " piece(s) in this plan aren't in the current data and were left out.";
  }

  // ---------- export ----------
  function boardBlock() {
    var L = letters();
    var floor = [], layout = [];
    for (var r = 0; r < N; r++) {
      var fr = "", lr = "";
      for (var c = 0; c < N; c++) {
        var t = at("tile", r, c), u = at("unit", r, c);
        fr += t ? L.get(t) : ".";
        lr += u ? L.get(u) : ".";
      }
      floor.push("  " + fr); layout.push("  " + lr);
    }
    var ordered = Array.from(L.keys());
    var lines = ["```board", "name: " + (state.name || "My board"), "season: " + D.seasonId, "floor: |"]
      .concat(floor, ["layout: |"], layout, ["pieces:"]);
    ordered.forEach(function (p) { lines.push("  " + L.get(p) + ": " + p.id); });
    var withGear = ordered.filter(function (p) { return (p.gear || []).length; });
    if (withGear.length) {
      lines.push("gear:");
      withGear.forEach(function (p) { lines.push("  " + L.get(p) + ": [" + p.gear.join(", ") + "]"); });
    }
    lines.push("```");
    return lines.join("\n");
  }

  // ---------- rendering ----------
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    for (var k in attrs || {}) {
      if (k === "class") el.className = attrs[k];
      else if (k === "text") el.textContent = attrs[k];
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== null && attrs[k] !== undefined && attrs[k] !== false) el.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (kid) { if (kid) el.appendChild(typeof kid === "string" ? document.createTextNode(kid) : kid); });
    return el;
  }
  function miniShape(shape, rot) {
    var cells = rotate(parseShape(shape), rot || 0), sz = size(cells);
    var el = h("span", { class: "swg-pl-mini", "aria-hidden": "true" });
    el.style.gridTemplate = "repeat(" + sz[0] + ", 6px) / repeat(" + sz[1] + ", 6px)";
    for (var r = 0; r < sz[0]; r++) for (var c = 0; c < sz[1]; c++) {
      var on = cells.some(function (p) { return p[0] === r && p[1] === c; });
      el.appendChild(h("span", { class: on ? "on" : "" }));
    }
    return el;
  }

  var els = {};
  function build() {
    root.innerHTML = "";
    els.budget = h("input", { type: "number", min: "0", max: "999", inputmode: "numeric", placeholder: "Any", id: "swg-pl-budget",
      oninput: function () { state.budget = els.budget.value; save(); renderSummary(); } });
    els.name = h("input", { type: "text", maxlength: "60", placeholder: "My board", id: "swg-pl-name",
      oninput: function () { state.name = els.name.value.trim(); save(); } });
    els.summary = h("div", { class: "swg-pl-summary", "aria-live": "polite" });
    var bar = h("div", { class: "swg-pl-bar" }, [
      h("label", {}, ["Soul Tokens to spend", els.budget]),
      h("label", {}, ["Name", els.name]),
      els.summary
    ]);

    els.board = h("div", { class: "swg-pl-board", role: "grid", "aria-label": N + " by " + N + " board" });
    els.board.addEventListener("mouseleave", function () { ui.hover = null; renderBoard(); });
    els.cells = [];
    for (var r = 0; r < N; r++) {
      var row = h("div", { role: "row", class: "swg-pl-row" });
      for (var c = 0; c < N; c++) {
        (function (r, c) {
          var cell = h("button", { type: "button", role: "gridcell", class: "swg-pl-cell",
            onclick: function () { clickCell(r, c); },
            onpointerdown: function (ev) { pressCell(ev, r, c); },
            onmouseenter: function () { if (ui.placing) { ui.hover = [r, c]; renderBoard(); } },
            onfocus: function () { if (ui.placing) { ui.hover = [r, c]; renderBoard(); } } });
          els.cells.push(cell); row.appendChild(cell);
        })(r, c);
      }
      els.board.appendChild(row);
    }
    els.msg = h("p", { class: "swg-pl-msg", "aria-live": "polite" });
    els.status = h("div", { class: "swg-pl-status" });
    els.detail = h("div", { class: "swg-pl-detail" });

    els.search = h("input", { type: "search", placeholder: "Search", "aria-label": "Search pieces",
      oninput: function () { ui.query = els.search.value.toLowerCase(); renderPalette(); } });
    els.tabs = h("div", { class: "swg-pl-tabs", role: "tablist" });
    [["unit", "Units"], ["tile", "Tiles"]].forEach(function (t) {
      els.tabs.appendChild(h("button", { type: "button", role: "tab", "data-tab": t[0], text: t[1],
        onclick: function () { ui.tab = t[0]; renderPalette(); } }));
    });
    els.list = h("ul", { class: "swg-pl-list" });
    var palette = h("div", { class: "swg-pl-palette" }, [els.tabs, els.search, els.list]);

    els.legend = h("ol", { class: "swg-pl-legend" });
    els.out = h("textarea", { class: "swg-pl-out", rows: "12", readonly: "readonly", "aria-label": "Board block", hidden: "hidden" });
    var actions = h("div", { class: "swg-pl-actions" }, [
      h("button", { type: "button", text: "Copy link", onclick: function () { copy(location.href, "Link copied. Anyone who opens it sees this board."); } }),
      h("button", { type: "button", text: "Copy board block", onclick: function () {
        var b = boardBlock(); els.out.value = b; els.out.hidden = false;
        copy(b, "Board block copied. Paste it into a build page.");
      } }),
      h("button", { type: "button", class: "swg-pl-danger", text: "Clear board", onclick: function () {
        if (!state.pieces.length) return;
        lastCleared = state.pieces; state.pieces = []; ui.selected = null; stopPlacing();
        ui.msg = "Board cleared."; ui.undo = true; save(); render();
      } })
    ]);

    // status sits under the board: its height changes while placing, and that must not move the board under the pointer
    var left = h("div", { class: "swg-pl-left" }, [els.board, els.status, els.msg, els.detail]);
    root.appendChild(bar);
    root.appendChild(h("div", { class: "swg-pl-main" }, [left, palette]));
    root.appendChild(h("h2", { id: "pieces", text: "Pieces on the board" }));
    root.appendChild(els.legend);
    root.appendChild(actions);
    root.appendChild(els.out);

    document.addEventListener("keydown", function (ev) {
      if (/INPUT|TEXTAREA|SELECT/.test((ev.target || {}).tagName)) return;
      if ((ev.key === "r" || ev.key === "R") && (ui.placing || ui.selected)) { ev.preventDefault(); ui.placing ? rotatePlacing() : rotateSelected(); }
      if (ev.key === "Escape") { stopPlacing(); ui.selected = null; render(); }
      if ((ev.key === "Delete" || ev.key === "Backspace") && ui.selected) { ev.preventDefault(); removeSelected(); }
    });
  }
  var lastCleared = null;

  function copy(text, done) {
    function ok() { ui.msg = done; renderMsg(); }
    function fail() { ui.msg = "Couldn't copy automatically. Select the text and copy it yourself."; els.out.value = text; els.out.hidden = false; els.out.select(); renderMsg(); }
    try { navigator.clipboard.writeText(text).then(ok, fail); } catch (e) { fail(); }
  }

  // ---------- actions ----------
  function startPlacing(kind, id, rot, gear) {
    ui.placing = { kind: kind, id: id, rot: rot || 0, gear: gear || [] };
    ui.selected = null; ui.msg = "";
    render();
  }
  function stopPlacing() {
    if (ui.moving) { state.pieces.push(ui.moving); ui.moving = null; }  // a cancelled move puts the piece back
    ui.placing = null; ui.hover = null;
  }
  function rotatePlacing() { ui.placing.rot = (ui.placing.rot + 1) % 4; ui.placing.grab = null; render(); drawGhost(); }
  function rotateSelected() {
    var p = ui.selected;
    if (p.kind === "tile" && unitsOn(p).length) { ui.msg = "Move the units on this tile before rotating it."; renderMsg(); return; }
    var old = p.rot; p.rot = (p.rot + 1) % 4;
    var why = problem(p);
    if (why) { p.rot = old; ui.msg = "Can't rotate here. " + why; }
    else { ui.msg = ""; save(); }
    render();
  }
  function unitsOn(tile) {
    var f = footprint(tile), out = [];
    f.forEach(function (q) { var u = at("unit", q[0], q[1]); if (u && out.indexOf(u) < 0) out.push(u); });
    return out;
  }
  function tilesUnder(unit) {
    var out = [];
    footprint(unit).forEach(function (q) { var t = at("tile", q[0], q[1]); if (t && out.indexOf(t) < 0) out.push(t); });
    return out;
  }
  function removeSelected() {
    var p = ui.selected;
    if (p.kind === "tile" && unitsOn(p).length) { ui.msg = "Remove or move the units standing on this tile first."; renderMsg(); return; }
    state.pieces.splice(state.pieces.indexOf(p), 1);
    ui.selected = null; ui.msg = ""; save(); render();
  }
  function moveSelected() {
    var p = ui.selected;
    if (p.kind === "tile" && unitsOn(p).length) { ui.msg = "Move the units on this tile first."; renderMsg(); return; }
    state.pieces.splice(state.pieces.indexOf(p), 1);
    ui.moving = p;
    ui.placing = { kind: p.kind, id: p.id, rot: p.rot, gear: p.gear || [] };
    ui.selected = null; ui.msg = "Pick the new spot. Esc puts it back.";
    render();
  }

  // Anchor the shape so the clicked square is its first square, which feels natural for any shape.
  // When dragging a placed piece, the square you grabbed stays under the pointer (pl.grab).
  function candidate(r, c) {
    var pl = ui.placing, cells = rotate(parseShape(byId[pl.kind][pl.id].shape), pl.rot);
    var g = pl.grab || cells[0];
    return { key: 0, kind: pl.kind, id: pl.id, rot: pl.rot, gear: pl.gear, r: r - g[0], c: c - g[1] };
  }

  function clickCell(r, c) {
    if (Date.now() < suppressClickUntil) return;
    if (ui.placing) {
      var cand = candidate(r, c), why = problem(cand);
      if (why) { ui.msg = why; ui.hover = [r, c]; render(); return; }
      cand.key = seq++;
      cand.gear = cand.gear.slice();
      state.pieces.push(cand);
      var wasMove = !!ui.moving;
      ui.moving = null;
      if (wasMove || cand.kind === "unit") { ui.placing = null; ui.hover = null; ui.selected = cand; }
      ui.msg = wasMove ? "Moved." : (cand.kind === "tile" && !dropping ? "Placed. Click again for another, or Esc when done." : "");
      save(); render();
      return;
    }
    ui.selected = at("unit", r, c) || at("tile", r, c);
    ui.msg = "";
    render();
  }

  // ---------- dragging ----------
  // A drag starts after a few pixels of movement. Pieces on the board and the shape icon in
  // each list row have touch-action: none, so a finger drags them; anywhere else a swipe still
  // scrolls the page.
  var suppressClickUntil = 0, dropping = false;
  var press = null;   // { x, y, pointerId, touch, timer, start: fn }
  var drag = null;    // { fromBoard, ghost }

  function pressPalette(ev, kind, id) {
    if (ev.button > 0) return;
    if (ev.pointerType === "touch" && !(ev.target.closest && ev.target.closest(".swg-pl-handle"))) return;
    beginPress(ev, function () {
      if (ui.moving) stopPlacing();
      ui.placing = { kind: kind, id: id, rot: 0, gear: [] };
      ui.selected = null; ui.msg = "";
      drag = { fromBoard: false };
    });
  }
  function pressCell(ev, r, c) {
    if (ev.button > 0 || ui.placing) return;
    var p = at("unit", r, c) || at("tile", r, c);
    if (!p) return;
    beginPress(ev, function () {
      if (p.kind === "tile" && unitsOn(p).length) {
        ui.msg = "Move the units on this tile first, then drag the tile."; renderMsg(); return false;
      }
      state.pieces.splice(state.pieces.indexOf(p), 1);
      ui.moving = p;
      ui.placing = { kind: p.kind, id: p.id, rot: p.rot, gear: p.gear || [],
                     grab: [r - p.r, c - p.c] };
      ui.selected = null; ui.msg = "";
      drag = { fromBoard: true };
    });
  }
  function beginPress(ev, start) {
    cancelPress();
    press = { x: ev.clientX, y: ev.clientY, id: ev.pointerId, start: start };
  }
  function cancelPress() { press = null; }
  function startDrag(x, y) {
    var go = press.start;
    cancelPress();
    if (go() === false) return;
    root.classList.add("is-dragging");
    drag.ghost = h("div", { class: "swg-pl-ghost", "aria-hidden": "true" });
    document.body.appendChild(drag.ghost);
    drag.x = x; drag.y = y;
    drawGhost();
    moveDrag(x, y);
    render();
  }
  function drawGhost() {
    if (!drag || !drag.ghost || !ui.placing) return;
    var pl = ui.placing, def = byId[pl.kind][pl.id];
    var cells = rotate(parseShape(def.shape), pl.rot), sz = size(cells);
    var px = els.cells[0].getBoundingClientRect().width;
    var g = pl.grab || cells[0];
    var hue = pl.kind === "unit" ? (state.pieces.filter(function (p) { return p.kind === "unit"; }).length % 6) : -1;
    drag.ghost.innerHTML = "";
    drag.ghost.style.gridTemplate = "repeat(" + sz[0] + ", " + px + "px) / repeat(" + sz[1] + ", " + px + "px)";
    drag.ghost.dataset.offX = (g[1] + 0.5) * px;
    drag.ghost.dataset.offY = (g[0] + 0.5) * px;
    for (var r = 0; r < sz[0]; r++) for (var c = 0; c < sz[1]; c++) {
      var on = cells.some(function (q) { return q[0] === r && q[1] === c; });
      drag.ghost.appendChild(h("span", { class: on ? (hue >= 0 ? "on swg-hue-" + hue : "on is-tile") : "" }));
    }
    placeGhost();
  }
  function placeGhost() {
    if (!drag || !drag.ghost) return;
    drag.ghost.style.transform = "translate(" + (drag.x - drag.ghost.dataset.offX) + "px," + (drag.y - drag.ghost.dataset.offY) + "px)";
  }
  function cellAt(x, y) {
    var el = document.elementFromPoint(x, y);
    var cell = el && el.closest ? el.closest(".swg-pl-cell") : null;
    var i = cell ? els.cells.indexOf(cell) : -1;
    return i < 0 ? null : [Math.floor(i / N), i % N];
  }
  function moveDrag(x, y) {
    drag.x = x; drag.y = y;
    placeGhost();
    var hit = cellAt(x, y);
    var changed = String(hit) !== String(ui.hover);
    ui.hover = hit;
    if (changed) renderBoard();
    // scroll the page when dragging near the top or bottom edge (the list sits below the board on phones)
    var edge = 70, vh = window.innerHeight;
    drag.scroll = y < edge ? -Math.ceil((edge - y) / 6) : y > vh - edge ? Math.ceil((y - (vh - edge)) / 6) : 0;
    if (drag.scroll && !drag.scrolling) {
      drag.scrolling = true;
      (function step() {
        if (!drag || !drag.scroll) { if (drag) drag.scrolling = false; return; }
        window.scrollBy(0, drag.scroll);
        var hit2 = cellAt(drag.x, drag.y);
        if (String(hit2) !== String(ui.hover)) { ui.hover = hit2; renderBoard(); }
        requestAnimationFrame(step);
      })();
    }
  }
  function endDrag(x, y, cancelled) {
    var d = drag;
    drag = null;
    root.classList.remove("is-dragging");
    if (d.ghost) d.ghost.remove();
    suppressClickUntil = Date.now() + 350;
    var hit = cancelled ? null : cellAt(x, y);
    if (hit) {
      var cand = candidate(hit[0], hit[1]);
      if (!problem(cand)) {
        dropping = true;
        clickCell2(hit[0], hit[1]);
        dropping = false;
        if (ui.placing && !ui.moving) { ui.placing = null; ui.hover = null; }  // a dropped tile doesn't keep placing mode
        render();
        return;
      }
      ui.msg = (d.fromBoard ? "Can't move it there. " : "Can't place it there. ") + problem(cand);
    } else {
      ui.msg = d.fromBoard ? "Dropped off the board, so it went back where it was." : "";
    }
    stopPlacing();
    if (d.fromBoard && state.pieces.length) ui.selected = state.pieces[state.pieces.length - 1];
    render();
  }
  // clickCell without the after-drag guard
  function clickCell2(r, c) { var t = suppressClickUntil; suppressClickUntil = 0; clickCell(r, c); suppressClickUntil = t; }

  document.addEventListener("pointermove", function (ev) {
    if (drag) { ev.preventDefault(); moveDrag(ev.clientX, ev.clientY); return; }
    if (!press || ev.pointerId !== press.id) return;
    if (Math.abs(ev.clientX - press.x) + Math.abs(ev.clientY - press.y) > 6) startDrag(ev.clientX, ev.clientY);
  }, { passive: false });
  document.addEventListener("pointerup", function (ev) {
    // use the last move position: some touch browsers report 0,0 on pointerup
    if (drag) {
      if (ev.clientX || ev.clientY) { drag.x = ev.clientX; drag.y = ev.clientY; }
      endDrag(drag.x, drag.y, false); return;
    }
    cancelPress();
  });
  document.addEventListener("pointercancel", function () {
    if (drag) endDrag(0, 0, true);
    cancelPress();
  });
  // While dragging with a finger, stop the page from scrolling under it.
  document.addEventListener("touchmove", function (ev) { if (drag) ev.preventDefault(); }, { passive: false });
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && drag) endDrag(0, 0, true); });

  // ---------- render pieces ----------
  function render() { renderBoard(); renderPalette(); renderDetail(); renderLegend(); renderSummary(); renderMsg(); renderStatus(); }

  function renderMsg() {
    els.msg.textContent = ui.msg || "";
    if (ui.undo && lastCleared) {
      els.msg.appendChild(document.createTextNode(" "));
      els.msg.appendChild(h("button", { type: "button", class: "swg-pl-link", text: "Undo", onclick: function () {
        state.pieces = lastCleared; lastCleared = null; ui.undo = false; ui.msg = "Restored."; save(); render();
      } }));
    }
    ui.undo = false;
  }

  function renderStatus() {
    els.status.innerHTML = "";
    if (ui.placing) {
      var def = byId[ui.placing.kind][ui.placing.id];
      els.status.appendChild(h("span", {}, [ui.moving ? "Moving " : "Placing ", h("b", { text: def.name })]));
      els.status.appendChild(miniShape(def.shape, ui.placing.rot));
      els.status.appendChild(h("button", { type: "button", text: "Rotate (R)", onclick: rotatePlacing }));
      els.status.appendChild(h("button", { type: "button", text: "Done (Esc)", onclick: function () { stopPlacing(); ui.msg = ""; render(); } }));
    } else {
      els.status.appendChild(h("span", { class: "swg-pl-hint", text: state.pieces.length
        ? "Drag pieces to move them. Click one to rotate, gear or remove it."
        : "Start with tiles: drag one from the list onto the board, or click it and then click the board. Units go on top." }));
    }
  }

  function renderBoard() {
    var L = letters();
    var preview = {}, previewBad = false;
    if (ui.placing && ui.hover) {
      var cand = candidate(ui.hover[0], ui.hover[1]);
      previewBad = !!problem(cand);
      footprint(cand).forEach(function (q) { preview[q[0] + "," + q[1]] = true; });
    }
    var units = state.pieces.filter(function (p) { return p.kind === "unit"; });
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) {
      var cell = els.cells[r * N + c];
      var t = at("tile", r, c), u = at("unit", r, c);
      var cls = ["swg-pl-cell"];
      cell.innerHTML = "";
      function edge(p, kind) {
        var e = [];
        if (at(kind, r - 1, c) !== p) e.push("e-t");
        if (at(kind, r + 1, c) !== p) e.push("e-b");
        if (at(kind, r, c - 1) !== p) e.push("e-l");
        if (at(kind, r, c + 1) !== p) e.push("e-r");
        return e.join(" ");
      }
      if (t) {
        cls.push("has-tile", edge(t, "tile"));
        if (ui.selected === t) cls.push("is-selected");
      }
      if (u) {
        var hue = units.indexOf(u) % 6;
        var first = footprint(u)[0];
        cell.appendChild(h("span", { class: "swg-pl-unit swg-hue-" + hue + " " + edge(u, "unit") + (ui.selected === u ? " is-selected" : "") },
          first[0] === r && first[1] === c ? [h("b", { text: L.get(u) })] : []));
      } else if (t) {
        var tf = footprint(t)[0];
        if (tf[0] === r && tf[1] === c) cell.appendChild(h("i", { text: L.get(t) }));
      }
      if (preview[r + "," + c]) cls.push(previewBad ? "is-bad" : "is-ok");
      cell.className = cls.join(" ");
      var label = "Row " + (r + 1) + ", column " + (c + 1) + ": " +
        (u ? byId.unit[u.id].name + " on " : "") + (t ? byId.tile[t.id].name : "empty");
      cell.setAttribute("aria-label", label);
    }
    root.classList.toggle("is-placing", !!ui.placing);
  }

  function renderPalette() {
    Array.prototype.forEach.call(els.tabs.children, function (b) {
      var on = b.getAttribute("data-tab") === ui.tab;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.classList.toggle("is-on", on);
    });
    els.list.innerHTML = "";
    var pool = ui.tab === "unit" ? D.units : D.tiles;
    var q = ui.query.trim();
    var shown = pool.filter(function (x) {
      return !q || (x.name + " " + (x.tags || []).join(" ") + " " + (x.grade || "") + " " + (x.effect || "")).toLowerCase().indexOf(q) >= 0;
    });
    shown.slice(0, 200).forEach(function (x) {
      var active = ui.placing && ui.placing.kind === ui.tab && ui.placing.id === x.id && !ui.moving;
      var meta = ui.tab === "unit"
        ? [x.grade ? h("span", { class: "swg-grade", "data-grade": x.grade.toLowerCase(), text: x.grade }) : null, h("span", { class: "swg-pl-tags", text: x.tags.join(", ") })]
        : [h("span", { class: "swg-pl-tags", text: x.effect })];
      els.list.appendChild(h("li", {}, [h("button", { type: "button", class: "swg-pl-item" + (active ? " is-on" : ""), "aria-pressed": active ? "true" : "false",
        onclick: function () {
          if (Date.now() < suppressClickUntil) return;
          if (active) { stopPlacing(); render(); } else { if (ui.moving) stopPlacing(); startPlacing(ui.tab, x.id); } },
        onpointerdown: function (ev) { pressPalette(ev, ui.tab, x.id); } },
        [h("span", { class: "swg-pl-handle", title: "Drag onto the board" }, [miniShape(x.shape)]), h("span", { class: "swg-pl-name" }, [h("span", { text: x.name }), h("span", { class: "swg-pl-meta" }, meta)]),
         h("span", { class: "swg-pl-price", text: String(x.price) })])]));
    });
    if (!shown.length) els.list.appendChild(h("li", { class: "swg-pl-empty", text: "Nothing matches." }));
  }

  function renderDetail() {
    els.detail.innerHTML = "";
    var p = ui.selected;
    if (!p) { els.detail.hidden = true; return; }
    els.detail.hidden = false;
    var def = byId[p.kind][p.id];
    var head = h("div", { class: "swg-pl-detail__head" }, [
      h("strong", { text: def.name }), h("span", { class: "swg-pl-price", text: String(def.price) })]);
    els.detail.appendChild(head);
    var btns = h("div", { class: "swg-pl-actions" }, [
      h("button", { type: "button", text: "Rotate", onclick: rotateSelected }),
      h("button", { type: "button", text: "Move", onclick: moveSelected }),
      h("button", { type: "button", class: "swg-pl-danger", text: "Remove", onclick: removeSelected })
    ]);
    if (p.kind === "tile") {
      els.detail.appendChild(h("p", { class: "swg-pl-effect", text: def.effect && def.effect !== "N/A" ? def.effect : "No effect." }));
      var on = unitsOn(p).map(function (u) { return byId.unit[u.id].name; });
      if (on.length) els.detail.appendChild(h("p", { class: "swg-pl-sub", text: "Under: " + on.join(", ") }));
      els.detail.appendChild(btns);
      return;
    }
    els.detail.appendChild(h("p", { class: "swg-pl-sub", text: [def.grade, def.tags.join(", ")].filter(Boolean).join(" · ") }));
    var under = tilesUnder(p).map(function (t) { return byId.tile[t.id]; });
    var withEffect = under.filter(function (t) { return t.effect && t.effect !== "N/A"; });
    els.detail.appendChild(h("p", { class: "swg-pl-sub" }, ["Standing on: " + (under.length ? under.map(function (t) { return t.name; }).join(", ") : "nothing")]));
    if (withEffect.length) {
      var ul = h("ul", { class: "swg-pl-effects" });
      withEffect.forEach(function (t) { ul.appendChild(h("li", {}, [h("b", { text: t.name + ": " }), t.effect])); });
      els.detail.appendChild(ul);
    }
    // gear
    var gl = h("ul", { class: "swg-pl-gear" });
    (p.gear || []).forEach(function (gid, i) {
      var g = byId.gear[gid], fit = gearFit(gid, def);
      gl.appendChild(h("li", { title: g.effect }, [
        h("span", { text: g.name }), h("span", { class: "swg-pl-price", text: String(g.price) }),
        fit ? h("span", { class: "swg-pl-fit" + (fit.good ? "" : " is-weak"), text: fit.text }) : null,
        h("button", { type: "button", class: "swg-pl-x", "aria-label": "Remove " + g.name, text: "×", onclick: function () {
          p.gear.splice(i, 1); save(); render(); } })]));
    });
    var sel = h("select", { "aria-label": "Add gear", onchange: function () {
      if (!sel.value) return;
      p.gear = (p.gear || []).concat([sel.value]); save(); render();
    } }, [h("option", { value: "", text: "Add gear…" })].concat(D.gear.map(function (g) {
      var fit = gearFit(g.id, def);
      return h("option", { value: g.id, text: g.name + " (" + g.price + ")" + (fit && !fit.good ? ", weak on this unit" : "") });
    })));
    els.detail.appendChild(h("div", { class: "swg-pl-gearbox" }, [h("span", { class: "swg-pl-sub", text: "Gear" }), gl, sel]));
    var link = def.guide ? h("a", { href: "../../units/" + def.id + "/", text: "Unit guide" }) : null;
    els.detail.appendChild(btns);
    if (link) btns.appendChild(link);
  }

  function renderLegend() {
    var L = letters();
    els.legend.innerHTML = "";
    var units = state.pieces.filter(function (p) { return p.kind === "unit"; });
    if (!state.pieces.length) { els.legend.appendChild(h("li", { class: "swg-pl-empty", text: "Nothing placed yet." })); return; }
    Array.from(L.keys()).forEach(function (p) {
      var def = byId[p.kind][p.id];
      var gear = (p.gear || []).map(function (g) { return byId.gear[g]; });
      var hue = p.kind === "unit" ? " swg-hue-" + (units.indexOf(p) % 6) : "";
      els.legend.appendChild(h("li", { class: ui.selected === p ? "is-selected" : "" }, [
        h("span", { class: "swg-key swg-cell--" + p.kind + hue, text: L.get(p) }),
        h("button", { type: "button", class: "swg-pl-link", text: def.name, onclick: function () { stopPlacing(); ui.selected = p; render(); } }),
        h("span", { class: "swg-pl-gearlist", text: gear.map(function (g) { return g.name + " " + g.price; }).join(" · ") }),
        h("span", { class: "swg-pl-price", text: String(def.price + gear.reduce(function (s, g) { return s + g.price; }, 0)) })]));
    });
  }

  function renderSummary() {
    var t = cost();
    var b = state.budget === "" ? null : Math.max(0, parseInt(state.budget, 10) || 0);
    els.summary.innerHTML = "";
    els.summary.appendChild(h("span", { class: "swg-pl-total" }, [h("b", { text: String(t.total) }), " tokens"]));
    els.summary.appendChild(h("span", { class: "swg-pl-split",
      text: "Units " + t.unit + " · Tiles " + t.tile + " · Gear " + t.gear }));
    if (b !== null) {
      var left = b - t.total;
      els.summary.appendChild(h("span", { class: "swg-pl-remain" + (left < 0 ? " is-over" : ""),
        text: left < 0 ? (-left) + " over budget" : left + " left" }));
    }
  }

  // ---------- start ----------
  build();
  load();
  els.budget.value = state.budget;
  els.name.value = state.name;
  render();
})();
