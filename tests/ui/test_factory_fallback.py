"""Tests for LVGL display/input factory fallback behavior."""

from unittest.mock import MagicMock


def test_display_factory_uses_whisplay_profile_for_simulation(monkeypatch):
    """Simulation should build the Whisplay LVGL adapter and start browser preview."""
    from yoyopod.ui.display.factory import get_display

    fake_server = MagicMock()
    import yoyopod.ui.display.adapters.simulation_web.server as web_server

    monkeypatch.setattr(web_server, "get_server", lambda *args, **kwargs: fake_server)

    display = get_display(hardware="simulation", simulate=False)
    try:
        assert display.DISPLAY_TYPE == "whisplay"
        assert display.SIMULATED_HARDWARE == "whisplay"
        assert display.WIDTH == 240
        assert display.HEIGHT == 280
        assert display.simulate is True
        fake_server.start.assert_called_once()
    finally:
        display.cleanup()


def test_simulate_flag_overrides_hardware_to_whisplay_profile(monkeypatch):
    """The simulate flag should ignore the requested hardware and build simulation."""

    from yoyopod.ui.display.factory import get_display

    fake_server = MagicMock()
    import yoyopod.ui.display.adapters.simulation_web.server as web_server

    monkeypatch.setattr(web_server, "get_server", lambda *args, **kwargs: fake_server)

    display = get_display(hardware="whisplay", simulate=True)
    try:
        assert display.DISPLAY_TYPE == "whisplay"
        assert display.SIMULATED_HARDWARE == "whisplay"
        assert display.simulate is True
    finally:
        display.cleanup()
