"""Board planner on a desktop browser."""
import re
import struct

from conftest import plan, saved


def test_drag_a_tile_then_a_unit_onto_it(planner, pieces):
    planner.open()
    planner.drag(planner.item("tile", pieces["wide_name"]), planner.cell(1, 1))
    assert planner.state() == [("t", pieces["wide"], 1, 1, 0, False)]
    planner.drag(planner.item("unit", pieces["unit_name"]), planner.cell(1, 1))
    assert ("u", pieces["unit"], 1, 1, 0, False) in planner.state()
    assert planner.p.locator(".swg-pl-legend li").count() == 2


def test_a_unit_needs_a_tile_under_it(planner, pieces):
    planner.open()
    planner.drag(planner.item("unit", pieces["unit_name"]), planner.cell(3, 3))
    assert planner.state() == []
    assert "tile" in planner.msg().lower()


def test_click_to_place_then_rotate(planner, pieces):
    planner.open()
    planner.item("tile", pieces["wide_name"]).click()
    planner.cell(3, 3).click()
    planner.p.keyboard.press("Escape")
    assert planner.state() == [("t", pieces["wide"], 3, 3, 0, False)]
    planner.cell(3, 3).click()
    planner.p.keyboard.press("r")
    assert planner.state()[0][4] == 1


def test_moving_a_tile_carries_the_unit_on_it(planner, pieces):
    w, u = pieces["wide"], pieces["unit"]
    planner.open(plan(f"t.{w}.0.0.0", f"u.{u}.0.0.0"))
    planner.drag(planner.cell(0, 1), planner.cell(4, 4))  # the tile's second square, not the unit
    tile = next(s for s in planner.state() if s[0] == "t")
    unit = next(s for s in planner.state() if s[0] == "u")
    assert (tile[2], tile[3]) == (4, 3)
    assert (unit[2], unit[3]) == (4, 3)


def test_drag_onto_the_list_removes_with_undo(planner, pieces):
    w, u = pieces["wide"], pieces["unit"]
    planner.open(plan(f"t.{w}.0.0.0", f"u.{u}.0.0.0"))
    planner.drag(planner.cell(0, 0), planner.p.locator(".swg-pl-list"))
    assert [s[0] for s in planner.state()] == ["t"]
    assert "Removed" in planner.msg()
    planner.p.click(".swg-pl-left > .swg-pl-msg button:has-text('Undo')")
    assert sorted(s[0] for s in planner.state()) == ["t", "u"]


def test_undo_and_redo_with_keys_and_buttons(planner, pieces):
    t = pieces["tile"]
    planner.open(plan(f"t.{t}.0.0.0"))
    undo, redo = planner.p.locator(".swg-pl-history button").nth(0), planner.p.locator(".swg-pl-history button").nth(1)
    planner.item("tile", pieces["tile_name"]).click()
    planner.cell(5, 5).click()
    planner.p.keyboard.press("Escape")
    assert len(planner.state()) == 2
    planner.p.locator("body").click(position={"x": 5, "y": 5})
    planner.p.keyboard.press("Control+z")
    assert len(planner.state()) == 1 and redo.is_enabled()
    planner.p.keyboard.press("Control+Shift+z")
    assert len(planner.state()) == 2 and not redo.is_enabled()
    undo.click()
    assert len(planner.state()) == 1


def test_clear_board_can_be_undone(planner, pieces):
    planner.open(plan(f"t.{pieces['tile']}.2.2.0", name="Keep"))
    planner.p.click(".swg-pl-actions button:has-text('Clear board')")
    assert planner.state() == []
    planner.p.click(".swg-pl-left > .swg-pl-msg button:has-text('Undo')")
    assert len(planner.state()) == 1
    assert planner.p.input_value("#swg-pl-name") == "Keep"


def test_shared_link_survives_a_reload(planner, pieces):
    planner.open(plan(f"t.{pieces['wide']}.2.1.0", f"u.{pieces['unit']}.2.1.0", name="Shared"))
    before = planner.state()
    planner.p.reload()
    planner.p.wait_for_selector(".swg-pl-cell")
    assert planner.state() == before and planner.p.input_value("#swg-pl-name") == "Shared"


