"""Browser tests for the built site, mostly the Board planner.

    uv run playwright install chromium   (once, downloads the test browser)
    uv run pytest                        (builds the site, then runs every test)

The site is served the way GitHub Pages serves it: under the folder in site_url
(/browndust2-library/), with 404.html for missing pages. Tests pick their pieces from
content/ (a 1x1 unit, a 1x1 tile, a tile two squares wide), so editing the data doesn't break them.
"""
from __future__ import annotations

import functools
import http.server
import json
import os
import threading
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright

from swg_site import catalog, render
from swg_site.linkcheck import site_url
from swg_site.paths import LIB, SITE

BASE = urlsplit(site_url()).path.rstrip("/")  # "/browndust2-library"


# ---------- the site ----------
@pytest.fixture(scope="session")
def built():
    """Build once per run. SWG_TEST_NO_BUILD=1 skips it (CI builds just before the tests)."""
    if not os.environ.get("SWG_TEST_NO_BUILD"):
        from swg_site.cli import build_main
        build_main()
    assert (SITE / "index.html").exists(), "no site/ to test; run uv run swg-build"


class _Pages(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if not path.startswith(BASE + "/"):
            return str(SITE / "__missing__")
        return super().translate_path(path[len(BASE):])

    def send_error(self, code, message=None, explain=None):
        page = SITE / "404.html"
        if code != 404 or not page.exists():
            return super().send_error(code, message, explain)
        body = page.read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture(scope="session")
def url(built):
    """Address of the site's front page, like https://babylath.github.io/browndust2-library/."""
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Pages, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}{BASE}/"
    server.shutdown()


# ---------- browsers ----------
@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(pw):
    b = pw.chromium.launch()
    yield b
    b.close()


def _watch(page, errors):
    page.on("pageerror", lambda e: errors.append(str(e)))
    return page


@pytest.fixture
def page(browser):
    """Desktop page with a fresh browser profile (empty localStorage) for every test."""
    ctx = browser.new_context(viewport={"width": 1280, "height": 1500}, accept_downloads=True,
                              permissions=["clipboard-read", "clipboard-write"])
    errors: list[str] = []
    ctx.on("page", lambda p: _watch(p, errors))
    p = ctx.new_page()
    yield p
    ctx.close()
    assert not errors, f"JavaScript errors: {errors}"


@pytest.fixture
def phone(pw, browser):
    ctx = browser.new_context(**pw.devices["iPhone 13"])
    errors: list[str] = []
    ctx.on("page", lambda p: _watch(p, errors))
    p = ctx.new_page()
    yield p
    ctx.close()
    assert not errors, f"JavaScript errors: {errors}"


# ---------- test data, chosen from content/ ----------
@pytest.fixture(scope="session")
def cat():
    return catalog.load()


def _first(items, test):
    for key, row in sorted(items.items()):
        if test(row):
            return key, row
    return None, None


@pytest.fixture(scope="session")
def pieces(cat):
    """unit: a 1x1 unit; tile: a 1x1 tile; wide: a tile whose top row is at least two squares."""
    def rows(x):
        return render.parse_shape(x.get("shape") or "") or []
    unit = _first(cat.units, lambda u: rows(u) == ["#"])
    tile = _first(cat.tiles, lambda t: rows(t) == ["#"])
    wide = _first(cat.tiles, lambda t: rows(t)[:1] and rows(t)[0].startswith("##"))
    if not (unit[0] and tile[0] and wide[0]):
        pytest.skip("content/ needs a 1x1 unit, a 1x1 tile and a tile two squares wide for these tests")
    return {"unit": unit[0], "unit_name": cat.unit_label(unit[0]), "tile": tile[0], "tile_name": tile[1]["name"],
            "wide": wide[0], "wide_name": wide[1]["name"]}


@pytest.fixture(scope="session")
def guides():
    return sorted(p.stem for p in (LIB / "units").glob("*.md") if p.stem != "index")


# ---------- planner helpers ----------
class Planner:
    def __init__(self, page, url):
        self.p, self.url = page, url

    def open(self, hash_: str = ""):
        self.p.goto(self.url + "tools/planner/" + hash_)
        self.p.wait_for_selector(".swg-pl-cell")
        return self

    def cell(self, r: int, c: int):
        return self.p.locator(".swg-pl-cell").nth(r * 7 + c)

    def item(self, kind: str, name: str):
        self.p.click(f'.swg-pl-tabs button[data-tab="{kind}"]')
        self.p.fill(".swg-pl-palette input[type=search]", name.lower())
        return self.p.locator(".swg-pl-item").first

    def drag(self, src, dst):
        """Mouse drag from one element's centre to another's, the way a person would."""
        a, b = src.bounding_box(), dst.bounding_box()
        x1, y1 = a["x"] + a["width"] / 2, a["y"] + a["height"] / 2
        x2, y2 = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
        m = self.p.mouse
        m.move(x1, y1)
        m.down()
        m.move(x1 + 10, y1 + 5, steps=3)
        m.move(x2, y2, steps=12)
        m.up()
        self.p.wait_for_timeout(450)  # the planner ignores clicks for a moment after a drop

    def state(self) -> list[tuple]:
        """Pieces as saved: (kind, id, row, col, turns, tray)."""
        q = self.p.evaluate("localStorage.getItem('swg-planner')") or ""
        plan = next((kv[5:] for kv in q.split("&") if kv.startswith("plan=")), "")
        out = []
        for s in filter(None, plan.split("~")):
            f = s.split(".")
            tray = f[2] == "-"
            out.append((f[0], f[1], None if tray else int(f[2]), None if tray else int(f[3]), int(f[4]), tray))
        return out

    def msg(self) -> str:
        return self.p.text_content(".swg-pl-left > .swg-pl-msg") or ""

    def tray(self):
        return self.p.locator(".swg-pl-tray__item")


@pytest.fixture
def planner(page, url):
    return Planner(page, url)


def plan(*pieces: str, name: str = "") -> str:
    """#plan= hash from "t.id.r.c.rot" strings."""
    return "#plan=" + "~".join(pieces) + (f"&n={name}" if name else "")


def touch_drag(page, src, dst, steps: int = 14):
    """Finger drag through Chrome's DevTools protocol (Playwright has no touch-move)."""
    cdp = page.context.new_cdp_session(page)
    a, b = src.bounding_box(), dst.bounding_box()
    x1, y1 = a["x"] + a["width"] / 2, a["y"] + a["height"] / 2
    x2, y2 = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x1, "y": y1}]})
    for k in range(1, steps + 1):
        cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [
            {"x": x1 + (x2 - x1) * k / steps, "y": y1 + (y2 - y1) * k / steps}]})
        page.wait_for_timeout(16)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(450)


def saved(page) -> dict:
    return json.loads(page.evaluate("localStorage.getItem('swg-planner-saves') || '[]'") or "[]")
