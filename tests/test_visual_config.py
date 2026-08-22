from visualizer.effects import PRESETS, VisualConfig


def test_invalid_values_are_clamped():
    cfg = VisualConfig(
        preset="does-not-exist",
        glow=99,
        trails=999,
        warp=-5,
        bass_punch=99,
        particles=9999,
        rainbow_speed=-3,
        background_dim=0,
        psychedelic=True,
        star_rain=True,
    ).validated()

    assert cfg.preset == "BlackMamba Trip"
    assert cfg.glow == 2.5
    assert cfg.trails == 12
    assert cfg.warp == 0.0
    assert cfg.bass_punch == 2.5
    assert cfg.particles == 320
    assert cfg.rainbow_speed == 0.0
    assert cfg.background_dim == 0.35


def test_all_presets_roundtrip_to_valid_config():
    for name in PRESETS:
        cfg = VisualConfig.from_preset(name).validated()
        assert cfg.preset == name
        assert 0.0 <= cfg.glow <= 2.5
        assert 0 <= cfg.trails <= 12
        assert 0.0 <= cfg.warp <= 2.5
        assert 0.0 <= cfg.bass_punch <= 2.5
        assert 0 <= cfg.particles <= 320
        assert 0.0 <= cfg.rainbow_speed <= 2.0
        assert 0.35 <= cfg.background_dim <= 1.0