def test_link_pasted_while_the_planner_is_open(planner, pieces):
    planner.open()
    planner.p.evaluate(f"location.hash = {plan(f't.{pieces['tile']}.4.4.0')!r}")
    planner.p.wait_for_timeout(200)
    assert planner.state() == [("t", pieces["tile"], 4, 4, 0, False)]


def test_add_link_puts_the_unit_in_the_tray(planner, pieces):
    planner.open("#add=" + pieces["unit"])
    assert planner.tray().count() == 1
    assert planner.state() == [("u", pieces["unit"], None, None, 0, True)]
    planner.p.locator(".swg-pl-history button").first.click()
    assert planner.tray().count() == 0


def test_tray_pieces_can_be_placed(planner, pieces):
    planner.open(plan(f"t.{pieces['tile']}.-.-.0", f"u.{pieces['unit']}.-.-.0"))
    assert planner.tray().count() == 2
    planner.drag(planner.p.locator(".swg-pl-tray__item", has_text=pieces["tile_name"]), planner.cell(3, 3))
    planner.p.locator(".swg-pl-tray__item", has_text=pieces["unit_name"]).click()
    planner.cell(3, 3).click()
    assert planner.tray().count() == 0
    assert sorted(planner.state()) == sorted([("t", pieces["tile"], 3, 3, 0, False), ("u", pieces["unit"], 3, 3, 0, False)])


def test_saved_boards(planner, pieces):
    planner.open(plan(f"t.{pieces['tile']}.1.1.0", name="Board A"))
    planner.p.click("button:has-text('Save board')")
    assert [s["name"] for s in saved(planner.p)] == ["Board A"]
    planner.p.click(".swg-pl-actions button:has-text('Clear board')")
    planner.p.click(".swg-pl-saves__name:has-text('Board A')")
    assert planner.state() == [("t", pieces["tile"], 1, 1, 0, False)]
    planner.p.click(".swg-pl-saves li:has-text('Board A') .swg-pl-x")
    assert saved(planner.p) == []
    planner.p.click(".swg-pl-savebox .swg-pl-msg button:has-text('Put it back')")
    assert [s["name"] for s in saved(planner.p)] == ["Board A"]


def test_copy_link_says_copied(planner, pieces):
    planner.open(plan(f"t.{pieces['tile']}.1.1.0"))
    btn = planner.p.locator(".swg-pl-actions button", has_text="Copy link")
    btn.click()
    planner.p.wait_for_timeout(100)
    assert "Copied" in planner.p.text_content(".swg-pl-actions button.is-done")
    assert "copied" in planner.p.text_content(".swg-pl-actions__msg").lower()
    clip = planner.p.evaluate("navigator.clipboard.readText()")
    assert "/tools/planner/#plan=" in clip and pieces["tile"] in clip


def test_save_image_downloads_a_png(planner, pieces):
    planner.open(plan(f"t.{pieces['wide']}.2.2.0", f"u.{pieces['unit']}.2.2.0", name="Picture"))
    with planner.p.expect_download() as dl:
        planner.p.click(".swg-pl-actions button:has-text('Save image')")
    data = open(dl.value.path(), "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert width >= 1200 and height >= 600
    assert dl.value.suggested_filename == "picture.png"


def test_open_in_planner_from_a_team_card(page, url):
    import pathlib
    from swg_site.paths import SITE
    with_link = next((p for p in sorted(SITE.rglob("index.html")) if "swg-team__open" in p.read_text()), None)
    if not with_link:
        import pytest
        pytest.skip("no team card with an Open in planner link")
    page.goto(url + with_link.parent.relative_to(SITE).as_posix() + "/")
    page.locator(".swg-team__open a").first.click()
    page.wait_for_selector(".swg-pl-cell")
    assert re.search(r"/tools/planner/", page.url)
    placed = page.locator(".swg-pl-legend li:not(.swg-pl-empty)").count()
    assert page.locator(".swg-pl-tray__item").count() + placed > 0
