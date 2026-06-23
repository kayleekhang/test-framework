import pytest

@pytest.mark.smoke
def test_vehicle_boots(vehicle_system):
    vehicle_system.startup()
    assert vehicle_system.wait_until_healthy()
