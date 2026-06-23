import pytest

@pytest.mark.smoke
def test_vehicle_system_boots(vehicle_system):
    vehicle_system.startup()

    assert vehicle_system.gps.health_check()
    assert vehicle_system.radio.health_check()
    assert vehicle_system.controller.wait_for_state("READY")
