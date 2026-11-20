/* BrownDust II Library: table filters, calculators and the season countdown.
   Plain JS, no dependencies. Each feature only runs if its markup is on the page. */
(function () {
  // ---------- shop math (keep in sync with swg_site/render.py) ----------
  var sale = function (p) { return Math.ceil(p / 2); };
  var sell = function (p, prot) { return prot ? 1 : Math.max(2, Math.floor(p / 2)); };
  var rerollCost = function (n) { return 1 + Math.floor((n - 1) / 4); };
  var rerollTotal = function (n) { var t = 0; for (var i = 1; i <= n; i++) t += rerollCost(i); return t; };
  var endGame = function (t) {
    if (t < 20) return 0;
    if (t < 48) return Math.max(0, Math.floor(t / 3) - 6);
    return Math.ceil(Math.pow(1.11, Math.floor(t / 3) + 6));
  };
  var endGameTotal = function (t) { var s = 0; for (var i = 20; i <= t; i++) s += endGame(i); return s; };

  // ---------- table filter (Units, Gear, Tiles) ----------
  function initFilter(box) {
    var table = document.getElementById(box.dataset.target);
    if (!table) return;
    var rows = Array.prototype.slice.call(table.tBodies[0].rows);
    var none = { value: "", checked: false };
    var f = function (k) { return box.querySelector('[data-f="' + k + '"]') || none; };
    var count = box.querySelector("[data-count]");
    function apply() {
      var q = (f("q").value || "").trim().toLowerCase();
      var grade = f("grade").value, tag = f("tag").value;
      var max = parseInt(f("max").value, 10);
      var shown = 0;
      rows.forEach(function (r) {
        var ok = (!q || r.dataset.search.indexOf(q) !== -1) &&
          (!grade || r.dataset.grade === grade) &&
          (!tag || r.dataset.tags.split("|").indexOf(tag) !== -1) &&
          (isNaN(max) || +r.dataset.price <= max);
        r.hidden = !ok;
        if (ok) shown++;
      });
      count.textContent = shown + " of " + rows.length;
    }
    box.addEventListener("input", apply);
    box.addEventListener("change", apply);
    apply();
    initSort(box, table);
  }

  // ---------- unit table sort ----------
  // The Sort menu (works on phones, where the header row is hidden) and the column headers
  // drive the same sort. Ties keep the default order: character, then costume.
  function initSort(box, table) {
    var sel = box.querySelector("[data-sort-by]");
    var heads = Array.prototype.slice.call(table.querySelectorAll("thead th[data-sort]"));
    if (!sel && !heads.length) return;
    var body = table.tBodies[0];
    var rows = Array.prototype.slice.call(body.rows);
    rows.forEach(function (r, i) { r._order = i; });
    function sortBy(key, dir) {
      var m = dir === "desc" ? -1 : 1;
      rows.slice().sort(function (a, b) {
        var x = a.dataset[key], y = b.dataset[key];
        if (x === "" || y === "") return (x === "" ? 1 : 0) - (y === "" ? 1 : 0) || a._order - b._order;  // blanks last
        var c = isFinite(x) && isFinite(y) ? x - y : x.localeCompare(y);  // numbers as numbers, names A to Z
        return c * m || a._order - b._order;
      }).forEach(function (r) { body.appendChild(r); });
      heads.forEach(function (th) {
        if (th.dataset.sort === key) th.setAttribute("aria-sort", dir === "desc" ? "descending" : "ascending");
        else th.removeAttribute("aria-sort");
      });
      if (sel) {
        sel.value = key + ":" + dir;
        if (sel.value !== key + ":" + dir) sel.selectedIndex = -1;
      }
    }
    if (sel) sel.addEventListener("change", function () {
      var v = sel.value.split(":");
      sortBy(v[0], v[1]);
    });
    heads.forEach(function (th) {
      var btn = th.querySelector(".swg-sort");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var key = th.dataset.sort;
        // a second click on the sorted column flips it
        sortBy(key, th.getAttribute("aria-sort") === "ascending" ? "desc" : "asc");
      });
    });
  }

  // ---------- add to planner ----------
  // "Add to planner" links put a unit in the Board planner's To place tray without leaving the
  // page, so you can collect several. The planner keeps its board in localStorage as
  // "plan=piece~piece&b=budget&n=name"; a tray piece is u.<id>.-.-.0. If storage is blocked
  // the link just opens the planner, which reads #add=<id> itself.
  var PLAN_KEY = "swg-planner";
  function addToPlanner(a) {
    var id = a.dataset.addUnit, name = a.dataset.name || id, saved;
    try { saved = localStorage.getItem(PLAN_KEY) || ""; } catch (e) { return false; }
    var params = saved.replace(/^#/, "").split("&").filter(Boolean), plan = "";
    params = params.filter(function (kv) { if (kv.indexOf("plan=") === 0) { plan = kv.slice(5); return false; } return true; });
    var pieces = plan ? plan.split("~") : [];
    var have = pieces.some(function (p) { var f = p.split("."); return f[0] === "u" && f[1] === id; });
    if (!have) {
      pieces.push("u." + id + ".-.-.0");
      try { localStorage.setItem(PLAN_KEY, ["plan=" + pieces.join("~")].concat(params).join("&")); } catch (e) { return false; }
    }
    var waiting = pieces.filter(function (p) { return p.split(".")[2] === "-"; }).length;
    toast(have ? name + " is already in your planner." : "Added " + name + " to the planner. " + waiting + " piece" + (waiting === 1 ? "" : "s") + " waiting to be placed.",
          a.href.split("#")[0]);
    return true;
  }
  var toastEl = null, toastTimer = null;
  function toast(text, plannerUrl) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "swg-toast";
      toastEl.setAttribute("role", "status");
      document.body.appendChild(toastEl);
    }
    toastEl.innerHTML = "";
    toastEl.appendChild(document.createTextNode(text + " "));
    var open = document.createElement("a");
    open.href = plannerUrl; open.textContent = "Open planner";
    toastEl.appendChild(open);
    var x = document.createElement("button");
    x.type = "button"; x.className = "swg-toast__x"; x.setAttribute("aria-label", "Dismiss"); x.textContent = "×";
    x.onclick = function () { toastEl.classList.remove("is-on"); };
    toastEl.appendChild(x);
    toastEl.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-on"); }, 6000);
  }
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[data-add-unit]");
    if (!a || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.button > 0) return;  // new tab or window: let the link open the planner
    if (addToPlanner(a)) ev.preventDefault();
  });

  // ---------- page not found ----------
  // Guess the page an old or mistyped address meant: compare its words with each page's
  // address and title in the search index (search.json) and list the closest few.
  function initNotFound(box) {
    var cfg = {};
    try { cfg = JSON.parse(document.getElementById("__config").textContent); } catch (e) {}
    var base = (cfg.base || "").replace(/\/$/, "");
    var asked = decodeURIComponent(location.pathname).toLowerCase();
    if (base && asked.indexOf(base.toLowerCase()) === 0) asked = asked.slice(base.length);
    asked = asked.replace(/(index)?\.html?$/, "").replace(/^\/+|\/+$/g, "");
    if (!asked) return;
    var words = function (t) { return String(t).toLowerCase().split(/[^a-z0-9]+/).filter(Boolean); };
    var segs = asked.split("/").filter(Boolean);
    var section = segs.length > 1 ? segs[0] : "";           // "units" in units/celia/
    var names = segs.length > 1 ? segs.slice(1) : segs;    // the parts that name the page
    function pairs(t) { var out = []; t = t.replace(/[^a-z0-9]/g, ""); for (var i = 0; i < t.length - 1; i++) out.push(t.slice(i, i + 2)); return out; }
    function dice(a, b) {  // letter-pair overlap, 0 to 1: forgives typos like "planer" or "gears"
      var x = pairs(a), y = pairs(b), n = y.length, hit = 0;
      if (!x.length || !n) return 0;
      x.forEach(function (p) { var i = y.indexOf(p); if (i >= 0) { hit++; y.splice(i, 1); } });
      return 2 * hit / (x.length + n);
    }
    function overlap(name, have) {  // share of the name's words found in the page's address or title
      var w = words(name);
      return w.filter(function (x) { return have.some(function (h) { return h.indexOf(x) === 0 || (x.indexOf(h) === 0 && h.length > 2); }); }).length / (w.length || 1);
    }
    fetch(base + "/search.json").then(function (r) { return r.json(); }).then(function (d) {
      var seen = {};
      var scored = (d.items || []).filter(function (it) {
        if (it.location.indexOf("#") >= 0 || seen[it.location]) return false;
        return (seen[it.location] = true);
      }).map(function (it) {
        var parts = it.location.split("/").filter(Boolean), seg = parts[parts.length - 1] || "", title = it.title.toLowerCase();
        var have = words(seg + " " + title);
        var best = Math.max.apply(null, names.map(function (n) { return Math.max(overlap(n, have), dice(n, seg), dice(n, title)); }));
        return { it: it, score: best + (section && parts[0] === section ? 0.15 : 0) };
      }).filter(function (x) { return x.score >= 0.5; })
        .sort(function (a, b) { return b.score - a.score; });
      if (scored.length) scored = scored.filter(function (x) { return x.score >= scored[0].score * 0.75; }).slice(0, 4);
      if (!scored.length) return;
      var ul = box.querySelector("ul");
      scored.forEach(function (x) {
        var li = document.createElement("li"), a = document.createElement("a");
        a.href = base + "/" + x.it.location; a.textContent = x.it.title;
        li.appendChild(a); ul.appendChild(li);
      });
      box.hidden = false;
    }).catch(function () {});
  }

  // ---------- calculators ----------
  var calcs = {
    reroll: function (el, out) {
      var n = Math.max(0, Math.min(40, +el.querySelector('[data-in="n"]').value || 0));
      out.innerHTML = n === 0 ? "No rerolls yet. The first one costs <strong>1</strong>."
        : "Spent so far: <strong>" + rerollTotal(n) + "</strong> tokens. The next reroll costs <strong>" + rerollCost(n + 1) + "</strong>.";
    },
    price: function (el, out) {
      var prot = el.querySelector('[data-in="prot"]').checked;
      var input = el.querySelector('[data-in="p"]');
      if (prot) input.value = 2;
      var p = Math.max(1, +input.value || 1);
      out.innerHTML = "On sale: <strong>" + sale(p) + "</strong>. Sells back for <strong>" + sell(p, prot) + "</strong>.";
    },
    endgame: function (el, out) {
      var t = +el.querySelector('[data-in="t"]').value;
      el.querySelector("[data-t]").textContent = t;
      var spark = el.querySelector("[data-spark]");
      if (!spark.childElementCount) {
        var max = endGame(90), html = "";
        for (var i = 0; i <= 90; i++) html += '<span style="height:' + (endGame(i) / max * 100) + '%"></span>';
        spark.innerHTML = html;
      }
      Array.prototype.forEach.call(spark.children, function (s, i) { s.classList.toggle("on", i <= t); });
      out.innerHTML = t < 20 ? "End Game starts at 20 seconds."
        : "At " + t + "s both sides take <strong>" + endGame(t) + "</strong> damage per second, <strong>" + endGameTotal(t) + "</strong> in total so far.";
    }
  };

  function initCalc(el) {
    var fn = calcs[el.dataset.calc], out = el.querySelector("[data-out]");
    if (!fn) return;
    var run = function () { fn(el, out); };
    el.addEventListener("input", run);
    el.addEventListener("change", run);
    run();
  }

  // ---------- current season countdown ----------
  function initSeason(el) {
    var end = el.dataset.seasonEnd, slot = el.querySelector("[data-countdown]");
    if (!end || !slot) return;
    var lock = new Date(end + "T15:00:00Z"); // settlement starts 15:00 UTC on the last day
    var start = new Date(el.dataset.seasonStart + "T00:00:00Z");
    var now = Date.now();
    var days = Math.ceil((lock - now) / 86400000);
    var day = Math.floor((now - start) / 86400000) + 1;
    if (now < start) {  // added ahead of time with swg-new-season: say when it starts instead
      var wait = Math.ceil((start - now) / 86400000), h2 = el.querySelector("h2"), dates = el.querySelector(".swg-now__dates");
      if (h2 && el.dataset.name) h2.textContent = el.dataset.name + " starts soon";
      if (dates) dates.textContent = dates.textContent.replace(/^Started/, "Starts");
      slot.textContent = "Starts in " + wait + " day" + (wait === 1 ? "" : "s") + ".";
      return;
    }
    var approx = el.dataset.approx === "1" ? "about " : "";
    slot.textContent = days > 0
      ? "Day " + day + ", " + approx + days + " day" + (days === 1 ? "" : "s") + " left, locking " +
        lock.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) + " your time."
      : "This season has ended. Update content/seasons.yaml with the next one.";
  }

  // ---------- column toggles: <input type="checkbox" data-toggle="class-name"> ----------
  // Adds or removes the class on the filter's table. The choice is remembered in this browser.
  function initToggles(box) {
    var table = document.getElementById(box.dataset.target);
    if (!table) return;
    box.querySelectorAll("[data-toggle]").forEach(function (input) {
      var key = "swg:" + table.id + ":" + input.dataset.toggle;
      try { input.checked = localStorage.getItem(key) === "1"; } catch (e) {}
      var apply = function () {
        table.classList.toggle(input.dataset.toggle, input.checked);
        try { localStorage.setItem(key, input.checked ? "1" : "0"); } catch (e) {}
      };
      input.addEventListener("change", apply);
      apply();
    });
  }

  function init() {
    document.querySelectorAll(".swg-filter").forEach(initFilter);
    document.querySelectorAll(".swg-filter").forEach(initToggles);
    document.querySelectorAll(".swg-calc").forEach(initCalc);
    document.querySelectorAll(".swg-now").forEach(initSeason);
    document.querySelectorAll("[data-404-guess]").forEach(initNotFound);
  }

  // Works with or without Zensical's instant navigation.
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
