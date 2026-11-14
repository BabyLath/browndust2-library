"""Board planner on a phone: the piece list is a drawer at the bottom, pieces move by finger."""
from conftest import Planner, plan, touch_drag


def open_phone(phone, url, hash_=""):
    pl = Planner(phone, url).open(hash_)
    phone.locator(".swg-pl-board").evaluate("e => { e.scrollIntoView({block: 'start'}); scrollBy(0, -70); }")
    phone.wait_for_timeout(300)
    return pl


def test_drawer_is_open_on_an_empty_board(phone, url):
    open_phone(phone, url)
    assert phone.locator(".swg-pl-palette").evaluate("e => getComputedStyle(e).position") == "fixed"
    assert phone.get_attribute(".swg-pl-drawer-btn", "aria-expanded") == "true"
    assert phone.locator(".swg-pl-list").is_visible()


def test_finger_drag_from_the_drawer_onto_the_board(phone, url, pieces):
    pl = open_phone(phone, url)
    phone.click('.swg-pl-tabs button[data-tab="tile"]')
    phone.fill(".swg-pl-palette input[type=search]", pieces["tile_name"].lower())
    touch_drag(phone, phone.locator(".swg-pl-item .swg-pl-handle").first, pl.cell(2, 2))
    assert pl.state() == [("t", pieces["tile"], 2, 2, 0, False)]


def test_finger_drag_onto_the_drawer_bar_removes(phone, url, pieces):
    pl = open_phone(phone, url, plan(f"t.{pieces['tile']}.2.2.0"))
    assert phone.get_attribute(".swg-pl-drawer-btn", "aria-expanded") == "false"  # closed: there's a board
    assert not phone.locator(".swg-pl-list").is_visible()
    touch_drag(phone, pl.cell(2, 2), phone.locator(".swg-pl-palette"))
    assert pl.state() == []


def test_drawer_steps_aside_while_placing(phone, url, pieces):
    pl = open_phone(phone, url)
    phone.click('.swg-pl-tabs button[data-tab="tile"]')
    phone.fill(".swg-pl-palette input[type=search]", pieces["tile_name"].lower())
    phone.locator(".swg-pl-item").first.click()
    assert not phone.locator(".swg-pl-list").is_visible()
    pl.cell(0, 0).click()
    phone.click("text=Done (Esc)")
    assert phone.locator(".swg-pl-list").is_visible()
    assert pl.state() == [("t", pieces["tile"], 0, 0, 0, False)]


def test_drawer_hides_below_the_planner(phone, url):
    open_phone(phone, url)
    phone.evaluate("scrollTo(0, document.body.scrollHeight)")
    phone.wait_for_timeout(500)
    top = phone.locator(".swg-pl-palette").bounding_box()["y"]
    assert top >= phone.viewport_size["height"]
