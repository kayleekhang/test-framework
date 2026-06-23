import pytest

@pytest.mark.integration
def test_vehicle_nominal_flow(vehicle_system):
    vehicle_system.startup()
    vehicle_system.nominal_mission_flow()
    assert vehicle_system.wait_until_healthy()
