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

  // ---------- unit table filter ----------
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
      var guide = f("guide").checked;
      var shown = 0;
      rows.forEach(function (r) {
        var ok = (!q || r.dataset.search.indexOf(q) !== -1) &&
          (!grade || r.dataset.grade === grade) &&
          (!tag || r.dataset.tags.split("|").indexOf(tag) !== -1) &&
          (isNaN(max) || +r.dataset.price <= max) &&
          (!guide || r.dataset.guide === "1");
        r.hidden = !ok;
        if (ok) shown++;
      });
      count.textContent = shown + " of " + rows.length;
    }
    box.addEventListener("input", apply);
    box.addEventListener("change", apply);
    apply();
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
  }

  // Works with or without Zensical's instant navigation.
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
