from settings import load_settings


def test_env_settings_are_clamped(monkeypatch):
    monkeypatch.setenv("VIANEY_GLOW", "999")
    monkeypatch.setenv("VIANEY_TRAILS", "999")
    monkeypatch.setenv("VIANEY_WARP", "-5")
    monkeypatch.setenv("VIANEY_PARTICLES", "9000")
    monkeypatch.setenv("VIANEY_VOLUME", "-1")
    monkeypatch.setenv("VIANEY_FPS", "999")

    cfg = load_settings()

    assert cfg.glow == 2.5
    assert cfg.trails == 12
    assert cfg.warp == 0.0
    assert cfg.particles == 320
    assert cfg.volume == 0.0
    assert cfg.target_fps == 60


def test_invalid_env_values_fall_back(monkeypatch):
    monkeypatch.setenv("VIANEY_GLOW", "wat")
    monkeypatch.setenv("VIANEY_FPS", "nope")

    cfg = load_settings()

    assert cfg.glow == 1.70
    assert cfg.target_fps == 30
