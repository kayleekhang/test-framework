import pytest

@pytest.mark.fault_injection
def test_controller_degrades_when_gps_stops(vehicle_system):
    vehicle_system.startup()
    vehicle_system.gps.stop()
    assert vehicle_system.controller.wait_for_state("DEGRADED")
