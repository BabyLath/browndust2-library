"""swg-new-season, run on copies of the real files."""
import datetime as dt
import re
import shutil

import pytest
import yaml

from swg_site import season
from swg_site.paths import CONTENT, LIB

TODAY = dt.date(2030, 1, 2)


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "content").mkdir()
    (tmp_path / "lib" / "guide").mkdir(parents=True)
    shutil.copy(CONTENT / "seasons.yaml", tmp_path / "content")
    shutil.copy(LIB / "changelog.md", tmp_path / "lib")
    if (LIB / "guide" / "current-season.md").exists():
        shutil.copy(LIB / "guide" / "current-season.md", tmp_path / "lib" / "guide")
    return tmp_path


def run(tree, answers=None, **kw):
    return season.rollover(answers or {}, content=tree / "content", lib=tree / "lib", today=TODAY,
                           validate=False, out=lambda *a: None, **kw)


def test_rolls_over_to_the_next_season(tree):
    old = yaml.safe_load((tree / "content" / "seasons.yaml").read_text())["seasons"]
    assert run(tree) == 0
    text = (tree / "content" / "seasons.yaml").read_text()
    new = yaml.safe_load(text)["seasons"]
    assert len(new) == len(old) + 1
    last, prev = new[-1], new[-2]
    assert last["id"] == season.bump(str(old[-1]["id"]), "-")
    assert prev.get("end") and last["start"] == prev["end"] + dt.timedelta(days=1)
    assert last["expected_end"] > last["start"]
    assert text.startswith("#")  # the explanatory comments at the top survive


def test_archives_the_strategy_page_with_working_links(tree):
    if not (tree / "lib" / "guide" / "current-season.md").exists():
        pytest.skip("no current-season page")
    old_id = yaml.safe_load((tree / "content" / "seasons.yaml").read_text())["seasons"][-1]["id"]
    run(tree)
    page = (tree / "lib" / "archive" / f"{old_id}-strategy.md").read_text()
    assert "<!-- swg:season -->" not in page and "countdown" not in page.lower()
    assert re.search(r"^# .+ strategy$", page, re.M)
    for target in re.findall(r"\]\(([^)\s]+)\)", page):
        if re.match(r"^(\w+:|#|/)", target):
            continue
        path = target.split("#")[0]
        assert (LIB / "archive" / path).resolve().exists(), f"broken link in the archive: {target}"


def test_adds_a_changelog_line_under_todays_date(tree):
    run(tree)
    text = (tree / "lib" / "changelog.md").read_text()
    heading = f"## {season.long_date(TODAY)}"
    assert heading in text
    after = text.split(heading, 1)[1].lstrip("\n").splitlines()[0]
    assert after.startswith("- ") and "started" in after


def test_dry_run_changes_nothing(tree):
    before = (tree / "content" / "seasons.yaml").read_text()
    assert run(tree, dry=True) == 0
    assert (tree / "content" / "seasons.yaml").read_text() == before
    assert not (tree / "lib" / "archive").exists()


def test_refuses_bad_answers(tree):
    seasons = yaml.safe_load((tree / "content" / "seasons.yaml").read_text())["seasons"]
    assert run(tree, {"id": str(seasons[0]["id"])}) == 1                   # id already used
    assert run(tree, {"start": season.as_date(seasons[-1]["start"])}) == 1  # doesn't start after the last one


def test_home_card_says_when_a_season_starts(page, url, cat):
    start = cat.current_season["start"]
    # midday UTC, nine and a half days before the season's first day: "Starts in 10 days"
    page.clock.install(time=dt.datetime(start.year, start.month, start.day, tzinfo=dt.timezone.utc) - dt.timedelta(days=9.5))
    page.goto(url)
    text = page.text_content(".swg-now")
    assert "starts soon" in text and "Starts in 10 days" in text
