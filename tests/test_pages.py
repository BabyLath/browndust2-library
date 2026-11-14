"""Tables, Add to planner, the page-not-found page and every link on the site."""
from swg_site import linkcheck


def numbers(page, table, key):
    return page.locator(f"#{table} tbody tr:not([hidden])").evaluate_all(f"rs => rs.map(r => r.dataset.{key})")


def test_every_link_and_image_exists(built):
    assert linkcheck.check() == []


def test_units_filter_and_sort(page, url):
    page.goto(url + "units/")
    page.fill("[data-f=max]", "5")
    prices = [int(x) for x in numbers(page, "swg-units", "price")]
    assert prices and max(prices) <= 5
    assert page.text_content("[data-count]").startswith(f"{len(prices)} of")
    page.select_option("[data-sort-by]", "price:desc")
    prices = [int(x) for x in numbers(page, "swg-units", "price")]
    assert prices == sorted(prices, reverse=True)
    assert page.get_attribute('th[data-sort="price"]', "aria-sort") == "descending"
    page.click('th[data-sort="char"] .swg-sort')
    names = numbers(page, "swg-units", "char")
    assert names == sorted(names)


def test_gear_search_reads_effects(page, url, cat):
    effect = next((g["effect"] for g in cat.gear.values() if g.get("effect")), None)
    if not effect:
        return
    word = max((w for w in effect.replace("[", " ").replace("]", " ").split() if w.isalpha()), key=len).lower()
    page.goto(url + "reference/gear/")
    page.fill("[data-f=q]", word)
    rows = page.locator("#swg-gear tbody tr:not([hidden])")
    assert rows.count() >= 1
    assert all(word in s for s in rows.evaluate_all("rs => rs.map(r => r.dataset.search)"))


def test_tiles_sort_by_shape(page, url):
    page.goto(url + "reference/tiles/")
    page.click('th[data-sort="cells"] .swg-sort')
    cells = [int(x) for x in numbers(page, "swg-tiles", "cells") if x]
    assert cells == sorted(cells)


def test_add_to_planner_from_the_units_table(page, url):
    page.goto(url + "units/")
    rows = page.locator("#swg-units tbody tr")
    rows.nth(0).locator("a.swg-addplan").click()
    rows.nth(1).locator("a.swg-addplan").click()
    assert "Added" in page.text_content(".swg-toast")
    rows.nth(1).locator("a.swg-addplan").click()
    assert "already" in page.text_content(".swg-toast")
    assert page.url.endswith("/units/")  # stays on the page
    page.click(".swg-toast a")
    page.wait_for_selector(".swg-pl-cell")
    assert page.locator(".swg-pl-tray__item").count() == 2


def test_add_to_planner_on_a_unit_guide(page, url, guides):
    if not guides:
        return
    page.goto(url + f"units/{guides[0]}/")
    page.click(".swg-guide__actions a.swg-addplan")
    assert "Added" in page.text_content(".swg-toast")


def test_page_not_found_suggests_the_page(page, url, guides, cat):
    if not guides:
        return
    uid = guides[0]
    resp = page.goto(url + f"units/{uid.split('-')[0]}/")
    assert resp.status == 404
    page.wait_for_selector("[data-404-guess]:not([hidden])")
    assert cat.unit_label(uid) in page.text_content("[data-404-guess]")


def test_page_not_found_works_at_any_depth(page, url):
    resp = page.goto(url + "no/such/deep/page/")
    assert resp.status == 404
    assert page.text_content("h1") == "Page not found"
    # the site's own stylesheet loaded, so relative paths didn't break
    assert page.evaluate("[...document.styleSheets].some(s => (s.href || '').endsWith('/styles/extra.css'))")
    for href in page.locator(".swg-404__links a").evaluate_all("as => as.map(a => a.href)"):
        assert page.request.get(href).status == 200, href


def _animated(cat_portraits_dir="images/portraits/still"):
    from swg_site.paths import SITE
    return sorted(p.stem for p in (SITE / cat_portraits_dir).glob("*.avif"))


def test_lists_show_still_portraits(page, url):
    if not _animated():
        return
    page.goto(url + "units/")
    srcs = page.locator("#swg-units .swg-thumb img").evaluate_all("is => is.map(i => i.getAttribute('src'))")
    assert srcs and all("/still/" in s for s in srcs if any(a in s for a in _animated()))


def test_guide_portrait_animates_unless_motion_is_reduced(browser, url, guides):
    animated = [g for g in guides if g in _animated()]
    if not animated:
        return
    for reduce, want_still in (("no-preference", False), ("reduce", True)):
        ctx = browser.new_context(reduced_motion=reduce)
        p = ctx.new_page()
        p.goto(url + f"units/{animated[0]}/")
        src = p.locator(".swg-guide__art img").evaluate("i => i.currentSrc")
        assert ("/still/" in src) == want_still, (reduce, src)
        ctx.close()


def test_planner_list_still_board_animated(page, url, cat):
    animated = _animated()
    if not animated:
        return
    uid = animated[0]
    page.goto(url + f"tools/planner/#plan=u.{uid}.0.0.0")
    page.wait_for_selector(".swg-pl-chibis img")
    assert "/still/" not in page.locator(".swg-pl-chibis img").first.get_attribute("src")
    page.fill(".swg-pl-palette input[type=search]", cat.unit_label(uid).lower())
    assert "/still/" in page.locator(".swg-pl-list .swg-pl-chibi img").first.get_attribute("src")
