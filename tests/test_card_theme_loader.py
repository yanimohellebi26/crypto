from __future__ import annotations

from pathlib import Path

from visuals import card_loader


def test_classic_theme_uses_real_deck_path_only(monkeypatch) -> None:
    monkeypatch.setitem(card_loader.THEME_DIRS, "classic", ("real_deck",))
    path = card_loader.card_path(1, theme="classic")
    assert isinstance(path, Path)
    assert "real_deck" in str(path)


def test_classic_theme_availability_detects_real_deck(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(card_loader, "ASSETS_ROOT", tmp_path)
    assert card_loader.classic_theme_available() is False

    (tmp_path / "real_deck").mkdir()
    assert card_loader.classic_theme_available() is True


def test_classic_missing_assets_uses_svg_fallback(monkeypatch, tmp_path) -> None:
    monkeypatch.setitem(card_loader.THEME_DIRS, "classic", ("real_deck",))
    monkeypatch.setattr(card_loader, "ASSETS_ROOT", tmp_path)
    src = card_loader.card_img_src(12, width=90, theme="classic")
    assert src.startswith("data:image/svg+xml;base64,")
