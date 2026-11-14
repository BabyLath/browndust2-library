"""swg-portraits: trims, scales to 128x128, centres, keeps every frame. No browser needed."""
from PIL import Image

from swg_site import portraits as P

UNITS = {"some-unit": {}, "other-unit": {}}


def animated(path, size=(220, 170), box=(50, 5, 110, 165), frames=4):
    """An off-centre figure that grows by a pixel each frame."""
    out = []
    for i in range(frames):
        im = Image.new("RGBA", size, (0, 0, 0, 0))
        im.paste((200, 60, 60, 255), (box[0] - i, box[1], box[2] + i, box[3]))
        out.append(im)
    out[0].save(path, save_all=True, append_images=out[1:], duration=[70, 80, 90, 100][:frames])


def test_fits_an_animation(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(P, "BACKUP", tmp_path / "backup")
    animated(tmp_path / "some-unit.avif")
    assert P.run(tmp_path, tmp_path, units=UNITS) == 0
    frames, durations = P.read_frames(tmp_path / "some-unit.avif")
    assert frames[0].size == (128, 128)
    assert len(frames) == 4 and durations == [70, 80, 90, 100]
    left, top, right, bottom = P.content_box(frames)
    assert top <= 1 and bottom >= 127                 # the longer side fills the square
    assert abs(left - (128 - right)) <= 2              # and it's centred
    assert (tmp_path / "backup" / "some-unit.avif").exists()

    P.run(tmp_path, tmp_path, units=UNITS)             # a second run leaves it alone
    assert "already 128×128" in capsys.readouterr().out


def test_converts_other_formats_and_skips_unknown_ids(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(P, "BACKUP", tmp_path / "backup")
    Image.new("RGBA", (60, 90), (0, 0, 0, 0)).save(tmp_path / "other-unit.png")
    im = Image.new("RGBA", (60, 90), (0, 0, 0, 0))
    im.paste((10, 200, 10, 255), (20, 10, 40, 80))
    im.save(tmp_path / "other-unit.png")
    im.save(tmp_path / "not-a-unit.png")
    assert P.run(tmp_path, tmp_path, units=UNITS) == 1  # the unknown id is the one problem
    assert (tmp_path / "other-unit.avif").exists() and not (tmp_path / "other-unit.png").exists()
    assert (tmp_path / "backup" / "other-unit.png").exists()
    assert "isn't a unit id" in capsys.readouterr().out


def test_dry_run_changes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "BACKUP", tmp_path / "backup")
    animated(tmp_path / "some-unit.avif")
    before = (tmp_path / "some-unit.avif").read_bytes()
    P.run(tmp_path, tmp_path, dry=True, units=UNITS)
    assert (tmp_path / "some-unit.avif").read_bytes() == before
